# browser_manager.py
import subprocess
import socket
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from typing import Optional
import logging

from config import Config


class BrowserManager:
    """브라우저 관리를 담당하는 클래스"""

    def __init__(self, config: Config):
        self.config = config
        self.driver: Optional[webdriver.Chrome] = None
        self.chrome_path = self._find_chrome_path()

    def _find_chrome_path(self) -> str:
        """Chrome 설치 경로를 찾는 메서드"""
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Users\%USERNAME%\AppData\Local\Google\Chrome\Application\chrome.exe"
        ]

        for path in possible_paths:
            expanded_path = os.path.expandvars(path)
            if os.path.exists(expanded_path):
                return expanded_path

        raise FileNotFoundError("Chrome을 찾을 수 없습니다.")

    def is_port_in_use(self, port: int) -> bool:
        """포트가 사용 중인지 확인"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return False
            except socket.error:
                return True

    def kill_chrome_processes(self):
        """Chrome 프로세스 종료"""
        try:
            subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'],
                           capture_output=True, text=True)
            time.sleep(2)
            logging.info("Chrome 프로세스가 종료되었습니다.")
        except Exception as e:
            logging.error(f"Chrome 프로세스 종료 중 오류: {str(e)}")

    def start_chrome_debug_mode(self):
        """Chrome을 디버그 모드로 시작"""
        if self.is_port_in_use(self.config.debug_port):
            logging.info(f"포트 {self.config.debug_port}가 이미 사용 중입니다.")
            return

        try:
            os.makedirs(self.config.user_data_dir, exist_ok=True)

            cmd = [
                self.chrome_path,
                f"--remote-debugging-port={self.config.debug_port}",
                f"--user-data-dir={self.config.user_data_dir}",
                "--no-first-run",
                "--no-default-browser-check"
            ]

            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(3)
            logging.info(f"Chrome이 디버그 모드로 시작되었습니다. 포트: {self.config.debug_port}")

        except Exception as e:
            logging.error(f"Chrome 디버그 모드 시작 실패: {str(e)}")
            raise

    def setup_driver(self):
        """WebDriver 설정 및 초기화"""
        try:
            options = Options()
            options.add_experimental_option("debuggerAddress", f"localhost:{self.config.debug_port}")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            self.driver = webdriver.Chrome(options=options)
            logging.info("WebDriver가 성공적으로 설정되었습니다.")
            return self.driver

        except Exception as e:
            logging.error(f"WebDriver 설정 실패: {str(e)}")
            raise

    def navigate_to_chatgpt(self):
        """ChatGPT 페이지로 이동"""
        if not self.driver:
            raise RuntimeError("WebDriver가 설정되지 않았습니다.")

        try:
            self.driver.get("https://chat.openai.com/")
            time.sleep(3)
            logging.info("ChatGPT 페이지로 이동했습니다.")

        except Exception as e:
            logging.error(f"ChatGPT 페이지 이동 실패: {str(e)}")
            raise

    def connect_to_existing_browser(self):
        """기존 브라우저에 연결"""
        try:
            if not self.is_port_in_use(self.config.debug_port):
                self.start_chrome_debug_mode()
                time.sleep(5)

            self.setup_driver()
            logging.info("기존 브라우저에 연결되었습니다.")

        except Exception as e:
            logging.error(f"브라우저 연결 실패: {str(e)}")
            raise

    def close_browser(self):
        """브라우저 종료"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                logging.info("브라우저가 종료되었습니다.")
        except Exception as e:
            logging.error(f"브라우저 종료 중 오류: {str(e)}")