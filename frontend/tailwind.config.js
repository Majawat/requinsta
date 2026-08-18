export default {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Public Sans"', "ui-sans-serif", "system-ui", "-apple-system", '"Segoe UI"', "Roboto", "sans-serif"],
        mono: ['"JetBrains Mono"', "ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      boxShadow: {
        // Bottom-sheet lift (design frame D)
        sheet: "0 -20px 50px rgba(0,0,0,.55)",
        toast: "0 8px 24px rgba(0,0,0,.4)",
      },
      // Full type-badge / status color families come from stock slate/indigo/
      // amber/sky/emerald/rose/orange — no custom palette needed.
    },
  },
  // Safelist the status utility classes so the JIT keeps them even though they
  // are only referenced via data maps in requestUtils.js (not literal in markup).
  safelist: [
    { pattern: /^(bg|text|ring|border)-(amber|sky|emerald|rose|orange|indigo|slate)-(200|300|400|500|600)(\/\d{1,3})?$/ },
  ],
  plugins: [],
};
