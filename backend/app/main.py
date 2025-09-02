from __future__ import annotations
from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uuid, shutil, cv2

from .config import ensure_dirs, FILES_DIR, WEIGHTS_DIR, ADMIN_TOKEN
from .pipeline import UpscalePipeline, UpscaleConfig

app = FastAPI(title="grayspace-upscale")
app.mount("/files", StaticFiles(directory=str(FILES_DIR)), name="files")

_pipeline: UpscalePipeline | None = None

def get_pipeline() -> UpscalePipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = UpscalePipeline(UpscaleConfig())
    return _pipeline

@app.get("/healthz")
def healthz():
    return {"ok": True}

def _auth(x_admin_token: str | None):
    if ADMIN_TOKEN and x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="unauthorized")

@app.post("/admin/weights/upload")
def upload_weight(file: UploadFile = File(...), x_admin_token: str | None = Header(default=None)):
    _auth(x_admin_token)
    ensure_dirs()
    if not file.filename.endswith(".pth"):
        raise HTTPException(400, "upload .pth only")
    dest = WEIGHTS_DIR / file.filename
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    # 다음 요청부터 새 가중치 쓰게 파이프라인 초기화
    global _pipeline; _pipeline = None
    return {"saved": str(dest)}

@app.get("/admin/weights")
def list_weights(x_admin_token: str | None = Header(default=None)):
    _auth(x_admin_token)
    ensure_dirs()
    files = [p.name for p in WEIGHTS_DIR.glob("*.pth")]
    return {"dir": str(WEIGHTS_DIR), "files": files}

@app.post("/upscale")
async def upscale(file: UploadFile = File(...), scale: int = Form(2)):
    ensure_dirs()
    job = uuid.uuid4().hex
    job_dir = FILES_DIR / job
    job_dir.mkdir(parents=True, exist_ok=True)

    in_path  = job_dir / "input.png"
    out_path = job_dir / "output.png"

    with in_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    with in_path.open("rb") as f:
        img_bytes = f.read()

    out_bgr = get_pipeline().run(img_bytes, scale=scale)
    cv2.imwrite(str(out_path), out_bgr)

    return {
        "job_id": job,
        "before": f"/files/{job}/input.png",
        "after":  f"/files/{job}/output.png",
        "scale":  scale
    }
