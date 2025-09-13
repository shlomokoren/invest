// server/index.js
import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import { google } from "googleapis";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(cors()); // you can restrict origins later if you want
app.use(express.json({ limit: "10mb" }));

// ──────────────────────────────────────────────────────────────
// Health routes FIRST (so startup never fails due to auth issues)
app.get("/api/ping", (_req, res) => res.json({ ok: true }));
app.get("/", (_req, res) => res.send("OK"));
// ──────────────────────────────────────────────────────────────

// Resolve local key path (for dev)
function resolveKeyPath(p) {
  if (!p) return path.resolve(__dirname, "service-account.json"); // default: next to index.js
  if (path.isAbsolute(p)) return p;

  const candidateA = path.resolve(process.cwd(), p); // relative to project root
  if (fs.existsSync(candidateA)) return candidateA;

  const candidateB = path.resolve(__dirname, p); // relative to this file
  if (fs.existsSync(candidateB)) return candidateB;

  return candidateA; // fall-through (may not exist)
}

const rawEnvPath = process.env.GOOGLE_APPLICATION_CREDENTIALS || "";
const keyPath = resolveKeyPath(rawEnvPath);

// Prefer GOOGLE_SERVICE_ACCOUNT_JSON in cloud (Render)
let svcJson = null;
if (process.env.GOOGLE_SERVICE_ACCOUNT_JSON) {
  try {
    svcJson = JSON.parse(process.env.GOOGLE_SERVICE_ACCOUNT_JSON);
  } catch (e) {
    console.error(
      "❌ Failed to JSON.parse GOOGLE_SERVICE_ACCOUNT_JSON:",
      e.message
    );
    // keep svcJson = null; Drive calls will fail later but server stays up
  }
}

console.log("PORT =", process.env.PORT || 5001);
console.log(
  "Using env creds =",
  !!svcJson,
  "| keyPath exists =",
  fs.existsSync(keyPath)
);

// Simple whoami to verify which credentials are in use
app.get("/api/whoami", (_req, res) => {
  try {
    if (svcJson) {
      return res.json({
        source: "env",
        client_email: svcJson.client_email,
        keyPresent: true,
      });
    }
    const raw = fs.readFileSync(keyPath, "utf8");
    const svc = JSON.parse(raw);
    return res.json({
      source: "file",
      client_email: svc.client_email,
      keyPath,
      keyPresent: true,
    });
  } catch (e) {
    return res.status(500).json({
      error: "cannot read service account",
      details: e?.message,
      keyPath,
      usingEnvCreds: !!svcJson,
    });
  }
});

// Build Google Drive client (env creds preferred; file for local dev)
const auth = new google.auth.GoogleAuth({
  credentials: svcJson || undefined,
  keyFile: svcJson ? undefined : keyPath,
  scopes: ["https://www.googleapis.com/auth/drive"],
});
const drive = google.drive({ version: "v3", auth });

// Helper for concise error logs
const explain = (err) => ({
  message: err?.message,
  code: err?.code,
  status: err?.response?.status,
  statusText: err?.response?.statusText,
  data: err?.response?.data,
});

// Peek metadata (checks permissions, mimeType, shortcut, etc.)
app.get("/api/peek/:fileId", async (req, res) => {
  try {
    const meta = await drive.files.get({
      fileId: req.params.fileId,
      fields: [
        "id",
        "name",
        "mimeType",
        "driveId",
        "shortcutDetails",
        "capabilities(canEdit,canModifyContent,canComment)",
        "permissions(kind,id,emailAddress,role,displayName)",
        "contentRestrictions(readOnly,reason)",
      ].join(","),
      supportsAllDrives: true,
    });
    res.json(meta.data);
  } catch (err) {
    console.error("Peek error:", explain(err));
    res.status(500).json({ error: "peek failed" });
  }
});

// GET file content (resolves shortcuts; streams JSON)
app.get("/api/file/:fileId", async (req, res) => {
  const { fileId } = req.params;
  try {
    const meta = await drive.files.get({
      fileId,
      fields: "id,name,mimeType,shortcutDetails",
      supportsAllDrives: true,
    });
    const realId =
      meta.data.mimeType === "application/vnd.google-apps.shortcut"
        ? meta.data.shortcutDetails?.targetId
        : fileId;

    const response = await drive.files.get(
      { fileId: realId, alt: "media", supportsAllDrives: true },
      { responseType: "stream" }
    );

    let data = "";
    response.data.on("data", (chunk) => (data += chunk));
    response.data.on("end", () => res.type("application/json").send(data));
    response.data.on("error", (err) => {
      console.error("Stream error:", err);
      res.status(500).json({ error: "Failed reading file stream" });
    });
  } catch (err) {
    console.error("Fetch error:", explain(err));
    res.status(500).json({ error: "Failed to fetch file" });
  }
});

// PUT file content (media-only update, resolves shortcuts, checks locks/permissions)
app.put("/api/file/:fileId", async (req, res) => {
  const { fileId } = req.params;
  const payload = req.body?.json;
  if (typeof payload === "undefined") {
    return res.status(400).json({ error: "Missing 'json' in request body" });
  }

  try {
    const meta = await drive.files.get({
      fileId,
      fields:
        "id,name,mimeType,shortcutDetails,capabilities,contentRestrictions",
      supportsAllDrives: true,
    });

    if (meta.data.contentRestrictions?.some((r) => r.readOnly)) {
      return res
        .status(423)
        .json({ error: "File is locked (contentRestrictions.readOnly=true)" });
    }
    if (
      meta.data.capabilities &&
      meta.data.capabilities.canModifyContent === false
    ) {
      return res
        .status(403)
        .json({ error: "Service account cannot modify content (permission)." });
    }

    const realId =
      meta.data.mimeType === "application/vnd.google-apps.shortcut"
        ? meta.data.shortcutDetails?.targetId
        : fileId;

    // MEDIA-ONLY update (reliable with googleapis)
    await drive.files.update({
      fileId: realId,
      supportsAllDrives: true,
      uploadType: "media",
      media: {
        mimeType: "application/json",
        body: Buffer.from(JSON.stringify(payload, null, 2)),
      },
    });

    res.json({ ok: true });
  } catch (err) {
    const details = explain(err);
    console.error("Update error:", details);
    res.status(details.status || 500).json({
      error: "Failed to update file",
      details: details.data || details.message,
    });
  }
});

// Start server
const port = process.env.PORT || 5001;
app.listen(port, () =>
  console.log(`✅ Server running at http://localhost:${port}`)
);
