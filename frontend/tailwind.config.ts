import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#050508",
        panel: "#0b0b10",
        crimson: "#ff2b3d",
        ember: "#ff5361",
        smoke: "#a5a5b0",
        signal: "#37e3a4",
        amber: "#ffc857",
      },
      boxShadow: {
        glow: "0 0 35px rgba(255, 43, 61, 0.2)",
        innerglow: "inset 0 0 30px rgba(255, 43, 61, 0.08)",
      },
    },
  },
  plugins: [],
};

export default config;
