# excel_handler.py
import pandas as pd
import os
from typing import List, Dict, Optional, Any
import logging


class ExcelHandler:
    """Excel 파일 처리를 담당하는 클래스"""

    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self.validate_file()

    def validate_file(self):
        """Excel 파일 존재 여부 확인"""
        if not os.path.exists(self.excel_path):
            raise FileNotFoundError(f"Excel 파일을 찾을 수 없습니다: {self.excel_path}")

        if not self.excel_path.endswith(('.xlsx', '.xls')):
            raise ValueError("지원되지 않는 파일 형식입니다. Excel 파일(.xlsx, .xls)을 사용하세요.")

    def get_prompts_from_excel(self) -> List[Dict[str, Any]]:
        """Excel 파일에서 프롬프트 데이터를 읽어오기 (G열 2행부터)"""
        try:
            # Excel 파일 읽기 (헤더는 1행으로 설정)
            df = pd.read_excel(self.excel_path, header=0)

            # G열(인덱스 6)에 해당하는 컬럼명 확인
            if len(df.columns) <= 6:
                raise ValueError("엑셀 파일에 G열이 존재하지 않습니다.")

            # G열의 컬럼명 가져오기 (인덱스 6이 G열)
            g_column = df.columns[6]

            # 2행부터 시작 (인덱스는 0부터 시작하므로 1부터)
            df = df.iloc[1:].copy()

            # G열에 값이 있는 행만 필터링
            df = df.dropna(subset=[g_column])
            df = df[df[g_column].astype(str).str.strip() != '']

            # 딕셔너리 리스트로 변환
            prompts = []
            for index, row in df.iterrows():
                prompt_value = str(row[g_column]).strip()
                if prompt_value and prompt_value.lower() != 'nan':
                    prompt_data = {
                        'prompt': prompt_value,
                        'row_index': index + 1  # 원본 엑셀 행 번호 (1부터 시작)
                    }
                    prompts.append(prompt_data)

            logging.info(f"Excel G열에서 {len(prompts)}개의 프롬프트를 읽었습니다 (2행부터).")
            return prompts

        except Exception as e:
            logging.error(f"Excel 파일 읽기 실패: {str(e)}")
            raise

    def update_processed_status(self, row_index: int):
        """특정 행의 처리 상태를 업데이트"""
        try:
            df = pd.read_excel(self.excel_path)

            # processed 컬럼이 없으면 추가
            if 'processed' not in df.columns:
                df['processed'] = False

            # 해당 행의 상태 업데이트
            if 0 <= row_index < len(df):
                df.at[row_index, 'processed'] = True

                # Excel 파일 저장
                df.to_excel(self.excel_path, index=False)
                logging.info(f"행 {row_index + 1}의 처리 상태가 업데이트되었습니다.")

        except Exception as e:
            logging.error(f"처리 상태 업데이트 실패: {str(e)}")

    def get_unprocessed_prompts(self) -> List[Dict[str, Any]]:
        """처리되지 않은 프롬프트만 반환"""
        all_prompts = self.get_prompts_from_excel()
        unprocessed = [prompt for prompt in all_prompts if not prompt.get('processed', False)]

        logging.info(f"처리되지 않은 프롬프트: {len(unprocessed)}개")
        return unprocessed

    def combine_prompt_elements(self, prompt_data: Dict[str, str]) -> str:
        """프롬프트 요소들을 조합하여 완전한 프롬프트 생성"""
        elements = []

        base_prompt = prompt_data.get('prompt', '').strip()
        style = prompt_data.get('style', '').strip()
        scene = prompt_data.get('scene', '').strip()
        resolution = prompt_data.get('resolution', '').strip()

        # 기본 프롬프트를 먼저 추가
        if base_prompt:
            elements.append(base_prompt)

        # 스타일 추가 (중복 방지)
        if style and style.lower() not in base_prompt.lower():
            elements.append(f"in {style} style")

        # 장면 추가 (중복 방지)
        if scene and scene.lower() not in base_prompt.lower():
            elements.append(f"scene: {scene}")

        # 해상도 추가
        if resolution:
            resolution_keywords = ['4k', '8k', 'hd', 'ultra', 'high', 'quality']
            if any(keyword in resolution.lower() for keyword in resolution_keywords):
                elements.append(f"{resolution} quality")
            elif 'x' in resolution.lower():  # 1920x1080 형태
                elements.append(f"resolution {resolution}")
            else:
                elements.append(f"{resolution} resolution")

        # 요소들을 자연스럽게 조합
        full_prompt = ", ".join(elements)

        logging.debug(f"조합된 프롬프트: {full_prompt}")
        return full_prompt

    def add_result_column(self, results: List[Dict[str, Any]]):
        """결과를 Excel 파일에 추가"""
        try:
            df = pd.read_excel(self.excel_path)

            # 결과 컬럼들 추가
            if 'download_count' not in df.columns:
                df['download_count'] = 0
            if 'download_time' not in df.columns:
                df['download_time'] = ''
            if 'status' not in df.columns:
                df['status'] = ''

            # 결과 업데이트
            for i, result in enumerate(results):
                if i < len(df):
                    df.at[i, 'download_count'] = result.get('download_count', 0)
                    df.at[i, 'download_time'] = result.get('download_time', '')
                    df.at[i, 'status'] = result.get('status', '')

            # 파일 저장
            df.to_excel(self.excel_path, index=False)
            logging.info("결과가 Excel 파일에 저장되었습니다.")

        except Exception as e:
            logging.error(f"결과 저장 실패: {str(e)}")