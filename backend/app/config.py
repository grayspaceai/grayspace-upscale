import os
from pathlib import Path

# 가중치/파일 저장 경로
WEIGHTS_DIR = Path(os.getenv("WEIGHTS_DIR", "weights")).resolve()
FILES_DIR   = Path(os.getenv("FILES_DIR",   "files")).resolve()

# 가중치 절대경로를 직접 지정하고 싶으면 여기에 환경변수로 넣어도 됨
REAL_ESRGAN_WEIGHT = os.getenv("REAL_ESRGAN_WEIGHT", "")

# 관리자 업로드 보호용 토큰 (없으면 무보호)
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")

def ensure_dirs():
    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    FILES_DIR.mkdir(parents=True, exist_ok=True)
