from pdf_processor import process_both_reports
from ai_processor import generate_ddr
from report_builder import build_report

# Replace these with any two PDFs you have
result = process_both_reports(
    "uploads/sample_inspection.pdf",
    "uploads/sample_thermal.pdf"
)

ddr = generate_ddr(
    inspection_text=result["inspection"]["text"],
    thermal_text=result["thermal"]["text"],
    inspection_images=result["inspection"]["images"],
    thermal_images=result["thermal"]["images"]
)

report_path = build_report(ddr, "test001")
print(f"Done! Open: {report_path}")