# chatgpt_automation.py
import time
import logging
from typing import Dict, Any, Optional

from config import Config
from conf.browser_manager import BrowserManager
# from image_downloader import ImageDownloader
from excel_handler import ExcelHandler
from chatgpt_interface import ChatGPTInterface


class ChatGPTAutomation:
    """모든 기능을 통합하는 메인 클래스"""

    def __init__(self, excel_path: str, config: Optional[Config] = None):
        self.config = config or Config()
        self.excel_handler = ExcelHandler(excel_path)

        # 컴포넌트 초기화
        self.browser_manager = BrowserManager(self.config)
        self.driver = None
        # self.image_downloader = None
        self.chatgpt_interface = None

        # 로깅 설정
        self._setup_logging()

    def _setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('chatgpt_automation.log'),
                logging.StreamHandler()
            ]
        )

    def initialize(self):
        """시스템 초기화"""
        try:
            # 브라우저 연결
            self.browser_manager.connect_to_existing_browser()
            self.driver = self.browser_manager.driver

            # ChatGPT 페이지로 이동
            self.browser_manager.navigate_to_chatgpt()

            # 컴포넌트 초기화
            # self.image_downloader = ImageDownloader(self.config, self.driver)
            self.chatgpt_interface = ChatGPTInterface(self.config, self.driver)

            logging.info("시스템 초기화 완료")
            return True

        except Exception as e:
            logging.error(f"시스템 초기화 실패: {str(e)}")
            return False

    def run_automation(self) -> Dict[str, Any]:
        """자동화 실행"""
        results = {
            'total_prompts': 0,
            'processed_prompts': 0,
            'downloaded_images': 0,
            'errors': []
        }

        try:
            # 시스템 초기화
            if not self.initialize():
                results['errors'].append("시스템 초기화 실패")
                return results

            # 프롬프트 데이터 로드
            prompts = self.excel_handler.get_unprocessed_prompts()
            results['total_prompts'] = len(prompts)

            if not prompts:
                logging.info("처리할 프롬프트가 없습니다.")
                return results

            # 각 프롬프트 처리
            for i, prompt_data in enumerate(prompts):
                try:
                    result = self._process_single_prompt(prompt_data, i)

                    if result['success']:
                        results['processed_prompts'] += 1
                        results['downloaded_images'] += result.get('downloaded_count', 0)
                    else:
                        results['errors'].append(f"프롬프트 {i + 1}: {result.get('error', '알 수 없는 오류')}")

                    # 진행 상황 로깅
                    logging.info(f"진행 상황: {i + 1}/{len(prompts)} 완료")

                    # 요청 간격 조절
                    time.sleep(3)

                except Exception as e:
                    error_msg = f"프롬프트 {i + 1} 처리 중 오류: {str(e)}"
                    logging.error(error_msg)
                    results['errors'].append(error_msg)

            logging.info(f"자동화 완료: {results['processed_prompts']}/{results['total_prompts']} 처리됨")
            return results

        except Exception as e:
            error_msg = f"자동화 실행 중 오류: {str(e)}"
            logging.error(error_msg)
            results['errors'].append(error_msg)
            return results

    def _process_single_prompt(self, prompt_data: Dict[str, Any], index: int) -> Dict[str, Any]:
        """단일 프롬프트 처리"""
        result = {
            'success': False,
            'downloaded_count': 0,
            'error': None
        }

        try:
            # 프롬프트 조합
            full_prompt = self.excel_handler.combine_prompt_elements(prompt_data)
            logging.info(f"처리 중: {full_prompt[:100]}...")

            # ChatGPT에 프롬프트 전송
            send_result = self.chatgpt_interface.send_prompt_to_chatgpt(full_prompt)

            if not send_result['success']:
                result['error'] = send_result.get('error', '프롬프트 전송 실패')
                return result

            # # 이미지 타입 프롬프트인 경우 이미지 다운로드
            # if send_result['prompt_type'] == 'image' and send_result['has_images']:
            #     downloaded_count = self.image_downloader.download_generated_images(full_prompt)
            #     result['downloaded_count'] = downloaded_count
            #
            #     if downloaded_count > 0:
            #         logging.info(f"{downloaded_count}개의 이미지를 다운로드했습니다.")
            #     else:
            #         logging.warning("이미지를 다운로드하지 못했습니다.")

            # Excel 처리 상태 업데이트
            self.excel_handler.update_processed_status(index)

            result['success'] = True
            return result

        except Exception as e:
            error_msg = f"프롬프트 처리 중 오류: {str(e)}"
            logging.error(error_msg)
            result['error'] = error_msg
            return result

    def cleanup(self):
        """리소스 정리"""
        try:
            if self.browser_manager:
                self.browser_manager.close_browser()
            logging.info("리소스 정리 완료")

        except Exception as e:
            logging.error(f"리소스 정리 중 오류: {str(e)}")