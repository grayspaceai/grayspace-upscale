import io, uuid, os
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from PIL import Image
from .model import upscale_image

DATA_DIR = Path(os.getenv("DATA_DIR", "data")).resolve()
DATA_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="GraySpace Upscale API", version="0.1.0")

allow_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins, allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

app.mount("/files", StaticFiles(directory=str(DATA_DIR)), name="files")

@app.get("/healthz")
def health():
    return {"ok": True}

@app.post("/upscale")
async def upscale(file: UploadFile = File(...), scale: int = Form(2)):
    job_id = str(uuid.uuid4())
    job_dir = DATA_DIR / job_id; job_dir.mkdir(parents=True, exist_ok=True)
    in_path = job_dir/"input.png"; out_path = job_dir/"output.png"

    img = Image.open(io.BytesIO(await file.read())).convert("RGB")
    img.save(in_path, format="PNG")

    upscale_image(str(in_path), str(out_path), scale=scale)

    return JSONResponse({
        "job_id": job_id,
        "before": f"/files/{job_id}/input.png",
        "after":  f"/files/{job_id}/output.png",
        "scale": scale
    })

