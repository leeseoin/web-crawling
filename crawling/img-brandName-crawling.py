# selenium의 webdriver를 사용하기 위한 import
from selenium import webdriver
# selenium으로 키를 조작하기 위한 import
from selenium.webdriver.common.keys import Keys
# 4.0 selenium부터는 xpath 메서드를 직접적으로 사용이 안된다고 한다
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
# 페이지 로딩을 기다리는데에 사용할 time 모듈 import
import time
# csv 파일을 위한 모듈 import
import os
import csv

# 이미지 저장용 폴더 경로 지정
images_storage_folder_path = r'/Users/seoin/Desktop/img-brandName/'

# 해당 경로에 폴더가 없을시 새로운 폴더 생성
if not os.path.isdir(images_storage_folder_path):
    os.mkdir(images_storage_folder_path)

# CSV 파일 경로 지정
csv_file_path = os.path.join(images_storage_folder_path, 'products.csv')

# 크롬드라이버 실행
driver = webdriver.Chrome()
# 크롬 드라이버에 url 주소 넣고 실행
driver.get('https://www.shopcider.com/product/list?collection_id=113716&link_url=https%3A%2F%2Fwww.shopcider.com%2Fproduct%2Flist%3Fcollection_id%3D113716&operationpage_title=product_detail&operation_position=4-3-1-5&operation_type=category&operation_content=%EB%8D%B0%EB%8B%98%20%EC%A0%90%ED%94%84%EC%88%98%ED%8A%B8%20%26%20%EB%A1%AC%ED%8D%BC&operation_image=&operation_update_time=1714111617563&listSource=product_detail-denim-floral-buckle-pocket-romper-1036565%3Bcollection_113716%3B4-3-1-5')
# 창 최대로 늘리기
driver.maximize_window()
# shopcider 사이트에 접속 후 완전히 로딩 될때까지 2초 대기
time.sleep(2)

# 스크롤 최근 값이라고 보면 됨. 초기 값이라 0으로 지정해놓은 거임
old_scroll_location = 0

# 스크롤 시도 횟수 제한을 위해 설정
scroll_attempts = 1000000
attempt_count = 0

while attempt_count < scroll_attempts:
    # 현재 스크롤 위치
    new_scroll_location = driver.execute_script("return document.body.scrollHeight")

    # 스크롤 위치가 변경되었는지 확인
    if new_scroll_location != old_scroll_location:
        # 스크롤 위치 업데이트
        old_scroll_location = new_scroll_location
    else:
        # 새롭게 로드된 제품 이름 목록
        product_names = driver.find_elements(By.CLASS_NAME, "product-item-name.text-ellipsis")
        
        # 새롭게 로드된 제품 이미지 목록
        product_images = driver.find_elements(By.CLASS_NAME, "cider-image.hover-second-image.percent")

        # 각 제품 이름과 이미지 URL을 매핑하기 위해 리스트 형식으로 저장함
        product_name_texts = [product_name.text for product_name in product_names]
        images_thumbnail = [product_image.get_attribute('data-img') for product_image in product_images]

        # 제품 이름과 이미지 URL을 짝지어 저장
        products = zip(product_name_texts, images_thumbnail)
        
        # CSV 파일 생성 및 헤더 작성
        with open(csv_file_path, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow(['No', '브랜드명', '이미지 URL'])

            # 제품 이름 CSV에 저장 및 이미지 다운로드 될 때마다 어떤 이미지가 다운되었는데 터미널에 출력해줌
            for index, (name, image_url) in enumerate(products, start=1):
                print(f"No.{index} 브랜드명: {name}")
                
                # 해당 경로 폴더에 브랜드 명+.jpg형태로 저장함
                file_path = os.path.join(images_storage_folder_path, f'{name}.jpg')
                
                # SSL 인증서 검증 무시
                import ssl
                from urllib.request import urlretrieve
                ssl._create_default_https_context = ssl._create_unverified_context

                # 이미지 다운로드(성공하면 성공 여부 확인용) -> 터미널에서 확인용
                try:
                    urlretrieve(image_url, file_path)
                    print(f"이미지 저장: {file_path}")
                except Exception as e:
                    print(f"이미지 저장 실패: {file_path}, 에러: {e}")
                
                # CSV 파일에 작성
                writer.writerow([index, name, image_url])
                
                time.sleep(0.4)

        # 루프 종료
        break

    # 스크롤 내리기
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    
    # 스크롤 내리고 1초 대기
    time.sleep(1.5)
    attempt_count += 1

# 드라이버 종료하지 않고 유지
driver.quit() 
