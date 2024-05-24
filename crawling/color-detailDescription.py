from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import csv

# 제품 색과 상세 설명 저장할 경로
images_storage_folder_path = r'/Users/seoin/Desktop/color_and_description/'

# 해당 경로에 폴더가 없을 시 새로운 폴더 생성
if not os.path.isdir(images_storage_folder_path):
    os.mkdir(images_storage_folder_path)

# CSV 파일 경로 지정
csv_file_path = os.path.join(images_storage_folder_path, 'colorAndDescription.csv')



# 크롬드라이버 실행
driver = webdriver.Chrome()

# 크롬 드라이버에 URL 주소 넣고 실행 
driver.get('https://www.shopcider.com/product/list?collection_id=113716&link_url=https%3A%2F%2Fwww.shopcider.com%2Fproduct%2Flist%3Fcollection_id%3D113716&operationpage_title=product_detail&operation_position=4-3-1-5&operation_type=category&operation_content=%EB%8D%B0%EB%8B%98%20%EC%A0%90%ED%94%84%EC%88%98%ED%8A%B8%20%26%20%EB%A1%AC%ED%8D%BC&operation_image=&operation_update_time=1714111617563&listSource=product_detail-denim-floral-buckle-pocket-romper-1036565%3Bcollection_113716%3B4-3-1-5')

# 창 크기 고정
driver.maximize_window()
# 사이트에 접속 후 완전히 로딩 될 때까지 2초 대기
time.sleep(2)

# 스크롤 최근 값. 초기 값이라 0으로 지정
old_scroll_location = 0

# 스크롤 시도 횟수 제한을 위해 설정
scroll_attempts = 100
attempt_count = 0

# 제품 정보 저장을 위한 리스트 초기화
product_info_list = []

# 색상 선택 상자 클릭 함수 정의
def click_color_box(color_index):
    time.sleep(2)
    color_boxes = driver.find_elements(By.CSS_SELECTOR, '.style-selct-item-contaienr')
    color_boxes[color_index].click()
    
while attempt_count < scroll_attempts:
    # 스크롤 내리기
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    # 스크롤 내리고 1.5초 대기
    time.sleep(1.5)
    attempt_count += 1
    
    # 현재 스크롤 위치
    new_scroll_location = driver.execute_script("return document.body.scrollHeight")

    # 스크롤 위치가 변경되었는지 확인
    if new_scroll_location != old_scroll_location:
        # 스크롤 위치 업데이트
        old_scroll_location = new_scroll_location
    else:
        # 제품에 해당하는 상세 설명 페이지 URL을 가지고 있는 HTML 요소 지정
        element_urls = driver.find_elements(By.CSS_SELECTOR, '.product-image-group .product-image-item.show a.cider-link')
        # HTML 요소 지정한 것 중에서 href만 뽑아내기 위한 작업
        element_url_href = [element_url.get_attribute('href') for element_url in element_urls]

        for url in element_url_href:
            # 새 창에서 페이지 열기
            driver.execute_script("window.open('{}', '_blank');".format(url))
            
            # 새로 열린 창으로 전환
            driver.switch_to.window(driver.window_handles[-1])
            
            # 페이지 로딩 대기
            time.sleep(2)
    
            # 제품 이름 추출
            product_name_element = driver.find_element(By.CSS_SELECTOR, '.product-detail-info .product-detail-title')
            product_name = product_name_element.text

            # 색상 선택 상자 클릭 및 색상 정보 추출
            color_boxes_count = len(driver.find_elements(By.CSS_SELECTOR, '.type-container .style-selct-item-contaienr'))
            colors = []
            for color_index in range(color_boxes_count):
                # 색상 선택 상자 클릭
                click_color_box(color_index)
                time.sleep(1)  # 선택 상자가 변경될 때까지 대기
                
                # 색상 정보 추출
                color_elements = driver.find_elements(By.CSS_SELECTOR, ".description-wrapper")
                colors.extend([elem.text.split('/')[0] for elem in color_elements])
            
            # 제품 상세사항 클릭
            accordion_elements = driver.find_elements(By.CSS_SELECTOR, ".accordion-title .desc-accordion-title")
            for accordion_element in accordion_elements:
                if accordion_element.text == "제품 상세사항":
                    accordion_element.click()
                    break

            # 제품 상세사항 내용 가져오기
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
            
            # 제품 정보 저장
            a = {'product_name': product_name, 'colors': colors, 'details': product_details}
            product_info_list.append(a)
            print(a, len(product_info_list))
            # 현재 창 닫기 (원래 페이지로 돌아가기 위해)
            driver.close()
    
            # 이전 창으로 전환
            driver.switch_to.window(driver.window_handles[0])

            # 원래 페이지로 돌아가기 위해 대기
            time.sleep(0.5)
            # 마지막 URL에 도달하면 루프 중단
            if url == element_url_href[-1]:
                attempt_count = scroll_attempts  # while 루프 종료 조건을 충족시킴
                break

# CSV 파일에 제품 정보 저장
with open(csv_file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
    fieldnames = ['No', '브랜드명', '색', '제품 상세사항']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for idx, product_info in enumerate(product_info_list, start=1):
        writer.writerow({
            'No': idx,
            '브랜드명': product_info['product_name'],
            '색': ', '.join(product_info['colors']),
            '제품 상세사항': product_info['details']
        })

# 드라이버 종료
driver.quit()
