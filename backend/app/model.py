from pathlib import Path
from PIL import Image

_upscaler = None

def _ensure_upscaler():
    global _upscaler
    if _upscaler is not None:
        return _upscaler
    try:
        from realesrgan import RealESRGAN
        import torch
    except Exception as e:
        raise RuntimeError("Install torch (CUDA-matched) and realesrgan") from e
    device = 'cuda' if hasattr(torch, 'cuda') and torch.cuda.is_available() else 'cpu'
    up = RealESRGAN(device, scale=4)
    up.load_weights('weights/RealESRGAN_x4plus.pth', download=True)
    _upscaler = up
    return up

def upscale_image(input_path: str, output_path: str, scale: int = 2):
    up = _ensure_upscaler()
    img = Image.open(input_path).convert('RGB')
    out = up.predict(img)  # native x4
    if scale == 2:
        w, h = out.size
        out = out.resize((w//2, h//2), resample=Image.LANCZOS)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    out.save(output_path, format='PNG')
