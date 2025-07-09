import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    host: "0.0.0.0",
    port: 3000,
    allowedHosts: ["bastet", "localhost", "127.0.0.1", ".local"],
  },
});
