import os
import csv
import time
import ssl
from urllib.request import urlretrieve
from selenium import webdriver
from selenium.webdriver.common.by import By

# 경로 설정
images_storage_folder_path = r'/Users/seoin/Desktop/cider_crawling/'
csv_file_path = os.path.join(images_storage_folder_path, 'cider.csv')

# 폴더가 없으면 생성
if not os.path.isdir(images_storage_folder_path):
    os.mkdir(images_storage_folder_path)

# 크롬드라이버 실행
driver = webdriver.Chrome()
driver.maximize_window()

# 첫 번째 단계: 브랜드명, 이미지 URL 추출 및 이미지 다운로드
driver.get('example.com')

# 스크롤을 통해 페이지 로드
scroll_attempts = 100
old_scroll_location = 0

for _ in range(scroll_attempts):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(1.5)
    new_scroll_location = driver.execute_script("return document.body.scrollHeight")
    if new_scroll_location == old_scroll_location:
        break
    old_scroll_location = new_scroll_location

# 제품 이름 및 이미지 URL, 상세 페이지 URL 추출
product_names = driver.find_elements(By.CLASS_NAME, "product-item-name")
product_images = driver.find_elements(By.CLASS_NAME, "cider-image.hover-second-image")
product_links = driver.find_elements(By.CSS_SELECTOR, '.product-image-group .product-image-item.show a.cider-link')

product_info = []
for name, img, link in zip(product_names, product_images, product_links):
    product_name = name.text
    image_url = img.get_attribute('data-img')
    product_url = link.get_attribute('href')
    product_info.append({'product_name': product_name, 'image_url': image_url, 'product_url': product_url})

# 이미지 다운로드 및 초기 CSV 파일 작성
with open(csv_file_path, mode='w', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    writer.writerow(['No', '브랜드명', '색', '제품 상세사항', '이미지 URL'])
    ssl._create_default_https_context = ssl._create_unverified_context
    for idx, product in enumerate(product_info, start=1):
        image_path = os.path.join(images_storage_folder_path, f"{product['product_name']}.jpg")
        try:
            urlretrieve(product['image_url'], image_path)
            image_status = "다운로드 성공"
        except Exception as e:
            image_status = f"다운로드 실패: {e}"
        print(f"No: {idx}, 브랜드명: {product['product_name']}, 이미지 URL: {product['image_url']}, 이미지 다운로드: {image_status}")
        writer.writerow([idx, product['product_name'], '', '', product['image_url']])

# 두 번째 단계: 제품 상세 페이지에서 색상 및 상세사항 추출
def click_color_box(color_index):
    time.sleep(2)
    color_boxes = driver.find_elements(By.CSS_SELECTOR, '.style-selct-item-contaienr')
    color_boxes[color_index].click()

for idx, product in enumerate(product_info, start=1):
    driver.get(product['product_url'])
    time.sleep(2)

    product_name = product['product_name']

    # 색상 정보 추출
    colors = []
    color_boxes_count = len(driver.find_elements(By.CSS_SELECTOR, '.type-container .style-selct-item-contaienr'))
    for color_index in range(color_boxes_count):
        click_color_box(color_index)
        time.sleep(1)
        color_elements = driver.find_elements(By.CSS_SELECTOR, ".description-wrapper")
        colors.extend([elem.text.split('/')[0] for elem in color_elements])

    # 상세사항 정보 추출
    accordion_elements = driver.find_elements(By.CSS_SELECTOR, ".accordion-title .desc-accordion-title")
    for accordion_element in accordion_elements:
        if accordion_element.text == "제품 상세사항":
            accordion_element.click()
            break

    time.sleep(1)
    accordion_wrap = driver.find_element(By.CLASS_NAME, 'desc-accordion-wrap')
    sections = accordion_wrap.find_elements(By.XPATH, './/div[contains(@class, "item-container")]')

    details = []
    for section in sections:
        title = section.find_element(By.CLASS_NAME, 'item-title').text
        items = section.find_elements(By.CLASS_NAME, 'item-li')
        item_texts = [item.text for item in items]
        details.append(title + " > " + " / ".join(item_texts))

    product_details = " | ".join(details)
    product['colors'] = colors
    product['details'] = product_details
    print(f"No: {idx}, 브랜드명: {product_name}, 색상: {colors}, 상세사항: {product_details}")

# 최종 CSV 파일 작성
with open(csv_file_path, mode='w', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    writer.writerow(['No', '브랜드명', '색', '제품 상세사항', '이미지 URL'])
    for idx, product in enumerate(product_info, start=1):
        writer.writerow([idx, product['product_name'], ', '.join(product.get('colors', [])), product.get('details', ''), product['image_url']])

# 드라이버 종료
driver.quit()
