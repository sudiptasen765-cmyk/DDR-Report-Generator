# backend/report_builder.py
import os
import re


def build_html_report(ddr: dict, inspection_data: dict, thermal_data: dict, output_path: str):
    """
    UrbanRoof DDR HTML Report Builder — v4 Final.
    Handles: deduplicated images, precise area names,
    corrected severity colours, confident language rendering.
    """

    # ── Meta ──────────────────────────────────────────────────────────────────
    insp_pages  = inspection_data.get("page_count", "N/A")
    therm_pages = thermal_data.get("page_count",    "N/A")
    total_imgs  = (len(inspection_data.get("images", [])) +
                   len(thermal_data.get("images",    [])))
    areas_count = len(ddr.get("area_wise_analysis", []))
    report_date = ddr.get("report_date", "N/A")

    # All extracted image paths for src resolution
    all_image_paths = (inspection_data.get("images", []) +
                       thermal_data.get("images",    []))

    # ── Severity map ──────────────────────────────────────────────────────────
    SEV = {
        "High":   {"bg": "#fff1f1", "border": "#ef4444", "badge": "#ef4444", "icon": "🔴"},
        "Medium": {"bg": "#fffbeb", "border": "#f59e0b", "badge": "#f59e0b", "icon": "🟡"},
        "Low":    {"bg": "#f0fdf4", "border": "#22c55e", "badge": "#22c55e", "icon": "🟢"},
    }
    SEV_DEFAULT = {"bg": "#f8fafc", "border": "#94a3b8", "badge": "#94a3b8", "icon": "⚪"}

    # ── Urgency map ───────────────────────────────────────────────────────────
    def urgency_style(u):
        u = u.lower()
        if any(x in u for x in ["24", "48", "immediate"]):
            return {"bg": "#fef2f2", "color": "#dc2626", "border": "#fca5a5"}
        if "1 week" in u:
            return {"bg": "#fffbeb", "color": "#d97706", "border": "#fde68a"}
        return {"bg": "#eff6ff", "color": "#2563eb", "border": "#bfdbfe"}

    # ── Delta-T highlighter ───────────────────────────────────────────────────
    def highlight_delta(text):
        return re.sub(
            r"(Delta-T|ΔT|delta-T)[^\.]{0,40}?(°C|deg C|degrees C)",
            lambda m: f'<span class="delta-t">{m.group(0)}</span>',
            text
        )

    # ── Risk level colour ─────────────────────────────────────────────────────
    RISK_COLORS = {
        "Low":      "#16a34a",
        "Medium":   "#d97706",
        "High":     "#dc2626",
        "Critical": "#7c3aed",
    }

    # ══════════════════════════════════════════════════════════════════════════
    # 🚨  IMMEDIATE ACTIONS
    # ══════════════════════════════════════════════════════════════════════════
    imm_html = ""
    for item in ddr.get("immediate_actions", []):
        action  = item.get("action",  "Not Available")
        urgency = item.get("urgency", "N/A")
        us      = urgency_style(urgency)
        imm_html += f"""
      <div class="imm-card"
           style="background:{us['bg']};border:1px solid {us['border']};border-left:4px solid {us['color']}">
        <div class="imm-row">
          <span class="imm-text">⚡ {action}</span>
          <span class="urgency-pill" style="background:{us['color']}">⏱ {urgency}</span>
        </div>
      </div>"""
    if not imm_html:
        imm_html = '<p class="na">No immediate actions identified.</p>'

    # ══════════════════════════════════════════════════════════════════════════
    # 1.  PROPERTY ISSUE SUMMARY
    # ══════════════════════════════════════════════════════════════════════════
    summary_html = "".join(
        f"<li>{pt}</li>" for pt in ddr.get("property_issue_summary", ["Not Available"])
    )

    # ══════════════════════════════════════════════════════════════════════════
    # 2.  ISSUE IMPACT SUMMARY
    # ══════════════════════════════════════════════════════════════════════════
    iis       = ddr.get("issue_impact_summary", {})
    risk_lvl  = iis.get("risk_level", "N/A")
    risk_col  = RISK_COLORS.get(risk_lvl, "#64748b")

    impact_html = f"""
    <div class="impact-grid">
      <div class="impact-cell">
        <span class="impact-lbl">Total Areas Affected</span>
        <span class="impact-val">{iis.get("total_areas_affected", "N/A")}</span>
      </div>
      <div class="impact-cell">
        <span class="impact-lbl">Primary Issue Type</span>
        <span class="impact-val">{iis.get("primary_issue_type", "N/A")}</span>
      </div>
      <div class="impact-cell">
        <span class="impact-lbl">Risk Level</span>
        <span class="impact-val" style="color:{risk_col};font-weight:800">{risk_lvl}</span>
      </div>
      <div class="impact-cell">
        <span class="impact-lbl">Spread</span>
        <span class="impact-val">{iis.get("spread", "N/A")}</span>
      </div>
    </div>"""

    # ══════════════════════════════════════════════════════════════════════════
    # 3.  AREA-WISE ANALYSIS
    # ══════════════════════════════════════════════════════════════════════════
    # Build a lookup: filename → full path
    img_lookup = {os.path.basename(p): p for p in all_image_paths}

    area_html = ""
    for area in ddr.get("area_wise_analysis", []):
        sev    = area.get("severity", "N/A")
        colors = SEV.get(sev, SEV_DEFAULT)

        issues = "".join(
            f"<li>{i}</li>" for i in area.get("observed_issues", ["Not Available"])
        )

        thermal      = highlight_delta(area.get("thermal_evidence", "Not Available"))
        risk_untreated = area.get("risk_if_untreated", "Not Available")

        # ── Image rendering (deduplicated by ai_processor, rendered here) ──
        images_raw = area.get("images", "")
        if images_raw and images_raw.strip().lower() not in ("not available", "n/a", ""):
            names     = [x.strip() for x in images_raw.replace(";", ",").split(",") if x.strip()]
            imgs_html = ""
            for name in names[:2]:          # safety cap — never more than 2
                path = img_lookup.get(name)
                if path:
                    imgs_html += f"""
                    <div class="img-wrap">
                      <img src="{path}" class="area-img" alt="{name}"
                           onerror="this.parentElement.innerHTML='<span class=\\'img-ref\\'>📎 {name}</span>'"/>
                      <span class="img-cap">{name}</span>
                    </div>"""
                else:
                    imgs_html += f'<span class="img-ref">📎 {name}</span>'
            img_block = f'<div class="img-row">{imgs_html}</div>'
        else:
            img_block = '<p class="na">Image Not Available</p>'

        area_html += f"""
      <div class="area-card"
           style="border-left:5px solid {colors['border']};background:{colors['bg']}">

        <div class="area-header">
          <h3 class="area-name">📍 {area.get("area_name", "Unknown Area")}</h3>
          <span class="sev-badge"
                style="background:{colors['badge']}">{colors['icon']} {sev} Severity</span>
        </div>

        <div class="area-cols">
          <div class="area-col">
            <p class="field-lbl">🔍 Observed Issues</p>
            <ul class="obs-list">{issues}</ul>
          </div>
          <div class="area-col thermal-col">
            <p class="field-lbl">🌡️ Thermal Evidence</p>
            <p class="thermal-text">{thermal}</p>
          </div>
        </div>

        <div class="risk-row">
          <span class="field-lbl">⚠️ Risk if Untreated: </span>{risk_untreated}
        </div>

        <div>
          <p class="field-lbl">🖼️ Reference Images</p>
          {img_block}
        </div>

      </div>"""

    if not area_html:
        area_html = '<p class="na">No area analysis available.</p>'

    # ══════════════════════════════════════════════════════════════════════════
    # 5.  PRIORITY MATRIX
    # ══════════════════════════════════════════════════════════════════════════
    def pri_list(items, icon):
        if not items:
            return '<li class="na">None identified</li>'
        return "".join(f"<li>{icon} {i}</li>" for i in items)

    pm      = ddr.get("priority_matrix", {})
    high_li = pri_list(pm.get("high",   []), "🔴")
    med_li  = pri_list(pm.get("medium", []), "🟡")
    low_li  = pri_list(pm.get("low",    []), "🟢")

    # ══════════════════════════════════════════════════════════════════════════
    # 6.  ACTION PLAN
    # ══════════════════════════════════════════════════════════════════════════
    action_html = ""
    for i, step in enumerate(ddr.get("recommended_action_plan", ["Not Available"]), 1):
        action_html += f"""
      <div class="action-step">
        <div class="step-num">{i}</div>
        <div class="step-text">{step}</div>
      </div>"""

    # ══════════════════════════════════════════════════════════════════════════
    # 8.  MISSING DATA
    # ══════════════════════════════════════════════════════════════════════════
    missing_raw = ddr.get("missing_or_unclear_data", [])
    if isinstance(missing_raw, list):
        missing_html = "<ul class='missing-list'>" + "".join(
            f"<li>{m}</li>" for m in missing_raw
        ) + "</ul>"
    else:
        missing_html = f"<p>{missing_raw}</p>"

    # ══════════════════════════════════════════════════════════════════════════
    # 🏗️  FULL HTML OUTPUT
    # ══════════════════════════════════════════════════════════════════════════
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>UrbanRoof DDR — {report_date}</title>
  <style>
    *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:'Segoe UI',Arial,sans-serif;background:#f0f2f5;color:#1e293b;font-size:15px;line-height:1.7}}

    /* ── Page ── */
    .page{{max-width:980px;margin:36px auto;background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 8px 40px rgba(0,0,0,0.11)}}

    /* ── Hero ── */
    .hero{{background:linear-gradient(135deg,#0d1f3c 0%,#1a3a6b 55%,#1a56db 100%);color:#fff;padding:44px 52px 36px}}
    .hero-top{{display:flex;align-items:center;justify-content:space-between;margin-bottom:22px;flex-wrap:wrap;gap:16px}}
    .logo-wrap{{display:flex;align-items:center;gap:14px}}
    .logo-box{{width:52px;height:52px;background:rgba(255,255,255,0.13);border:2px solid rgba(255,255,255,0.25);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:26px}}
    .co-name{{font-size:1.5rem;font-weight:800;letter-spacing:0.5px}}
    .co-tag{{font-size:0.71rem;opacity:0.62;letter-spacing:0.8px;text-transform:uppercase;margin-top:2px}}
    .rpt-meta{{text-align:right;font-size:0.84rem;opacity:0.75}}
    .rpt-meta strong{{display:block;font-size:1rem;opacity:1;margin-bottom:2px}}
    .hero h1{{font-size:1.8rem;font-weight:800;margin-bottom:5px}}
    .hero-sub{{opacity:0.68;font-size:0.88rem}}

    /* ── Stats bar ── */
    .stats{{display:flex;border-top:1px solid rgba(255,255,255,0.13);margin-top:26px;padding-top:18px;flex-wrap:wrap}}
    .stat{{flex:1;min-width:110px;text-align:center;padding:0 12px;border-right:1px solid rgba(255,255,255,0.13)}}
    .stat:last-child{{border-right:none}}
    .stat-n{{font-size:1.8rem;font-weight:800;display:block}}
    .stat-l{{font-size:0.69rem;opacity:0.58;text-transform:uppercase;letter-spacing:0.5px}}

    /* ── Body ── */
    .body{{padding:42px 52px}}

    /* ── Section ── */
    .section{{margin-bottom:46px}}
    .sec-title{{
      font-size:0.91rem;font-weight:800;color:#0d1f3c;
      text-transform:uppercase;letter-spacing:0.9px;
      margin-bottom:16px;padding-bottom:9px;
      border-bottom:2px solid #e2e8f0;
      display:flex;align-items:center;gap:9px;
    }}
    .sec-num{{background:#0d1f3c;color:#fff;width:24px;height:24px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:0.71rem;font-weight:800;flex-shrink:0}}

    /* ── Immediate actions ── */
    .imm-card{{border-radius:9px;padding:13px 18px;margin-bottom:9px}}
    .imm-row{{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;flex-wrap:wrap}}
    .imm-text{{font-weight:600;line-height:1.5;flex:1;font-size:0.93rem}}
    .urgency-pill{{color:#fff;font-size:0.72rem;font-weight:700;padding:4px 12px;border-radius:16px;white-space:nowrap;flex-shrink:0}}

    /* ── Summary ── */
    .summary-list{{list-style:none;padding:0}}
    .summary-list li{{padding:10px 14px 10px 38px;margin-bottom:8px;background:#f7f9fc;border-radius:8px;border-left:3px solid #1a56db;position:relative;line-height:1.6}}
    .summary-list li::before{{content:"▸";position:absolute;left:14px;color:#1a56db;font-weight:bold}}

    /* ── Impact grid ── */
    .impact-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}
    @media(max-width:640px){{.impact-grid{{grid-template-columns:1fr 1fr}}}}
    .impact-cell{{background:#f7f9fc;border:1px solid #e2e8f0;border-radius:9px;padding:14px 16px}}
    .impact-lbl{{display:block;font-size:0.69rem;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;color:#64748b;margin-bottom:5px}}
    .impact-val{{display:block;font-size:1rem;font-weight:700;color:#0d1f3c}}

    /* ── Area cards ── */
    .area-card{{border-radius:10px;padding:22px 24px;margin-bottom:16px}}
    .area-header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;flex-wrap:wrap;gap:8px}}
    .area-name{{font-size:0.97rem;font-weight:700;color:#0d1f3c}}
    .sev-badge{{color:#fff;font-size:0.71rem;font-weight:700;padding:4px 13px;border-radius:20px;text-transform:uppercase;letter-spacing:0.5px}}
    .area-cols{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:12px}}
    @media(max-width:600px){{.area-cols{{grid-template-columns:1fr}}}}
    .field-lbl{{font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;color:#64748b;margin-bottom:6px;display:block}}
    .obs-list{{padding-left:17px}}
    .obs-list li{{margin-bottom:4px;color:#334155;font-size:0.91rem;line-height:1.55}}
    .thermal-col{{background:rgba(255,255,255,0.55);border-radius:7px;padding:10px 14px}}
    .thermal-text{{color:#1e293b;font-size:0.91rem;line-height:1.65}}
    .delta-t{{background:#fef3c7;color:#92400e;font-weight:700;padding:1px 5px;border-radius:4px;font-size:0.86rem}}
    .risk-row{{font-size:0.9rem;color:#334155;background:rgba(255,255,255,0.45);border-radius:6px;padding:8px 12px;margin-bottom:12px;line-height:1.55}}
    .img-row{{display:flex;gap:10px;flex-wrap:wrap;margin-top:6px}}
    .img-wrap{{display:flex;flex-direction:column;align-items:center;gap:4px}}
    .area-img{{max-width:160px;max-height:120px;border-radius:6px;border:1px solid #e2e8f0;object-fit:cover}}
    .img-cap{{font-size:0.69rem;color:#64748b}}
    .img-ref{{font-size:0.79rem;color:#2563eb;background:#eff6ff;padding:4px 10px;border-radius:6px;border:1px solid #bfdbfe;display:inline-block;margin-top:6px}}

    /* ── Root cause ── */
    .root-box{{background:#fefce8;border:1px solid #fde68a;border-left:4px solid #f59e0b;border-radius:8px;padding:18px 22px;line-height:1.82;color:#1e293b}}

    /* ── Priority matrix ── */
    .pri-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}
    @media(max-width:620px){{.pri-grid{{grid-template-columns:1fr}}}}
    .pri-col{{border-radius:10px;padding:16px 18px}}
    .pri-col.h{{background:#fff1f1;border:1px solid #fca5a5}}
    .pri-col.m{{background:#fffbeb;border:1px solid #fde68a}}
    .pri-col.l{{background:#f0fdf4;border:1px solid #bbf7d0}}
    .pri-head{{font-weight:800;font-size:0.77rem;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:10px}}
    .pri-col.h .pri-head{{color:#dc2626}}
    .pri-col.m .pri-head{{color:#d97706}}
    .pri-col.l .pri-head{{color:#16a34a}}
    .pri-col ul{{list-style:none;padding:0}}
    .pri-col ul li{{font-size:0.86rem;margin-bottom:7px;line-height:1.5;color:#334155}}

    /* ── Action steps ── */
    .action-step{{display:flex;gap:14px;align-items:flex-start;margin-bottom:10px;padding:13px 18px;background:#f7f9fc;border-radius:8px}}
    .step-num{{background:#0d1f3c;color:#fff;width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:0.81rem;flex-shrink:0}}
    .step-text{{padding-top:4px;color:#1e293b;line-height:1.6;font-size:0.91rem}}

    /* ── Insights ── */
    .insight-box{{background:#eff6ff;border:1px solid #bfdbfe;border-left:4px solid #3b82f6;border-radius:8px;padding:18px 22px;line-height:1.82}}

    /* ── Missing data ── */
    .missing-wrap{{background:#fff7ed;border:1px solid #fed7aa;border-left:4px solid #f97316;border-radius:8px;padding:18px 22px}}
    .missing-list{{padding-left:20px;line-height:1.9}}
    .missing-list li{{color:#475569;font-size:0.9rem;margin-bottom:4px}}

    /* ── Footer ── */
    .footer{{background:#0d1f3c;color:rgba(255,255,255,0.44);text-align:center;padding:18px 52px;font-size:0.76rem;letter-spacing:0.3px}}
    .footer strong{{color:rgba(255,255,255,0.74)}}

    .na{{color:#94a3b8;font-style:italic;font-size:0.87rem}}

    @media print{{.page{{box-shadow:none;margin:0;border-radius:0}}body{{background:#fff}}}}
  </style>
</head>
<body>
<div class="page">

<!-- ═══ HERO ═══ -->
<div class="hero">
  <div class="hero-top">
    <div class="logo-wrap">
      <div class="logo-box">🏗️</div>
      <div>
        <div class="co-name">UrbanRoof</div>
        <div class="co-tag">Building Diagnostics &amp; Inspection</div>
      </div>
    </div>
    <div class="rpt-meta">
      <strong>Detailed Diagnostic Report (DDR)</strong>
      Date: {report_date}
    </div>
  </div>
  <h1>Detailed Diagnostic Report</h1>
  <p class="hero-sub">System-generated diagnostic analysis based on Inspection Report and Thermal Imaging</p>
  <div class="stats">
    <div class="stat"><span class="stat-n">{insp_pages}</span><span class="stat-l">Inspection Pages</span></div>
    <div class="stat"><span class="stat-n">{therm_pages}</span><span class="stat-l">Thermal Pages</span></div>
    <div class="stat"><span class="stat-n">{total_imgs}</span><span class="stat-l">Images Used</span></div>
    <div class="stat"><span class="stat-n">{areas_count}</span><span class="stat-l">Key Areas Analysed</span></div>
  </div>
</div>

<!-- ═══ BODY ═══ -->
<div class="body">

  <!-- 🚨 IMMEDIATE ACTIONS -->
  <div class="section">
    <div class="sec-title">🚨 Immediate Actions Required</div>
    {imm_html}
  </div>

  <!-- 1. PROPERTY ISSUE SUMMARY -->
  <div class="section">
    <div class="sec-title"><span class="sec-num">1</span> Property Issue Summary</div>
    <ul class="summary-list">{summary_html}</ul>
  </div>

  <!-- 2. ISSUE IMPACT SUMMARY -->
  <div class="section">
    <div class="sec-title"><span class="sec-num">2</span> Issue Impact Summary</div>
    {impact_html}
  </div>

  <!-- 3. AREA-WISE ANALYSIS -->
  <div class="section">
    <div class="sec-title"><span class="sec-num">3</span> Area-wise Analysis — Key Areas (Critical Zones)</div>
    {area_html}
  </div>

  <!-- 4. ROOT CAUSE ANALYSIS -->
  <div class="section">
    <div class="sec-title"><span class="sec-num">4</span> Root Cause Analysis</div>
    <div class="root-box">{ddr.get("root_cause_analysis", "Not Available")}</div>
  </div>

  <!-- 5. PRIORITY MATRIX -->
  <div class="section">
    <div class="sec-title"><span class="sec-num">5</span> Priority Matrix</div>
    <div class="pri-grid">
      <div class="pri-col h"><div class="pri-head">🔴 High Priority</div><ul>{high_li}</ul></div>
      <div class="pri-col m"><div class="pri-head">🟡 Medium Priority</div><ul>{med_li}</ul></div>
      <div class="pri-col l"><div class="pri-head">🟢 Low Priority</div><ul>{low_li}</ul></div>
    </div>
  </div>

  <!-- 6. RECOMMENDED ACTION PLAN -->
  <div class="section">
    <div class="sec-title"><span class="sec-num">6</span> Recommended Action Plan</div>
    {action_html}
  </div>

  <!-- 7. ADDITIONAL INSIGHTS -->
  <div class="section">
    <div class="sec-title"><span class="sec-num">7</span> Additional Insights</div>
    <div class="insight-box">{ddr.get("additional_insights", "Not Available")}</div>
  </div>

  <!-- 8. MISSING / UNCLEAR DATA -->
  <div class="section">
    <div class="sec-title"><span class="sec-num">8</span> Missing / Unclear Data</div>
    <div class="missing-wrap">{missing_html}</div>
  </div>

</div><!-- /body -->

<!-- ═══ FOOTER ═══ -->
<div class="footer">
  <strong>UrbanRoof</strong> — Building Diagnostics &amp; Inspection &nbsp;·&nbsp;
  Report Date: {report_date} &nbsp;·&nbsp;
  Generated by UrbanRoof Diagnostic System &nbsp;·&nbsp;
  All findings must be verified by a licensed engineer before remedial action is taken.
</div>

</div><!-- /page -->
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ UrbanRoof DDR v4 saved: {output_path}")