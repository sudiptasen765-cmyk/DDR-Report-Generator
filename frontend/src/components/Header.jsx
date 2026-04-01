// src/components/Header.jsx
export default function Header({ theme, onToggleTheme }) {
  return (
    <header className="header">
      <div className="header-inner">

        {/* Brand */}
        <a className="header-brand" href="/" style={{ textDecoration: "none" }}>
          <div className="brand-icon">🏗️</div>
          <div className="brand-text">
            <span className="brand-name">UrbanRoof</span>
            <span className="brand-sub">Building Diagnostics &amp; Inspection</span>
          </div>
        </a>

        {/* Right side */}
        <div className="header-right">
          <span className="header-badge">Diagnostic System</span>

          {/* Dark / Light Toggle */}
          <button
            className="theme-toggle"
            onClick={onToggleTheme}
            title={theme === "light" ? "Switch to dark mode" : "Switch to light mode"}
            aria-label="Toggle theme"
          >
            <div className="toggle-knob">
              {theme === "light" ? "☀️" : "🌙"}
            </div>
          </button>
        </div>

      </div>
    </header>
  );
}