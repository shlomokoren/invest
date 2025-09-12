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
app.use(cors());
app.use(express.json({ limit: "2mb" }));

// -------- helpers --------
const explain = (err) => ({
  message: err?.message,
  code: err?.code,
  status: err?.response?.status,
  statusText: err?.response?.statusText,
  data: err?.response?.data,
});

function resolveKeyPath(p) {
  if (!p) return path.resolve(__dirname, "service-account.json"); // default: next to index.js
  if (path.isAbsolute(p)) return p;

  const candidateA = path.resolve(process.cwd(), p); // relative to project root
  if (fs.existsSync(candidateA)) return candidateA;

  const candidateB = path.resolve(__dirname, p); // relative to this file
  if (fs.existsSync(candidateB)) return candidateB;

  return candidateA; // fall-through (will fail later if not found)
}

const rawEnvPath = process.env.GOOGLE_APPLICATION_CREDENTIALS || "";
const keyPath = resolveKeyPath(rawEnvPath);

console.log("cwd =", process.cwd());
console.log(
  "GOOGLE_APPLICATION_CREDENTIALS =",
  rawEnvPath || "(empty, using default)"
);
console.log("Resolved keyPath =", keyPath, "exists =", fs.existsSync(keyPath));

// -------- health + whoami --------
app.get("/api/ping", (req, res) => res.json({ ok: true }));

app.get("/api/whoami", (req, res) => {
  try {
    const raw = fs.readFileSync(keyPath, "utf8");
    const svc = JSON.parse(raw);
    res.json({ client_email: svc.client_email, keyPath, keyFileExists: true });
  } catch (e) {
    res
      .status(500)
      .json({ error: "cannot read key", details: e?.message, keyPath });
  }
});

// -------- Google Drive client --------
const auth = new google.auth.GoogleAuth({
  keyFile: keyPath,
  scopes: ["https://www.googleapis.com/auth/drive"],
});
const drive = google.drive({ version: "v3", auth });

// Peek metadata (debug)
app.get("/api/peek/:fileId", async (req, res) => {
  try {
    const meta = await drive.files.get({
      fileId: req.params.fileId,
      fields: [
        "id",
        "name",
        "mimeType",
        "driveId",
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

// Get JSON content
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

// Save JSON content
// server/index.js  (replace the PUT route)
app.put("/api/file/:fileId", async (req, res) => {
  const { fileId } = req.params;
  const payload = req.body?.json;
  if (typeof payload === "undefined") {
    return res.status(400).json({ error: "Missing 'json' in request body" });
  }

  try {
    // Resolve shortcut & check locks
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

    // ✅ MEDIA-ONLY update (reliable with googleapis)
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
    console.error("Update error:", {
      message: err?.message,
      status: err?.response?.status,
      data: err?.response?.data,
    });
    res.status(err?.response?.status || 500).json({
      error: "Failed to update file",
      details: err?.response?.data || err?.message,
    });
  }
});

// -------- start server (this keeps the process alive) --------
const port = process.env.PORT || 5001;
app.listen(port, () =>
  console.log(`✅ Server running at http://localhost:${port}`)
);
