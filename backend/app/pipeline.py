from __future__ import annotations
import io
import os
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from PIL import Image
import cv2
import torch

from .config import WEIGHTS_DIR, REAL_ESRGAN_WEIGHT, ensure_dirs

@dataclass
class UpscaleConfig:
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    tile: int = int(os.getenv("TILE", "0"))
    tile_pad: int = int(os.getenv("TILE_PAD", "10"))

class UpscalePipeline:
    """
    노트북 코드를 그대로 옮겨 담는 래퍼.
    - setup(): 가중치 로드 & 모델 초기화
    - run(image_bytes, scale) -> np.ndarray(BGR)
    """

    def __init__(self, cfg: UpscaleConfig | None = None):
        self.cfg = cfg or UpscaleConfig()
        self.model = None
        self._weight_path = None

    def _find_weight(self) -> str:
        ensure_dirs()
        cand: list[Path] = []
        if REAL_ESRGAN_WEIGHT:
            cand.append(Path(REAL_ESRGAN_WEIGHT))
        cand += [
            WEIGHTS_DIR / "RealESRGAN_x4plus.pth",   # 대표 이름(필요 시 바꿔)
        ]
        for p in cand:
            if p.exists():
                return str(p)
        raise RuntimeError(
            f"[weights-missing] 가중치(.pth)를 {WEIGHTS_DIR}에 올리거나 "
            f"REAL_ESRGAN_WEIGHT 환경변수로 절대경로를 지정하세요."
        )

    def setup(self):
        """여기에서 노트북의 '모델 로드' 셀을 그대로 옮겨 담는다."""
        self._weight_path = self._find_weight()

        # =========== NOTEBOOK ZONE START (모델 로드/초기화) ===========
        # 예시) Real-ESRGAN을 썼다면 (네 노트북과 동일하게 수정)
        from basicsr.archs.rrdbnet_arch import RRDBNet
        from realesrgan import RealESRGANer

        model = RRDBNet(num_in_ch=3, num_out_ch=3,
                        num_feat=64, num_block=23,
                        num_grow_ch=32, scale=4)

        self.model = RealESRGANer(
            scale=4,
            model_path=self._weight_path,
            model=model,
            tile=self.cfg.tile,
            tile_pad=self.cfg.tile_pad,
            pre_pad=0,
            half=(self.cfg.device == "cuda"),
        )
        # ============ NOTEBOOK ZONE END ============

    def run(self, image_bytes: bytes, scale: int = 2) -> np.ndarray:
        """여기에서 노트북의 '추론/후처리' 셀을 그대로 옮긴다."""
        if self.model is None:
            self.setup()

        # =========== NOTEBOOK ZONE START (전처리/추론/후처리) ===========
        # 공통: 바이너리 → OpenCV 이미지(BGR)
        img_array = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("이미지 디코딩 실패")

        # 예시) Real-ESRGAN
        out, _ = self.model.enhance(img, outscale=scale)
        return out
        # ============ NOTEBOOK ZONE END ============
