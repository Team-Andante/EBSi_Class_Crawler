### EBSi Class Crawler
# Version 2.0

### Patch note
# 학년 터미널로 선택 가능

import csv
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

BASE = "https://www.ebsi.co.kr"

# 기본설정
def init_set():
    global GRADE, SUBJECTS
    res = int(input("크롤링할 학년을 선택해주세요. (1: 고1, 2: 고2, 3: 고3)"))

    if res == 1:
        # 고1
        GRADE = "high1" 
        SUBJECTS = {
            "국어":           ["B100", 7],
            "영어":           ["B200", 7],
            "수학":           ["B300", 7],
            "과학":           ["B500", 2],
            "사회":           ["B400", 2],
            "한국사":         ["B800", 2],
    }
        
    if res == 2:
    # 고2
        GRADE = "high2" 
        SUBJECTS = {
            "국어":           ["B100", 6],
            "영어":           ["B200", 6],
            "수학":           ["B300", 8],
            "과학":           ["B500", 3],
            "사회":           ["B400", 4],
            "한국사":         ["B800", 1],
            "일반/진로/교양": ["B900", 1],
        }

    if res == 3:
        # 고3
        GRADE = "high3" 
        SUBJECTS = {
            "국어":           ["A100", 16],
            "영어":           ["A200", 14],
            "수학":           ["A300", 19],
            "과학":           ["A400", 25],
            "사회":           ["A500", 24],
            "직업":           ["A600", 3],
            "제2외국어":      ["A700", 5],
            "한국사":         ["A800", 4],
            "일반/진로/교양": ["A900", 1],
        }

# Chrome 드라이버 초기화
def init_driver(headless=True):
    opts = Options()                                # Chrome 옵션 객체
    if headless: opts.add_argument("--headless")    # headless=True면 브라우저 창 숨김
    opts.add_argument("--window-size=1920,1080")    # 가상 브라우저 창 크기

   # ChromeDriver 자동 설치 후 Chrome 브라우저 드라이버 반환
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)

# 강좌정보 파싱
def parse_page(html, subject_name):
    soup = BeautifulSoup(html, "html.parser")       # HTML을 BeautifulSoup 객체로 파싱
    rows = []                                       # 결과 저장 리스트
    items = soup.select(".cont_wrap")               # 강좌 카드에 해당하는 모든 .cont_wrap 요소
    
    for item in items:
        # 1. 강좌명 및 링크
        title_el = item.select_one(".tit a")        # 강좌명 링크 태그
        if not title_el: continue
        
        name = title_el.get_text(strip=True)        # 강좌명 추출
        link = title_el.get("href", "")             # URL 추출

        # 상대경로인 경우 절대경로로 변환
        if not link.startswith("http"): 
            link = BASE + link
            
        # 2. 강사명 추출 (detail_info의 2번째 span 태그)
        teacher = ""
        detail_spans = item.select(".detail_info span")     # 상세 정보 span 태그 모두

        if len(detail_spans) >= 2:
            teacher = detail_spans[1].get_text(strip=True)  # 두 번째 span
        
        # 3. 플래그 정보 (flag_ro_col2, flag_ro_col3)
        col2 = item.select_one(".flag_ro_col2")                 # 강좌구분 플래그
        flag2 = col2.get_text(strip=True) if col2 else ""       # 있으면 추출, 없으면 빈 문자열
        
        col3 = item.select_one(".flag_ro_col3")                 # 난이도 플래그
        flag3 = col3.get_text(strip=True) if col3 else ""       # 있으면 추출, 없으면 빈 문자열
        
        # [과목명, 강좌명, 강사, 강좌구분, 난이도, 링크]
        rows.append([subject_name, name, teacher, flag2, flag3, link])
    
    return rows

# 과목 페이지 파싱
def crawl_subject(driver, name, info):
    code, max_page = info       # info 리스트 분리
    base_url = f"{BASE}/ebs/pot/potn/retrieveSbjtListByArea.ebs?categoryCode={code}&cookieGradeVal={GRADE}"
    
    print(f"▶ [{GRADE}] {name} 시작 (지정 페이지: {max_page})")
    all_rows = []               # 과목 데이터용 리스트

    for page in range(1, max_page + 1):
        target_url = f"{base_url}&pageIndex={page}"     # 타깃 URL 지정
        driver.get(target_url)                          # 페이지 로드
        
        try:
            # 동적 렌더링 처리 (10초 대기)
            WebDriverWait(driver, 10).until(
                # .cont_wrap 요소가 나타날 때까지 대기
                EC.presence_of_element_located((By.CSS_SELECTOR, ".cont_wrap"))
            )
            time.sleep(0.7) 
            
            page_rows = parse_page(driver.page_source, name)        # 현재페이지 파싱
            if not page_rows: break                                 # 마지막페이지에서 루프 종료
                
            all_rows.extend(page_rows)                              # 현재페이지 데이터 추가
            print(f"  {page}/{max_page} 페이지 완료")
            
        # 예외발생 시 중단
        except Exception:
            break

    return all_rows

def main():
    init_set()      # 초기설정

    driver = init_driver(headless=True)     # Chrome 드라이버 초기화
    final_data = []

    try:
        # 과목 순회 파싱
        for name, info in SUBJECTS.items():     
            final_data.extend(crawl_subject(driver, name, info))
            
        filename = "ebs_high2_data.csv"     # 파일명 지정
        
        # 파일 열기
        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["과목", "강좌명", "강사", "강좌구분", "난이도", "링크"])       # 헤더 행 작성
            writer.writerows(final_data)        # 나머지 데이터 일괄 작성
        
        print(f"\n✅ 완료! 총 {len(final_data)}개 데이터가 {filename}에 저장되었습니다.")

    finally:
        driver.quit()       # 브라우저 드라이버 종료

if __name__ == "__main__":
    main()