
"""FastAPI application for ECG2Signal."""
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
from pathlib import Path
from ecg2signal import ECGConverter
from ecg2signal.config import get_settings

settings = get_settings()
app = FastAPI(title="ECG2Signal API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

converter = ECGConverter(settings)

@app.get("/")
def root():
    return {"message": "ECG2Signal API", "version": "0.1.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/convert")
async def convert_ecg(
    file: UploadFile = File(...),
    format: str = Form("wfdb"),
    paper_speed: float = Form(25.0),
    gain: float = Form(10.0),
):
    """Convert ECG image to signals."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        result = converter.convert(tmp_path, paper_speed=paper_speed, gain=gain)
        
        output_dir = Path(tempfile.mkdtemp())
        if format == "wfdb":
            result.export_wfdb(str(output_dir), "ecg")
            return {"status": "success", "format": format, "files": list(output_dir.glob("*"))}
        elif format == "json":
            output_file = output_dir / "ecg.json"
            result.export_json(str(output_file))
            return FileResponse(output_file, media_type="application/json")
        else:
            return {"status": "success", "message": f"Format {format} processed"}
    finally:
        Path(tmp_path).unlink(missing_ok=True)
