# backend/pdf_processor.py
import fitz  # PyMuPDF
import os

def extract_pdf_data(pdf_path: str, session_id: str, report_type: str) -> dict:
    """
    Extracts text and images from a PDF file.
    Returns: { "text": "...", "images": [...], "page_count": N, "report_type": "..." }
    """
    extracted_text = ""
    image_paths = []
    page_count = 0

    image_dir = f"extracted/{session_id}_{report_type}_images"
    os.makedirs(image_dir, exist_ok=True)

    try:
        doc = fitz.open(pdf_path)
        page_count = len(doc)

        for page_num, page in enumerate(doc):
            # Extract text
            page_text = page.get_text()
            if page_text.strip():
                extracted_text += f"\n--- Page {page_num + 1} ---\n{page_text}"

            # Extract embedded images
            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                try:
                    base_image  = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext   = base_image["ext"]
                    filename    = f"page{page_num+1}_img{img_index+1}.{image_ext}"
                    image_path  = os.path.join(image_dir, filename)

                    with open(image_path, "wb") as img_file:
                        img_file.write(image_bytes)

                    image_paths.append(image_path)
                except Exception as img_err:
                    print(f"⚠️ Skipped image xref={xref}: {img_err}")

        doc.close()

        if not extracted_text.strip():
            extracted_text = "Not Available"
            print(f"⚠️ No text found in {pdf_path} — might be a scanned PDF")

    except Exception as e:
        print(f"❌ PDF extraction failed: {e}")
        extracted_text = "Not Available"

    return {
        "text": extracted_text,
        "images": image_paths,
        "page_count": page_count,
        "report_type": report_type
    }