import { useEffect, useMemo, useRef, useState } from "react";
import axios from "axios";
import Editor from "@monaco-editor/react";

// Put your Drive fileId in VITE_FILE_ID (client/.env.local) or hardcode below
const FILE_ID = import.meta.env.VITE_FILE_ID ?? "YOUR_FILE_ID_HERE";

export default function App() {
  const [raw, setRaw] = useState("{ }");
  const [status, setStatus] = useState("idle"); // idle | loading | ready | saving | saved | error
  const [error, setError] = useState("");
  const [loadedOnce, setLoadedOnce] = useState(false); // avoid autosave during initial load
  const [lastSavedRaw, setLastSavedRaw] = useState("{ }"); // to know if there are unsaved changes
  const saveTimer = useRef(null);

  // Load JSON from backend
  useEffect(() => {
    (async () => {
      setStatus("loading");
      try {
        const res = await axios.get(`/api/file/${FILE_ID}`);
        const text =
          typeof res.data === "string"
            ? res.data
            : JSON.stringify(res.data, null, 2);
        setRaw(text);
        setLastSavedRaw(text);
        setLoadedOnce(true);
        setStatus("ready");
      } catch (e) {
        console.error(e);
        setError("Failed to load file");
        setStatus("error");
      }
    })();
  }, []);

  // Parse JSON (shows errors live)
  const parsed = useMemo(() => {
    try {
      setError("");
      return JSON.parse(raw);
    } catch (e) {
      setError(e.message);
      return null;
    }
  }, [raw]);

  const hasUnsavedChanges = raw !== lastSavedRaw;

  // Manual save (keeps the Save button behavior)
  const save = async () => {
    if (!parsed) return; // don't save invalid JSON
    try {
      setStatus("saving");
      await axios.put(
        `/api/file/${FILE_ID}`,
        { json: parsed },
        {
          headers: { "Content-Type": "application/json" },
        }
      );
      setLastSavedRaw(JSON.stringify(parsed, null, 2));
      setStatus("saved");
      setTimeout(() => setStatus("ready"), 600);
    } catch (e) {
      console.error(e);
      setError("Failed to save");
      setStatus("error");
    }
  };

  // ✅ Autosave with debounce (fires 1s after user stops typing)
  useEffect(() => {
    // only after first successful load, only if valid JSON, and only if content changed
    if (!loadedOnce || !parsed || !hasUnsavedChanges) return;

    clearTimeout(saveTimer.current);
    saveTimer.current = setTimeout(() => {
      // fire-and-forget save (uses same save() for consistency)
      save();
    }, 1000); // 1s debounce

    return () => clearTimeout(saveTimer.current);
  }, [raw, parsed, loadedOnce, hasUnsavedChanges]); // runs on edits

  return (
    <div
      style={{
        padding: 16,
        maxWidth: 1000,
        margin: "0 auto",
        fontFamily: "sans-serif",
      }}
    >
      <h1>Google Drive JSON Editor</h1>
      <p>
        Status: {status}
        {hasUnsavedChanges && status !== "saving" && status !== "error"
          ? " • unsaved changes"
          : ""}
      </p>
      {error && <p style={{ color: "crimson" }}>Error: {error}</p>}

      <Editor
        height="70vh"
        defaultLanguage="json"
        value={raw}
        onChange={(v) => setRaw(v ?? "")}
        options={{
          minimap: { enabled: false },
          formatOnPaste: true,
          formatOnType: true,
          tabSize: 2,
          scrollBeyondLastLine: false,
        }}
      />

      <div style={{ marginTop: 12, display: "flex", gap: 8 }}>
        <button
          onClick={() =>
            setRaw(JSON.stringify(parsed ?? JSON.parse(raw), null, 2))
          }
          disabled={!raw}
        >
          Pretty format
        </button>
        <button
          onClick={save}
          disabled={!parsed || !hasUnsavedChanges || status === "saving"}
        >
          Save
        </button>
      </div>
    </div>
  );
}
