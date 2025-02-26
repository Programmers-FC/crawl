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

options = webdriver.ChromeOptions()
options.add_argument("--headless")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)

url = "https://fconline.nexon.com/datacenter/rank"
driver.get(url)

def safe_find_text(element, by, selector):
    try:
        return element.find_element(by, selector).text
    except NoSuchElementException:
        return ""

def crawl_page():
    tbody_xpath = '/html/body/div[2]/main/div/div/div[6]/div/div[1]/div/div[2]'
    page_data = []

    rows_count = len(wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.tbody div.tr'))))

    for idx in range(rows_count):
        retries = 0
        while retries < 3:
            try:
                tbody = wait.until(EC.presence_of_element_located((By.XPATH, tbody_xpath)))
                rows = tbody.find_elements(By.CLASS_NAME, 'tr')
                row = rows[idx]

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

current_page = 1
end_page = 500

while current_page <= end_page:
    print(f"{current_page} 페이지 크롤링 중...")
    page_data = crawl_page()
    all_data.extend(page_data)

    try:
        if current_page % 10 == 0 and current_page != end_page:
            next_btn_xpath = '//a[@class="btn_next_list ajaxNav"]'
            next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, next_btn_xpath)))
            ActionChains(driver).move_to_element(next_btn).click().perform()
            time.sleep(1)

        elif current_page % 10 == 1 and current_page != 1:
            pass

        elif current_page != end_page:
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
