# chatgpt_interface.py
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Optional, Dict, Any
import logging
import re

from config import Config


class ChatGPTInterface:
    """ChatGPT 웹 인터페이스와의 상호작용을 담당하는 클래스"""

    def __init__(self, config: Config, driver):
        self.config = config
        self.driver = driver
        self.prompt_counter = 0

    def wait_for_prompt_input(self) -> bool:
        """프롬프트 입력창이 준비될 때까지 대기"""
        try:
            selectors = [
                "textarea[placeholder*='Message']",
                "textarea[data-id='root']",
                "#prompt-textarea",
                "textarea[placeholder*='메시지']"
            ]

            for selector in selectors:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    logging.info("프롬프트 입력창이 준비되었습니다.")
                    return True
                except TimeoutException:
                    continue

            logging.error("프롬프트 입력창을 찾을 수 없습니다.")
            return False

        except Exception as e:
            logging.error(f"프롬프트 입력창 대기 중 오류: {str(e)}")
            return False

    def wait_for_response_completion(self) -> bool:
        """ChatGPT 응답 완료까지 대기"""
        try:
            max_wait_time = self.config.max_wait_time
            start_time = time.time()

            while time.time() - start_time < max_wait_time:
                if not self.is_chatgpt_responding():
                    if self.is_response_complete():
                        logging.info("응답이 완료되었습니다.")
                        return True

                time.sleep(2)

            logging.warning("응답 대기 시간이 초과되었습니다.")
            return False

        except Exception as e:
            logging.error(f"응답 대기 중 오류: {str(e)}")
            return False

    def is_chatgpt_responding(self) -> bool:
        """ChatGPT가 현재 응답 중인지 확인"""
        try:
            # 응답 중 표시기들 확인
            responding_indicators = [
                "button[aria-label='Stop generating']",
                "button[data-testid='stop-button']",
                ".result-streaming",
                "[data-testid='stop-button']",
                "button:contains('Stop')",
                ".loading",
                ".generating"
            ]

            for indicator in responding_indicators:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, indicator)
                    if elements and any(elem.is_displayed() for elem in elements):
                        return True
                except:
                    continue

            return False

        except Exception as e:
            logging.error(f"응답 상태 확인 중 오류: {str(e)}")
            return False

    def is_response_complete(self) -> bool:
        """응답이 완료되었는지 확인"""
        try:
            # 완료 표시기들 확인
            completion_indicators = [
                "button[aria-label*='Send message']",
                "button[data-testid='send-button']",
                "svg[data-testid='send-button']"
            ]

            for indicator in completion_indicators:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, indicator)
                    if elements and any(elem.is_enabled() for elem in elements):
                        return True
                except:
                    continue

            # 스트리밍 완료 확인
            try:
                streaming_elements = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    "[data-is-streaming='false']"
                )
                if streaming_elements:
                    return True
            except:
                pass

            return False

        except Exception as e:
            logging.error(f"응답 완료 확인 중 오류: {str(e)}")
            return False

    def has_image_elements(self) -> bool:
        """페이지에 이미지 요소가 있는지 확인 (개선된 버전)"""
        try:
            # 더 포괄적인 이미지 셀렉터
            selectors = [
                "img[src*='blob:']",
                "img[src*='dalle']",
                "img[src*='oaidalleapiprodscus']",  # DALL-E 3 이미지
                "img[alt*='Generated']",
                "img[alt*='generated']",
                ".result-image img",
                "[data-testid*='image'] img",
                "img[src*='chatgpt']",
                "img[width][height]:not([src*='avatar'])",  # 아바타 제외한 크기가 있는 이미지
                "div[data-message-author-role='assistant'] img",  # 어시스턴트 메시지 내 이미지
                ".message img",
                "figure img",
                ".dalle-image img"
            ]

            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    valid_images = []

                    for element in elements:
                        try:
                            # 이미지가 실제로 표시되고 크기가 있는지 확인
                            if (element.is_displayed() and
                                    element.size['width'] > 50 and
                                    element.size['height'] > 50):
                                src = element.get_attribute('src')
                                # 유효한 이미지 소스인지 확인
                                if src and not src.startswith('data:image/svg'):
                                    valid_images.append(element)
                        except:
                            continue

                    if valid_images:
                        logging.info(f"{len(valid_images)}개의 유효한 이미지를 발견했습니다 (셀렉터: {selector})")
                        return True

                except Exception as e:
                    logging.debug(f"셀렉터 {selector} 확인 중 오류: {str(e)}")
                    continue

            logging.warning("유효한 이미지 요소를 찾을 수 없습니다.")
            return False

        except Exception as e:
            logging.error(f"이미지 요소 확인 중 오류: {str(e)}")
            return False

    def wait_for_image_generation(self, timeout: int = 120) -> bool:
        """이미지 생성 완료까지 대기 (새로운 메소드)"""
        try:
            start_time = time.time()

            while time.time() - start_time < timeout:
                # 이미지 생성 진행 상황 확인
                if self.is_image_generation_in_progress():
                    logging.info("이미지 생성 중...")
                    time.sleep(5)
                    continue

                # 이미지가 생성되었는지 확인
                if self.has_image_elements():
                    logging.info("이미지 생성이 완료되었습니다.")
                    # 추가 로딩 시간 제공
                    time.sleep(3)
                    return True

                time.sleep(2)

            logging.warning("이미지 생성 대기 시간이 초과되었습니다.")
            return False

        except Exception as e:
            logging.error(f"이미지 생성 대기 중 오류: {str(e)}")
            return False

    def is_image_generation_in_progress(self) -> bool:
        """이미지 생성이 진행 중인지 확인"""
        try:
            # 이미지 생성 진행 상황 표시기들
            progress_indicators = [
                "[data-testid='loading']",
                ".animate-spin",
                ".loading",
                ".generating",
                "div:contains('Generating')",
                "div:contains('Creating')",
                ".progress-bar",
                "[role='progressbar']"
            ]

            for indicator in progress_indicators:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, indicator)
                    if elements and any(elem.is_displayed() for elem in elements):
                        return True
                except:
                    continue

            return False

        except Exception as e:
            logging.error(f"이미지 생성 진행 상황 확인 중 오류: {str(e)}")
            return False

    def detect_prompt_type(self, prompt: str) -> str:
        """프롬프트 타입 감지 (이미지 생성 vs 텍스트)"""
        image_keywords = [
            'generate', 'create', 'draw', 'paint', 'design', 'illustration',
            'picture', 'image', 'photo', 'artwork', 'sketch', 'render',
            '생성', '그려', '만들어', '디자인', '일러스트', '그림', '사진'
        ]

        prompt_lower = prompt.lower()

        if any(keyword in prompt_lower for keyword in image_keywords):
            return "image"
        else:
            return "text"

    def send_prompt_to_chatgpt(self, prompt: str) -> Dict[str, Any]:
        """ChatGPT에 프롬프트 전송 (개선된 버전)"""
        result = {
            'success': False,
            'prompt_type': 'text',
            'has_images': False,
            'error': None
        }

        try:
            # 프롬프트 타입 감지
            result['prompt_type'] = self.detect_prompt_type(prompt)
            logging.info(f"감지된 프롬프트 타입: {result['prompt_type']}")

            # 입력창 대기
            if not self.wait_for_prompt_input():
                result['error'] = "입력창을 찾을 수 없습니다."
                return result

            # 입력창 찾기 및 프롬프트 입력
            selectors = [
                "textarea[placeholder*='Message']",
                "textarea[data-id='root']",
                "#prompt-textarea",
                "textarea[placeholder*='메시지']",
                "div[contenteditable='true']",  # 새로운 입력 방식
                "textarea[id*='prompt']"
            ]

            input_element = None
            for selector in selectors:
                try:
                    input_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if input_element.is_displayed() and input_element.is_enabled():
                        logging.info(f"입력창을 찾았습니다: {selector}")
                        break
                except:
                    continue

            if not input_element:
                result['error'] = "입력창을 찾을 수 없습니다."
                return result

            # 기존 텍스트 클리어 및 새 프롬프트 입력
            input_element.clear()
            time.sleep(0.5)
            input_element.send_keys(prompt)
            time.sleep(1)

            # 전송 버튼 클릭 또는 Enter 키 사용
            send_selectors = [
                "button[data-testid='send-button']",
                "button[aria-label*='Send']",
                "button[type='submit']",
                "svg[fill='currentColor'] parent::button"
            ]

            sent = False
            for selector in send_selectors:
                try:
                    send_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if send_button.is_enabled():
                        send_button.click()
                        sent = True
                        logging.info(f"전송 버튼 클릭: {selector}")
                        break
                except:
                    continue

            if not sent:
                input_element.send_keys(Keys.RETURN)
                logging.info("Enter 키로 전송")

            self.prompt_counter += 1
            logging.info(f"프롬프트 전송 완료: {prompt[:50]}...")

            # 일반 응답 대기
            if not self.wait_for_response_completion():
                result['error'] = "응답 대기 시간 초과"
                return result

            # 이미지 타입 프롬프트인 경우 추가 대기
            if result['prompt_type'] == 'image':
                logging.info("이미지 생성 프롬프트로 감지됨. 이미지 생성 완료까지 대기 중...")
                if self.wait_for_image_generation():
                    result['has_images'] = True
                    logging.info("이미지 생성 완료 확인됨")
                else:
                    logging.warning("이미지 생성이 완료되지 않았거나 감지되지 않음")
                    # 그래도 한 번 더 확인
                    time.sleep(5)
                    result['has_images'] = self.has_image_elements()
            else:
                result['has_images'] = self.has_image_elements()

            result['success'] = True
            logging.info(f"응답 완료. 이미지 포함: {result['has_images']}")
            return result

        except Exception as e:
            error_msg = f"프롬프트 전송 중 오류: {str(e)}"
            logging.error(error_msg)
            result['error'] = error_msg
            return result

    def get_latest_response(self) -> Optional[str]:
        """최신 응답 텍스트 가져오기"""
        try:
            # 응답 메시지 셀렉터들
            selectors = [
                "[data-message-author-role='assistant']:last-child",
                ".message.assistant:last-child",
                ".response-message:last-child"
            ]

            for selector in selectors:
                try:
                    response_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if response_element:
                        return response_element.text.strip()
                except:
                    continue

            return None

        except Exception as e:
            logging.error(f"응답 텍스트 가져오기 실패: {str(e)}")
            return None

    def clear_conversation(self):
        """대화 내용 초기화"""
        try:
            # 새 채팅 시작 버튼 찾기
            new_chat_selectors = [
                "button[aria-label*='New chat']",
                "a[href='/']",
                "button:contains('New chat')"
            ]

            for selector in new_chat_selectors:
                try:
                    new_chat_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    new_chat_button.click()
                    time.sleep(2)
                    logging.info("새 채팅을 시작했습니다.")
                    return True
                except:
                    continue

            logging.warning("새 채팅 버튼을 찾을 수 없습니다.")
            return False

        except Exception as e:
            logging.error(f"대화 초기화 실패: {str(e)}")
            return False