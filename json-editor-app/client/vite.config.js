import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  // 👇 Pages URL will be /invest/json-editor/
  base: "/invest/json-editor/",
  plugins: [react()],
  // 👇 Build into a subfolder so Pages serves /json-editor/index.html
  build: { outDir: "dist/json-editor" },
  server: {
    port: 5173,
    proxy: { "/api": { target: "http://localhost:5001", changeOrigin: true } },
  },
});
