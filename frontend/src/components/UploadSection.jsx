// src/components/UploadSection.jsx
import { useRef, useState } from "react";

function DropZone({ label, icon, file, onFileChange, id }) {
  const inputRef     = useRef();
  const [drag, setDrag] = useState(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setDrag(false);
    const f = e.dataTransfer.files?.[0];
    if (f && f.name.endsWith(".pdf")) onFileChange(f);
  };

  return (
    <div
      className={`drop-zone ${file ? "filled" : ""} ${drag ? "dragging" : ""}`}
      onClick={() => inputRef.current.click()}
      onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
      onDragLeave={() => setDrag(false)}
      onDrop={handleDrop}
    >
      <input
        ref={inputRef}
        id={id}
        type="file"
        accept=".pdf"
        onChange={(e) => onFileChange(e.target.files?.[0] || null)}
        onClick={(e) => e.stopPropagation()}
      />
      <div className="dz-icon">{file ? "✅" : icon}</div>
      <div className="dz-label">{label}</div>
      {file ? (
        <div className="dz-filename">📎 {file.name}</div>
      ) : (
        <div className="dz-hint">Click or drag &amp; drop PDF</div>
      )}
    </div>
  );
}

export default function UploadSection({
  inspectionFile, thermalFile,
  onInspectionChange, onThermalChange,
  onGenerate, errorMsg,
}) {
  const bothSelected = inspectionFile && thermalFile;

  return (
    <div className="upload-page">

      {/* Hero heading */}
      <div className="upload-hero">
        <div className="upload-hero-icon">📋</div>
        <h1>Detailed Diagnostic Report</h1>
        <p>
          Upload the Inspection Report and Thermal Report to generate
          a comprehensive diagnostic document.
        </p>
      </div>

      {/* Upload card */}
      <div className="upload-card">

        {/* How it works */}
        <div style={{ display: "flex", gap: "10px", marginBottom: "28px", flexWrap: "wrap" }}>
          {[
            { icon: "📤", label: "Upload PDFs" },
            { icon: "⚙️", label: "Process Reports" },
            { icon: "📄", label: "Download DDR" },
          ].map((step, i) => (
            <div key={i} style={{
              flex: 1, minWidth: "100px",
              display: "flex", flexDirection: "column", alignItems: "center",
              gap: "6px", padding: "14px 10px",
              background: "var(--bg-surface-2)",
              borderRadius: "var(--radius-md)",
              border: "1px solid var(--border)",
              textAlign: "center",
            }}>
              <span style={{ fontSize: "20px" }}>{step.icon}</span>
              <span style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.5px" }}>
                Step {i + 1}
              </span>
              <span style={{ fontSize: "0.82rem", color: "var(--text-primary)", fontWeight: 600 }}>
                {step.label}
              </span>
            </div>
          ))}
        </div>

        <div className="divider" />

        {/* Drop zones */}
        <div className="upload-grid">
          <DropZone
            id="inspection-input"
            label="Inspection Report"
            icon="📄"
            file={inspectionFile}
            onFileChange={onInspectionChange}
          />
          <DropZone
            id="thermal-input"
            label="Thermal Report"
            icon="🌡️"
            file={thermalFile}
            onFileChange={onThermalChange}
          />
        </div>

        {/* Requirements note */}
        <div style={{
          background: "var(--bg-surface-2)",
          border: "1px solid var(--border)",
          borderRadius: "var(--radius-sm)",
          padding: "10px 14px",
          marginBottom: "20px",
          display: "flex",
          alignItems: "center",
          gap: "8px",
          fontSize: "0.8rem",
          color: "var(--text-muted)",
        }}>
          <span>ℹ️</span>
          <span>Both files must be in <strong style={{ color: "var(--text-secondary)" }}>PDF format</strong>. Maximum recommended size: 10 MB per file.</span>
        </div>

        {/* Error */}
        {errorMsg && (
          <div className="error-box">
            <span>⚠️</span>
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Generate button */}
        <button
          className="btn-generate"
          onClick={onGenerate}
          disabled={!bothSelected}
          style={{ opacity: bothSelected ? 1 : 0.55 }}
        >
          <span>Generate Diagnostic Report</span>
          <span>→</span>
        </button>

        <p className="upload-note">
          <span>🔒</span>
          <span>Files are processed locally and not stored on external servers.</span>
        </p>
      </div>
    </div>
  );
}