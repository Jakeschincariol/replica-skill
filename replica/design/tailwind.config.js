/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        bg: "var(--color-bg)",
        surface: "var(--color-surface)",
        "surface-raised": "var(--color-surface-raised)",
        border: "var(--color-border)",
        "border-input": "var(--color-border-input)",
        text: "var(--color-text)",
        muted: "var(--color-text-muted)",
        accent: "var(--color-accent)",
        "on-accent": "var(--color-on-accent)",
        "accent-action": "var(--color-accent-action)",
        "on-accent-action": "var(--color-on-accent-action)",
        danger: "var(--color-danger)",
        "on-danger": "var(--color-on-danger)",
        success: "var(--color-success)",
        "on-success": "var(--color-on-success)",
        warning: "var(--color-warning)",
        "on-warning": "var(--color-on-warning)",
        focus: "var(--color-focus)",
        interactive: "var(--color-interactive)",
      },
      fontFamily: {
        sans: ["var(--font-sans)"],
        mono: ["var(--font-mono)"],
      },
      fontSize: {
        xs: ["var(--font-size-xs)", "var(--line-height-xs)"],
        sm: ["var(--font-size-sm)", "var(--line-height-sm)"],
        base: ["var(--font-size-base)", "var(--line-height-base)"],
        lg: ["var(--font-size-lg)", "var(--line-height-lg)"],
        xl: ["var(--font-size-xl)", "var(--line-height-xl)"],
        display: ["var(--font-size-display)", "var(--line-height-display)"],
      },
      spacing: {
        0: "var(--space-0)",
        1: "var(--space-1)",
        2: "var(--space-2)",
        3: "var(--space-3)",
        4: "var(--space-4)",
        6: "var(--space-6)",
        8: "var(--space-8)",
        12: "var(--space-12)",
        16: "var(--space-16)",
      },
      borderRadius: {
        sm: "var(--radius-sm)",
        md: "var(--radius-md)",
        lg: "var(--radius-lg)",
        pill: "var(--radius-pill)",
      },
      boxShadow: {
        card: "var(--shadow-card)",
        pop: "var(--shadow-pop)",
      },
      transitionDuration: {
        fast: "var(--motion-fast)",
        base: "var(--motion-base)",
      },
      maxWidth: {
        content: "var(--layout-content-max)",
      },
      width: {
        sidebar: "var(--layout-sidebar-width)",
      },
      height: {
        header: "var(--layout-header-height)",
      },
    },
  },
  plugins: [],
};
