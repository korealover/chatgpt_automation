# main.py
import logging
from pathlib import Path

from config import Config
from conf.chatgpt_automation import ChatGPTAutomation


def main():
    """메인 실행 함수"""

    # Excel 파일 경로 설정
    excel_path = input("Excel 파일 경로를 입력하세요 (예: prompt.xlsx): ").strip()

    if not excel_path:
        excel_path = "prompts.xlsx"  # 기본값

    # 파일 존재 확인
    if not Path(excel_path).exists():
        print(f"❌ Excel 파일을 찾을 수 없습니다: {excel_path}")
        return

    try:
        # 설정 생성
        config = Config(
            debug_port=9222,
            download_folder="./downloaded_images",
            default_wait_time=30,
            max_wait_time=120
        )

        # 자동화 시스템 초기화
        automation = ChatGPTAutomation(excel_path, config)

        print("🚀 ChatGPT 자동화를 시작합니다...")

        # 자동화 실행
        results = automation.run_automation()

        # 결과 출력
        print("\n📊 실행 결과:")
        print(f"• 전체 프롬프트: {results['total_prompts']}개")
        print(f"• 처리된 프롬프트: {results['processed_prompts']}개")
        print(f"• 다운로드된 이미지: {results['downloaded_images']}개")

        if results['errors']:
            print(f"• 오류 발생: {len(results['errors'])}건")
            for error in results['errors']:
                print(f"  - {error}")

        print("\n✅ 자동화가 완료되었습니다!")

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        logging.error(f"메인 실행 중 오류: {str(e)}")

    finally:
        # 리소스 정리
        try:
            automation.cleanup()
        except:
            pass


if __name__ == "__main__":
    main()