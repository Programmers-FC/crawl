import csv
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# 크롬 옵션 설정 (--headless == 백그라운드 실행)
options = webdriver.ChromeOptions()
# options.add_argument("--headless")

# 크롬 드라이버 실행
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)

url = "https://fconline.nexon.com/datacenter/rank"
driver.get(url)

# ✅ 팝업이 있으면 닫기
try:
    close_button = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="wrapper"]/div[1]/a'))
    )
    close_button.click()
    print("팝업 닫음")
except:
    print("팝업 없음")

def safe_find_text(element, by, selector):
    """
    특정 HTML 요소에서 텍스트를 안전하게 추출하는 함수
    요소가 없을 경우 예외 처리하여 빈 문자열 반환
    """
    try:
        return element.find_element(by, selector).text
    except NoSuchElementException:
        return ""

def crawl_page():
    """
    현재 페이지에서 유저 정보를 크롤링하는 함수
    - 각 유저 정보를 리스트에 저장하여 반환
    """
        
    tbody_xpath = '//div[@class="tbody"]'
    page_data = []

    # 현재 페이지에서 랭킹 리스트 개수 가져오기
    rows_count = len(wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.tbody div.tr'))))

    for idx in range(rows_count):
        retries = 0
        while retries < 3:
            try:
                tbody = wait.until(EC.presence_of_element_located((By.XPATH, tbody_xpath)))
                rows = tbody.find_elements(By.CLASS_NAME, 'tr')
                row = rows[idx]

                # 각 유저 정보 크롤링
                rank_no = safe_find_text(row, By.CLASS_NAME, 'rank_no')
                coach_name = safe_find_text(row, By.CSS_SELECTOR, 'span.name.profile_pointer')
                coach_level = safe_find_text(row, By.CSS_SELECTOR, 'span.lv .txt')
                team_value = safe_find_text(row, By.CLASS_NAME, 'price')
                win_point = safe_find_text(row, By.CLASS_NAME, 'rank_r_win_point')
                win_rate = safe_find_text(row, By.CSS_SELECTOR, 'span.rank_before span.top')
                record = safe_find_text(row, By.CSS_SELECTOR, 'span.rank_before span.bottom')
                team_names_elements = row.find_elements(By.CSS_SELECTOR, 'span.team_color span.inner')
                team_names = "|".join([t.text for t in team_names_elements]) if team_names_elements else ""
                formation = safe_find_text(row, By.CLASS_NAME, 'formation')

                # 고유번호 data-sn 추출 추가
                try:
                    unique_id = row.find_element(By.CSS_SELECTOR, 'span.name.profile_pointer').get_attribute('data-sn')
                except NoSuchElementException:
                    unique_id = ""

                # rank 이미지 번호 추출 추가
                try:
                    img_url = row.find_element(By.CSS_SELECTOR, 'span.ico_rank img').get_attribute('src')
                    rank_match = re.search(r'ico_rank(\d+)\.png', img_url)
                    rank_num = rank_match.group(1) if rank_match else ''
                except NoSuchElementException:
                    rank_num = ''

                # 데이터 저장 (rank_no이 있는 경우)
                if rank_no:
                    data = [
                        rank_no, coach_name, unique_id, rank_num, coach_level,
                        team_value, win_point, win_rate, record, team_names, formation
                    ]
                    page_data.append(data)
                break

            except StaleElementReferenceException:
                retries += 1
                time.sleep(1)
                continue

    return page_data

all_data = []

# 1~500 페이지까지 크롤링
current_page = 1
end_page = 500

while current_page <= end_page:
    print(f"{current_page} 페이지 크롤링 중...")
    # 현재 페이지 크롤링
    page_data = crawl_page()
    all_data.extend(page_data)

    try:
        if current_page % 10 == 0 and current_page != end_page:
            # 10페이지 단위마다 다음 버튼 클릭
            next_btn_xpath = '//a[@class="btn_next_list ajaxNav"]'
            next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, next_btn_xpath)))
            ActionChains(driver).move_to_element(next_btn).click().perform()
            time.sleep(1)

        elif current_page % 10 == 1 and current_page != 1:
            pass

        elif current_page != end_page:
            # current_page에 해당하는 버튼 클릭
            page_btn_num = current_page + 1
            page_xpath = f'//a[@onclick="goSearchDetail({page_btn_num},false);"]'
            page_btn = wait.until(EC.element_to_be_clickable((By.XPATH, page_xpath)))
            ActionChains(driver).move_to_element(page_btn).click().perform()
            time.sleep(1)

    except Exception as e:
        print(f"{current_page} 페이지 이동 중 에러: {e}, 재시도 중...")
        time.sleep(1)
        continue

    current_page += 1

header = ['순위', '감독명', '고유번호', '랭크번호', '레벨', '팀 가치', '승점', '승률', '전적', '팀 이름', '포메이션']

with open('crawl_result.csv', 'w', encoding='utf-8-sig', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header)
    writer.writerows(all_data)

print("모든 데이터 크롤링 완료: crawl_result.csv")

driver.quit()