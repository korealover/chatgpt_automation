# image_downloader.py
import os
import time
import requests
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from typing import List, Optional
import logging
import base64

from config import Config


class ImageDownloader:
    """이미지 다운로드를 담당하는 클래스"""

    def __init__(self, config: Config, driver):
        self.config = config
        self.driver = driver

    def find_generated_images(self) -> List:
        """생성된 이미지 요소들을 찾기"""
        try:
            wait = WebDriverWait(self.driver, 10)

            # 다양한 이미지 셀렉터 시도
            selectors = [
                "img[class*='absolute top-0 z-1 w-full']",
                "img[src*='dalle']",
                "img[alt*='Generated']",
                ".result-image img",
                "[data-testid*='image'] img"
            ]

            for selector in selectors:
                try:
                    images = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
                    if images:
                        logging.info(f"{len(images)}개의 이미지를 찾았습니다.")
                        return images
                except TimeoutException:
                    continue

            logging.warning("이미지를 찾을 수 없습니다.")
            return []

        except Exception as e:
            logging.error(f"이미지 검색 중 오류: {str(e)}")
            return []

    def generate_filename(self, prompt: str, index: int = 0) -> str:
        """파일명 생성"""
        # 특수문자 제거 및 길이 제한
        safe_prompt = "".join(c for c in prompt if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_prompt = safe_prompt[:50]  # 길이 제한

        timestamp = int(time.time())
        filename = f"{safe_prompt}_{timestamp}_{index}.png"
        return filename

    def download_image_by_url(self, img_element, filename: str) -> bool:
        """URL을 통한 이미지 다운로드"""
        try:
            img_url = img_element.get_attribute('src')
            if not img_url or img_url.startswith('data:'):
                return False

            response = requests.get(img_url, timeout=30)
            response.raise_for_status()

            filepath = os.path.join(self.config.download_folder, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)

            logging.info(f"이미지 다운로드 완료: {filename}")
            return True

        except Exception as e:
            logging.error(f"URL 다운로드 실패: {str(e)}")
            return False

    def download_blob_image(self, img_element, filename: str) -> bool:
        """Blob URL 이미지 다운로드"""
        try:
            # JavaScript를 사용하여 blob을 base64로 변환
            script = """
            const img = arguments[0];
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = img.naturalWidth;
            canvas.height = img.naturalHeight;
            ctx.drawImage(img, 0, 0);
            return canvas.toDataURL('image/png');
            """

            base64_data = self.driver.execute_script(script, img_element)
            if not base64_data:
                return False

            # base64 데이터에서 실제 이미지 데이터 추출
            img_data = base64_data.split(',')[1]
            img_bytes = base64.b64decode(img_data)

            filepath = os.path.join(self.config.download_folder, filename)
            with open(filepath, 'wb') as f:
                f.write(img_bytes)

            logging.info(f"Blob 이미지 다운로드 완료: {filename}")
            return True

        except Exception as e:
            logging.error(f"Blob 다운로드 실패: {str(e)}")
            return False

    def download_image_by_click(self, img_element, filename: str) -> bool:
        """클릭을 통한 이미지 다운로드"""
        try:
            # 이미지 우클릭
            actions = ActionChains(self.driver)
            actions.context_click(img_element).perform()
            time.sleep(1)

            # 컨텍스트 메뉴에서 "이미지 저장" 클릭 시도
            try:
                save_option = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), '이미지 저장') or contains(text(), 'Save image')]"))
                )
                save_option.click()
                logging.info(f"클릭 다운로드 시도: {filename}")
                return True

            except TimeoutException:
                logging.warning("컨텍스트 메뉴를 찾을 수 없습니다.")
                return False

        except Exception as e:
            logging.error(f"클릭 다운로드 실패: {str(e)}")
            return False

    def take_image_screenshot(self, img_element, filename: str) -> bool:
        """스크린샷을 통한 이미지 저장"""
        try:
            # 이미지 요소로 스크롤
            self.driver.execute_script("arguments[0].scrollIntoView(true);", img_element)
            time.sleep(1)

            # 요소 스크린샷
            screenshot = img_element.screenshot_as_png

            filepath = os.path.join(self.config.download_folder, filename)
            with open(filepath, 'wb') as f:
                f.write(screenshot)

            logging.info(f"스크린샷 저장 완료: {filename}")
            return True

        except Exception as e:
            logging.error(f"스크린샷 저장 실패: {str(e)}")
            return False

    def resize_downloaded_image(self, filepath: str, max_size: tuple = (1024, 1024)):
        """다운로드된 이미지 크기 조정"""
        try:
            with Image.open(filepath) as img:
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    img.save(filepath, optimize=True, quality=85)
                    logging.info(f"이미지 크기 조정 완료: {filepath}")

        except Exception as e:
            logging.error(f"이미지 크기 조정 실패: {str(e)}")

    def download_generated_images(self, prompt: str) -> int:
        """생성된 모든 이미지 다운로드"""
        images = self.find_generated_images()
        if not images:
            return 0

        downloaded_count = 0

        for i, img_element in enumerate(images):
            filename = self.generate_filename(prompt, i)

            # 다양한 다운로드 방법 시도
            methods = [
                self.download_image_by_url,
                self.download_blob_image,
                self.download_image_by_click,
                self.take_image_screenshot
            ]

            for method in methods:
                if method(img_element, filename):
                    # 이미지 크기 조정
                    filepath = os.path.join(self.config.download_folder, filename)
                    self.resize_downloaded_image(filepath)
                    downloaded_count += 1
                    break
            else:
                logging.warning(f"이미지 {i + 1} 다운로드 실패")

        logging.info(f"총 {downloaded_count}개의 이미지를 다운로드했습니다.")
        return downloaded_count