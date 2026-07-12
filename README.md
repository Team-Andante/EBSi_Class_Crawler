# EBSi_Class__Crawler

<p>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white">
  <img alt="Selenium" src="https://img.shields.io/badge/Selenium-4-43B02A?logo=selenium&logoColor=white">
  <img alt="BeautifulSoup4" src="https://img.shields.io/badge/BeautifulSoup-4-orange">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green.svg">
</p>

**[EBSi(EBS 고교강의)](https://www.ebsi.co.kr)** 사이트의 강좌 목록을 학년·과목별로 자동 수집하여 CSV 파일로 저장하는 Python 크롤러입니다. Selenium으로 동적 페이지를 렌더링하고 BeautifulSoup으로 강좌명, 강사, 강좌구분, 난이도, 상세 링크를 추출합니다.

> 이 크롤러로 수집한 데이터는 Team Andante의 교육 지원 서비스 **[COMPASS](https://github.com/Team-Andante/COMPASS)**의 EBS 강좌 추천 기능에 활용됩니다.

## 주요 기능

- 🎓 **학년별 크롤링** — 실행 시 터미널 입력으로 고1 / 고2 / 고3 중 선택
- 📚 **과목 자동 순회** — 국어·영어·수학·과학·사회 등 학년별 전 과목을 카테고리 코드 기준으로 순회
- 🤖 **Selenium 기반 동적 렌더링 처리** — `webdriver-manager`가 ChromeDriver를 자동으로 설치하고, headless Chrome으로 페이지가 로드될 때까지 대기 후 파싱
- 🔍 **BeautifulSoup 파싱** — 강좌명, 강사명, 강좌구분, 난이도, 상세페이지 링크를 각 강좌 카드(`.cont_wrap`)에서 추출
- 💾 **CSV 저장** — `utf-8-sig` 인코딩으로 저장되어 엑셀에서 한글이 깨지지 않고 바로 열람 가능
- 📄 **페이지네이션 자동 처리** — 과목별로 지정된 페이지 수만큼 순회하며, 더 이상 강좌가 없으면 조기 종료

## 결과물 예시

| 과목 | 강좌명 | 강사 | 강좌구분 | 난이도 | 링크 |
| --- | --- | --- | --- | --- | --- |
| 국어 | [올림포스] 독서와 작문 (2022 개정) | 차해나 | 개념완성 | 기본 | ebsi.co.kr/... |
| 국어 | [올림포스] 화법과 언어 (2022 개정) | 김상태 | 개념완성 | 기본 | ebsi.co.kr/... |

## 시작하기

### 요구 사항

- Google Chrome 브라우저 (로컬에 설치되어 있어야 합니다)
- Python 3 (별도 최소 버전 명시는 없으나 최신 3.x 버전 권장)

### 설치

```bash
git clone https://github.com/Team-Andante/EBSi_Class_Crawler.git
cd EBSi_Class_Crawler
pip install beautifulsoup4 selenium webdriver-manager
```

### 실행

```bash
python class_crawler.py
```

실행하면 아래와 같이 학년을 물어봅니다. `1`, `2`, `3` 중 하나를 입력해 주세요 (그 외의 값을 입력하면 과목 목록이 설정되지 않아 오류가 발생합니다).

```
크롤링할 학년을 선택해주세요. (1: 고1, 2: 고2, 3: 고3) 2
```

선택한 학년의 전 과목 크롤링이 끝나면 스크립트를 실행한 위치에 CSV 파일이 생성됩니다.

## 학년별 수집 과목

크롤링 대상은 EBSi의 과목 카테고리 코드와 학년별 강좌 목록 페이지 수를 기준으로 미리 정의되어 있습니다.

<details>
<summary><b>고1 (high1)</b></summary>

| 과목 | 카테고리 코드 | 수집 페이지 수 |
| --- | --- | --- |
| 국어 | B100 | 7 |
| 영어 | B200 | 7 |
| 수학 | B300 | 7 |
| 과학 | B500 | 2 |
| 사회 | B400 | 2 |
| 한국사 | B800 | 2 |

</details>

<details>
<summary><b>고2 (high2)</b></summary>

| 과목 | 카테고리 코드 | 수집 페이지 수 |
| --- | --- | --- |
| 국어 | B100 | 6 |
| 영어 | B200 | 6 |
| 수학 | B300 | 8 |
| 과학 | B500 | 3 |
| 사회 | B400 | 4 |
| 한국사 | B800 | 1 |
| 일반/진로/교양 | B900 | 1 |

</details>

<details>
<summary><b>고3 (high3)</b></summary>

| 과목 | 카테고리 코드 | 수집 페이지 수 |
| --- | --- | --- |
| 국어 | A100 | 16 |
| 영어 | A200 | 14 |
| 수학 | A300 | 19 |
| 과학 | A400 | 25 |
| 사회 | A500 | 24 |
| 직업 | A600 | 3 |
| 제2외국어 | A700 | 5 |
| 한국사 | A800 | 4 |
| 일반/진로/교양 | A900 | 1 |

</details>

## 동작 방식

1. **`init_set()`** — 입력받은 학년에 따라 `GRADE` 값과 과목별 카테고리 코드·페이지 수(`SUBJECTS`)를 설정합니다.
2. **`init_driver()`** — `webdriver-manager`로 ChromeDriver를 준비하고 headless 모드의 Chrome을 실행합니다.
3. **`crawl_subject()`** — `retrieveSbjtListByArea.ebs` 엔드포인트에 과목 코드·학년·페이지 번호를 파라미터로 붙여 접속하고, `.cont_wrap` 요소가 로드될 때까지 최대 10초 대기합니다.
4. **`parse_page()`** — BeautifulSoup으로 강좌 카드에서 강좌명/링크(`.tit a`), 강사명(`.detail_info span`), 강좌구분·난이도(`.flag_ro_col2`, `.flag_ro_col3`)를 추출합니다.
5. 모든 과목의 크롤링이 끝나면 결과를 `[과목, 강좌명, 강사, 강좌구분, 난이도, 링크]` 형식으로 CSV에 저장합니다.

## 참고 사항

- 결과 파일명은 현재 `ebs_high2_data.csv`로 고정되어 있습니다. 고1·고3 데이터를 크롤링한 경우에도 동일한 이름으로 저장되므로, 필요하다면 실행 후 파일명을 직접 변경하거나 `main()`의 `filename` 값을 수정해서 사용해 주세요.
- EBSi 페이지의 HTML 구조가 바뀌면 CSS 선택자(`.cont_wrap`, `.tit a` 등)가 더 이상 맞지 않아 크롤링이 정상 동작하지 않을 수 있습니다.
- 학습·개인 용도로 제작된 크롤러입니다. 과도한 요청으로 서버에 부담을 주지 않도록 유의하고, EBSi 이용약관을 준수해 주세요.

## License

이 프로젝트는 [MIT License](./LICENSE)를 따릅니다.
Copyright (c) 2026 Team Andante | ASAP (gmstghost)
