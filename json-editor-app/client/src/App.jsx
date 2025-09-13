import { useEffect, useMemo, useRef, useState } from "react";
import axios from "axios";
import Editor from "@monaco-editor/react";

const API = import.meta.env.VITE_API_BASE || "";
const FILE_ID = import.meta.env.VITE_FILE_ID ?? "YOUR_FILE_ID_HERE";

// detect small screens to pick a comfy default
const isMobile =
  typeof window !== "undefined" &&
  window.matchMedia("(max-width: 640px)").matches;
const stored =
  typeof window !== "undefined"
    ? Number(localStorage.getItem("editor.fontSize"))
    : NaN;
const DEFAULT_FONT_SIZE = Number.isFinite(stored) ? stored : isMobile ? 18 : 14;

export default function App() {
  const [raw, setRaw] = useState("{ }");
  const [status, setStatus] = useState("idle"); // idle | loading | ready | saving | saved | error
  const [error, setError] = useState("");
  const [loadedOnce, setLoadedOnce] = useState(false);
  const [lastSavedRaw, setLastSavedRaw] = useState("{ }");
  const [fontSize, setFontSize] = useState(DEFAULT_FONT_SIZE);
  const [wrap, setWrap] = useState(true);

  const saveTimer = useRef(null);

  // persist font size preference
  useEffect(() => {
    try {
      localStorage.setItem("editor.fontSize", String(fontSize));
    } catch {}
  }, [fontSize]);

  // load JSON
  useEffect(() => {
    (async () => {
      setStatus("loading");
      try {
        const res = await axios.get(`${API}/api/file/${FILE_ID}`);
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

  // live JSON syntax check
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

  const save = async () => {
    if (!parsed) return;
    try {
      setStatus("saving");
      await axios.put(
        `${API}/api/file/${FILE_ID}`,
        { json: parsed },
        { headers: { "Content-Type": "application/json" } }
      );
      const pretty = JSON.stringify(parsed, null, 2);
      setLastSavedRaw(pretty);
      setRaw(pretty);
      setStatus("saved");
      setTimeout(() => setStatus("ready"), 600);
    } catch (e) {
      console.error(e);
      setError("Failed to save");
      setStatus("error");
    }
  };

  // autosave with debounce
  useEffect(() => {
    if (!loadedOnce || !parsed || !hasUnsavedChanges) return;
    clearTimeout(saveTimer.current);
    saveTimer.current = setTimeout(() => {
      void save();
    }, 1000);
    return () => clearTimeout(saveTimer.current);
  }, [raw, parsed, loadedOnce, hasUnsavedChanges]);

  // simple UI helpers
  const incFont = () => setFontSize((s) => Math.min(28, s + 2));
  const decFont = () => setFontSize((s) => Math.max(12, s - 2));
  const resetFont = () => setFontSize(isMobile ? 18 : 14);

  return (
    <div
      style={{
        padding: 12,
        maxWidth: 1000,
        margin: "0 auto",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <h1 style={{ fontSize: 22, margin: "8px 0" }}>
        Google Drive JSON Editor
      </h1>

      <div
        style={{
          display: "flex",
          gap: 8,
          alignItems: "center",
          flexWrap: "wrap",
        }}
      >
        <span style={{ opacity: 0.8 }}>Status: {status}</span>
        {hasUnsavedChanges && status !== "saving" && status !== "error" && (
          <span style={{ opacity: 0.7 }}>• unsaved changes</span>
        )}
        {error && <span style={{ color: "crimson" }}> • {error}</span>}

        <span style={{ flex: 1 }} />

        {/* font controls */}
        <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
          <button onClick={decFont} aria-label="Smaller font">
            A−
          </button>
          <span style={{ minWidth: 28, textAlign: "center" }}>{fontSize}</span>
          <button onClick={incFont} aria-label="Larger font">
            A+
          </button>
          <button onClick={resetFont} title="Reset font size">
            Reset
          </button>
        </div>

        {/* wrap toggle */}
        <label style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <input
            type="checkbox"
            checked={wrap}
            onChange={(e) => setWrap(e.target.checked)}
          />
          Wrap
        </label>
      </div>

      <Editor
        height={isMobile ? "60vh" : "70vh"}
        defaultLanguage="json"
        value={raw}
        onChange={(v) => setRaw(v ?? "")}
        options={{
          automaticLayout: true,
          fontSize,
          lineHeight: Math.round(fontSize * 1.6),
          wordWrap: wrap ? "on" : "off",
          wrappingIndent: "same",
          minimap: { enabled: false },
          padding: { top: 8, bottom: 8 },
          scrollBeyondLastLine: false,
          smoothScrolling: true,
          cursorBlinking: "smooth",
        }}
      />

      <div style={{ marginTop: 10, display: "flex", gap: 8 }}>
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
