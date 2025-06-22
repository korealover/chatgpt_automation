# ChatGPT 자동화 도구 (ChatGPT Automation Tool)

## 개요

이 프로젝트는 ChatGPT 웹 인터페이스와 자동으로 상호작용하여 프롬프트를 전송하고 응답을 수집하는 Python 기반 자동화 도구입니다. Excel 파일에서 프롬프트를 읽어와 ChatGPT에 전송하고, 생성된 이미지를 자동으로 다운로드하는 기능을 제공합니다.

## 주요 기능

- **ChatGPT 웹 인터페이스 자동화**: Selenium을 사용한 웹 브라우저 자동 제어
- **Excel 파일 처리**: Excel 파일에서 프롬프트 읽기 및 결과 저장
- **이미지 자동 다운로드**: ChatGPT에서 생성된 이미지 자동 감지 및 다운로드
- **프롬프트 타입 감지**: 텍스트 응답과 이미지 생성 프롬프트 자동 구분
- **브라우저 관리**: Chrome 브라우저 자동 설정 및 관리

## 프로젝트 구조
```aiignore
chatgpt_automation/ 
├── main.py # 메인 실행 파일 
├── config.py # 설정 파일 
├── chatgpt_interface.py # ChatGPT 인터페이스 클래스 
├── conf/ # 구성 모듈 디렉토리 
│ ├── browser_manager.py # 브라우저 관리 
│ ├── chatgpt_automation.py # 메인 자동화 로직 
│ ├── excel_handler.py # Excel 파일 처리 
│ └── image_downloader.py # 이미지 다운로드 관리 
├── pyproject.toml # 프로젝트 설정 및 의존성 
└── uv.lock # 패키지 잠금 파일

```
## 설치 및 설정

### 요구사항

- Python 3.13.1+
- UV 패키지 매니저

### 설치 방법

1. 프로젝트 클론:
```bash
bash git clone <repository-url> cd chatgpt_automation
```
2. 의존성 설치:
```bash
uv install
```
3. Chrome 브라우저가 설치되어 있는지 확인


## 사용 방법
### 기본 실행
```bash
python main.py
```
### Excel 파일 준비
Excel 파일에 다음과 같은 형식으로 프롬프트를 준비하세요:

| 프롬프트 | 결과 | 이미지_경로 |
| --- | --- | --- |
| 고양이 그림을 그려주세요 |  |  |
| 파이썬 코드 예제를 보여주세요 |  |  |
### 설정 옵션
파일에서 다음 설정을 조정할 수 있습니다: `config.py`
- **max_wait_time**: 응답 대기 최대 시간
- **image_download_path**: 이미지 다운로드 경로
- **browser_options**: 브라우저 실행 옵션

## 주요 클래스
### ChatGPTInterface
ChatGPT 웹 인터페이스와의 상호작용을 담당:
- `send_prompt_to_chatgpt()`: 프롬프트 전송
- `wait_for_response_completion()`: 응답 완료 대기
- `has_image_elements()`: 이미지 요소 감지
- `detect_prompt_type()`: 프롬프트 타입 감지

### 핵심 기능
- **자동 프롬프트 타입 감지**: 텍스트와 이미지 생성 프롬프트 자동 구분
- **응답 완료 감지**: ChatGPT 응답이 완료될 때까지 지능적 대기
- **이미지 생성 대기**: 이미지 생성 완료 시까지 추가 대기 시간 제공
- **강력한 요소 탐지**: 다양한 CSS 셀렉터를 통한 안정적인 웹 요소 찾기

## 개발 환경
- **언어**: Python 3.13.1
- **패키지 매니저**: UV
- **주요 의존성**:
    - Selenium (웹 자동화)
    - openpyxl (Excel 처리)
    - requests (HTTP 요청)

## 로깅
프로그램 실행 중 상세한 로그가 출력되어 디버깅과 모니터링이 가능합니다:
- 프롬프트 전송 상태
- 응답 대기 진행상황
- 이미지 감지 및 다운로드 상태
- 오류 메시지 및 예외 처리

## 주의사항
- ChatGPT 웹사이트의 구조 변경에 따라 셀렉터 업데이트가 필요할 수 있습니다
- 브라우저 자동화 특성상 안정적인 인터넷 연결이 필요합니다
- 대량의 요청 시 ChatGPT의 사용 제한에 주의하세요

## 라이선스
이 프로젝트는 개인 및 교육 목적으로 사용하실 수 있습니다.

## 기여
버그 리포트나 개선 제안은 [jhsun3692@gmail.com](mailto:jhsun3692@gmail.com)으로 보내주세요.

