import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/app/**/*.{ts,tsx}",
    "./src/components/**/*.{ts,tsx}",
    "./src/features/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        neon: {
          cyan: "#22d3ee",
          violet: "#a78bfa",
          pink: "#f472b6",
          green: "#34d399",
          amber: "#fbbf24",
        },
      },
      backgroundImage: {
        "dashboard-mesh":
          "radial-gradient(ellipse 70% 50% at 15% 0%, rgba(34,211,238,0.06), transparent 50%), radial-gradient(ellipse 60% 40% at 85% 5%, rgba(167,139,250,0.06), transparent 45%)",
      },
    },
  },
  plugins: [],
};

export default config;
