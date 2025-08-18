# eco-bee-Intake-Perception
demo for Intake &amp; Perception

1. **Intake & Perception (Quiz + Vision)** Lead Jonathan, Support Caleb (i have just used plain ocr before feel free to choose model or do this with mistral’s pixtral)
- 5–7 Q “snapshot” form; optional image for meal/outfit; barcode read.
- Vision: classify meal/outfit to category/material; map to factor tables.
- Deliverables:
    - Next.js form components + validation.
    - Image pipeline: **LLaVA-Next** (or **LLaVA-1.6**), fallback CLIP; barcode via `zxing` (web) or `jsbarcode`.
    - REST endpoint: `POST /api/intake` → normalised item list for the Scoring Engine.


# Instructions for windows
1. Install python libraries
- cd backend; pip install -r .\requirements.txt; py -3 .\simple_server.py
- python 
2. Initialize npm
- cd frontend; npm install; npm run dev

# Note:
backend runs on localhost:8000
frontend runs on localhost:3000
paste your key in the .env file in backend
.next frequently gets corrupted run this in the frontend directory:
- Remove-Item -Recurse -Force .next
