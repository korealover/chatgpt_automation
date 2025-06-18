# config.py
from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class Config:
    """애플리케이션 설정을 관리하는 클래스"""
    debug_port: int = 9222
    default_wait_time: int = 60
    max_wait_time: int = 300
    download_folder: str = "./chatgpt_images"
    user_data_dir: Optional[str] = None
    chrome_path: Optional[str] = None

    def __post_init__(self):
        # 다운로드 폴더 생성
        os.makedirs(self.download_folder, exist_ok=True)

        # 기본 사용자 데이터 디렉토리 설정
        if not self.user_data_dir:
            self.user_data_dir = os.path.join(os.getcwd(), "chrome_user_data")