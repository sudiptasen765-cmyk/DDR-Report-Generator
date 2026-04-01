# backend/main.py
import os
from dotenv import load_dotenv

# ✅ Load .env FIRST before anything else
load_dotenv()

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil
import uuid

from pdf_processor import extract_pdf_data
from ai_processor import generate_ddr_report
from report_builder import build_html_report

app = FastAPI(title="DDR Report Generator")

# ✅ Allow React frontend to call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
EXTRACTED_DIR = "extracted"
OUTPUT_DIR = "outputs"

for d in [UPLOAD_DIR, EXTRACTED_DIR, OUTPUT_DIR]:
    os.makedirs(d, exist_ok=True)


@app.get("/")
def root():
    return {"status": "DDR Backend Running ✅", "model": "gpt-4o"}


@app.post("/generate-ddr")
async def generate_ddr(
    inspection_report: UploadFile = File(...),
    thermal_report: UploadFile = File(...)
):
    session_id = str(uuid.uuid4())[:8]

    try:
        # --- Save uploaded PDFs ---
        inspection_path = f"{UPLOAD_DIR}/{session_id}_inspection.pdf"
        thermal_path = f"{UPLOAD_DIR}/{session_id}_thermal.pdf"

        with open(inspection_path, "wb") as f:
            shutil.copyfileobj(inspection_report.file, f)
        with open(thermal_path, "wb") as f:
            shutil.copyfileobj(thermal_report.file, f)

        print(f"✅ Files saved: {inspection_path}, {thermal_path}")

        # --- Extract text + images ---
        inspection_data = extract_pdf_data(inspection_path, session_id, "inspection")
        thermal_data    = extract_pdf_data(thermal_path,    session_id, "thermal")

        print(f"✅ Extraction done")
        print(f"   Inspection: {len(inspection_data['text'])} chars, {len(inspection_data['images'])} images")
        print(f"   Thermal:    {len(thermal_data['text'])} chars, {len(thermal_data['images'])} images")

        # --- Generate DDR with OpenAI ---
        ddr_content = generate_ddr_report(inspection_data, thermal_data)
        print(f"✅ AI report generated")

        # --- Build HTML report ---
        output_path = f"{OUTPUT_DIR}/{session_id}_ddr_report.html"
        build_html_report(ddr_content, inspection_data, thermal_data, output_path)
        print(f"✅ HTML report saved: {output_path}")

        return FileResponse(
            output_path,
            media_type="text/html",
            filename=f"DDR_Report_{session_id}.html"
        )

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))