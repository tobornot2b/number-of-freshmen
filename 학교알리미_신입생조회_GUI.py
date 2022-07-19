#!/usr/bin/env python
# coding: utf-8


import requests
import pandas as pd
import sys
from datetime import datetime
from gooey import Gooey, GooeyParser
import warnings
warnings.filterwarnings(action='ignore') # 경고메시지 무시
import os

today = datetime.today().strftime("%Y%m%d")

@Gooey(program_name='학교알리미 신입생 수 받아오기',
       program_description='학교알리미 API 에서 신입생 수를 받아오는 프로그램 입니다.',
       default_size=(600, 500),
       progress_regex=r"^Progress (\d+)$",
       show_restart_button = False,
       language='korean'
      )

def get_args() -> None:
    parser = GooeyParser(description='신입생 수 받아오기')
    num_of_student = parser.add_argument_group('')
    
    num_of_student.add_argument('year',
                              metavar='공시연도',
                              help='최근 3년간의 정보만 제공',
                              widget="Dropdown",
                              choices=[str(i + int(today[:4])) for i in range(0, -3, -1)],
                              default='2022'
                             )
    num_of_student.add_argument('sch_code',
                              metavar='학교급구분',
                              help='03:중등 04:고등',
                              widget="Dropdown",
                              choices=['03', '04'],
                              default='03'
                             )

    args = parser.parse_args()
    
    get_students(args.year, args.sch_code)


# 학생수 받아오기
def get_students(year: str, sch_kind: str) -> None:
    url = 'http://www.schoolinfo.go.kr/openApi.do'
    apiType = "?apiType=63" # API 종류 (성별 학생수)
    year = '&pbanYr=' + year
    sch_kind = '&schulKndCode=' + sch_kind

    print('>> URL 및 파라메터 조립, 인증 안함')
    print('현재 작업폴더 :', os.getcwd())
    print(url + apiType + year + sch_kind + '&API_KEY')
    print()

    # 키 가져오기
    sys.path.append('/settings')
    import config
    apiKey = config.API_Keys['school_info_Key']
    
    # URL 및 파라메터 조립, 인증 안함
    get_data = requests.get(url + apiType + year + sch_kind + apiKey, verify=False) # verify=False 없으면 ssl 인증에러남
    
    result_data = get_data.json()
    
    df = pd.json_normalize(result_data['list'])
    
    df['년도'] = year[-4:]
    
    # 원하는 열만 뽑아내기
    df = df[['년도',
             'ADRCD_NM', # 지역
             'SCHUL_NM', # 학교명
             'COL_M1', # 1학년(남)
             'COL_W1' # 1학년(여)
            ]]
    
    # 열이름 한글변경
    df.columns = ['년도', '지역', '학교명', '1학년(남)', '1학년(여)']
    
    print('>> 가져온 데이터프레임 출력')
    print()
    print(df)
    print()

    make_excel(sch_kind[-2:], df)

    
def make_excel(sch_kind: str, df: pd.DataFrame) -> None:
    if sch_kind == '03':
        df.to_excel('중1_학생수.xlsx', sheet_name='중학교', index=False)
        print('중학교 신입생 수를 기록중입니다.')
        print(f'{df.shape[0]} 행 {df.shape[1]} 열을 기록합니다.')
        print()
        print('고등학교 학생수는 "편집" 버튼 클릭 -> 학교급구분 "04" 설정 후 다시 실행해주세요.')
        print('작업이 완료되었습니다.')
        print()
    elif sch_kind == '04':
        df.to_excel('고1_학생수.xlsx', sheet_name='고등학교', index=False)
        print('고등학교 신입생 수를 기록중입니다.')
        print(f'{df.shape[0]} 행 {df.shape[1]} 열을 기록합니다.')
        print()
        print('중학교 학생수는 "편집" 버튼 클릭 -> 학교급구분 "03" 설정 후 다시 실행해주세요.')
        print('작업이 완료되었습니다.')
        print()


if __name__ == "__main__": 
    get_args()
