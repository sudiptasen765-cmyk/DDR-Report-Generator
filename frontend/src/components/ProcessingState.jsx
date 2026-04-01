// src/components/ProcessingState.jsx
import { useState, useEffect } from "react";

const STEPS = [
  { label: "Reading inspection report...",         duration: 4000  },
  { label: "Reading thermal report...",            duration: 4000  },
  { label: "Analysing structural observations...", duration: 8000  },
  { label: "Evaluating thermal data...",           duration: 8000  },
  { label: "Generating diagnostic report...",      duration: 99999 }, // stays until done
];

export default function ProcessingState() {
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    let elapsed = 0;
    const timers = [];
    for (let i = 0; i < STEPS.length - 1; i++) {
      elapsed += STEPS[i].duration;
      const t = setTimeout(() => setActiveStep(i + 1), elapsed);
      timers.push(t);
    }
    return () => timers.forEach(clearTimeout);
  }, []);

  return (
    <div className="processing-wrap">
      <div className="processing-card">

        <div className="processing-spinner" />

        <h2 style={{
          fontFamily: "'DM Serif Display', serif",
          fontSize: "1.35rem",
          color: "var(--text-primary)",
          marginBottom: "6px",
        }}>
          Processing Reports
        </h2>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.88rem" }}>
          Please wait while we analyse the uploaded documents.
          This may take up to 60 seconds.
        </p>

        <div className="processing-steps">
          {STEPS.map((step, i) => {
            const state = i < activeStep ? "done" : i === activeStep ? "active" : "waiting";
            return (
              <div key={i} className={`proc-step ${state}`}>
                <div className="step-dot" />
                <span>
                  {state === "done" ? "✓ " : ""}{step.label}
                </span>
              </div>
            );
          })}
        </div>

      </div>

      <p style={{
        fontSize: "0.78rem",
        color: "var(--text-muted)",
        textAlign: "center",
        maxWidth: "380px",
      }}>
        Do not close this window. The report will appear automatically once processing is complete.
      </p>
    </div>
  );
}