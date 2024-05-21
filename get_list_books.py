import numpy as np
from selenium import webdriver
from time import sleep, time
from selenium.webdriver.common.keys import Keys
import random
from selenium.webdriver import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import json
from datetime import datetime

from webdriver_manager.opera import OperaDriverManager
from selenium.webdriver.chrome import service

webdriver_service = service.Service(OperaDriverManager().install())
webdriver_service.start()

options = webdriver.ChromeOptions()
options.add_experimental_option('w3c', True)

driver = webdriver.Remote(webdriver_service.service_url, options=options)
driver.get("opera://settings/?search=vpn")
sleep(30)

pd.set_option("display.max_columns", 8)
# Bắt đầu đo thời gian
start_time = time()
path=r"E:\python\work\BookRecommenderSystem\data_for_book_recommend_system\Books_That_Should_Be_Made_Into_Movies.csv"
linkListBook="https://www.goodreads.com/list/show/1043.Books_That_Should_Be_Made_Into_Movies"
# Declare browser
# driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
page = 22
while (page <= 100):
    try:
        print("================= Page {} =================".format(page))
        driver.get(f"{linkListBook}?page={page}")
        sleep(random.randint(1, 3))
        # get title and book id
        elems_title_bookId = driver.find_elements(By.CSS_SELECTOR, ".bookTitle")
        titles = [elem_title.text for elem_title in elems_title_bookId]
        links = []
        booksId = []
        for elem in elems_title_bookId:
            link = elem.get_attribute('href')
            links.append(link)
            booksId.append(re.search(r'\d+', link).group(0))

        # get author
        elems_author = driver.find_elements(By.CSS_SELECTOR, ".authorName__container .authorName span")
        authors = [elem.text for elem in elems_author]

        # get link img
        elems_img = driver.find_elements(By.CSS_SELECTOR, ".js-tooltipTrigger a .bookCover")
        imgs = [elem_img.get_attribute("src") for elem_img in elems_img]

        df1 = pd.DataFrame(list(zip(booksId, titles, links, authors, imgs)),
                           columns=['bookId', 'title', 'link', 'authors', 'img'])
        print("Done get basic information of book in page {}".format(page))
        print(df1)

        # access each link of a book and get details information
        df2 = pd.DataFrame(columns=['book_id', 'genres', 'average_rating', 'language', 'num_pages', 'ratings_count',
                                    'text_reviews_count', 'publication_date', 'publisher'])
        countBook = 0
        for link, book_id in zip(links, booksId):
            retries = 0
            while retries < 3:
                try:
                    driver.get(link)
                    sleep(random.randint(1, 2))

                    # genres và Đợi cho tất cả các phần tử xuất hiện trong 10 giây
                    elems_genres = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,
                                                                                                        ".BookPageMetadataSection__genres .CollapsableList .BookPageMetadataSection__genreButton .Button__labelItem")))
                    genres = [elem.text for elem in elems_genres]
                    genres_string = ', '.join(genres)

                    # get more details. Lấy ra json và Phân tích JSON
                    json_script_details_1 = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "/html/head/script[9]"))).get_attribute('innerHTML')
                    json_script_details_2 = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "/html/body/script[1]"))).get_attribute('innerHTML')
                    data_details_1 = json.loads(json_script_details_1)
                    data_details_2 = json.loads(json_script_details_2)
                    # Truy cập và in ra giá trị ratingCount, average_rating và text_reviews_count
                    aggregateRating = data_details_1.get("aggregateRating")
                    average_rating = aggregateRating.get("ratingValue")
                    ratings_count = aggregateRating.get("ratingCount")
                    text_reviews_count = aggregateRating.get("reviewCount")
                    # Phân tích sâu vào data_details_2 để lấy giá trị trong json
                    BookByLegacyId = data_details_2.get("props").get("pageProps").get("apolloState").get(
                        "ROOT_QUERY").get(f'getBookByLegacyId({{"legacyId":"{book_id}"}})')
                    __refBook = BookByLegacyId.get("__ref")
                    details = data_details_2.get("props").get("pageProps").get("apolloState").get(__refBook).get(
                        "details")
                    # num_pages
                    numpages = details.get("numPages")
                    # publisher
                    publisher = details.get("publisher")
                    # publication_date
                    epoch_time = details.get("publicationTime")
                    publication_date = datetime.fromtimestamp(epoch_time / 1000)
                    # language
                    language = details.get("language").get("name")

                    df2.loc[len(df2)] = [book_id, genres_string, average_rating, language, numpages, ratings_count,
                                         text_reviews_count, publication_date, publisher]
                    # Calculate time to get detail of a book
                    countBook += 1
                    end_time = time()
                    execution_time = end_time - start_time
                    print(f"Thời gian chạy của sách có id {book_id}, STT là {countBook} : {execution_time} giây")
                    print(
                        f"Thời gian chạy của sách có id {book_id}, STT là {countBook}: {float(execution_time / 60)} phút")
                    print(f"Done get details information of book have id {book_id}, STT là {countBook}")
                    break
                except:
                    retries += 1
                    if retries == 3:
                        df2.loc[len(df2)] = [book_id, "", "", "", "", "",
                                             "", "", ""]
                        print(
                            f" err ==== Failed to get details information of book with id {book_id} after 3 retries. ==== err")
                        break  # Thoát khỏi vòng lặp nếu đã thử quá 3 lần
                    else:
                        print(
                            f" err ==== Failed to get details information of book with id {book_id}. Retrying... ==== err")
                        continue

        print("Completely get all the detailed information of the book page {}".format(page))
        df3 = df1.merge(df2, how='left', left_on='bookId', right_on='book_id')
        existing_data = pd.read_csv(path)
        df3.to_csv(path, mode='a', header=False, index=False)

        end_time = time()
        execution_time = end_time - start_time
        print(f"Thời gian chạy của trang {page}: {execution_time} giây")
        print(f"Thời gian chạy của trang {page}: {float(execution_time / 60)} phút")
        page += 1
    except ElementNotInteractableException:
        print("Element Not Interactable Exception!")
        break
    except pd.errors.EmptyDataError:
        df3.to_csv(path, index=False)

# Kết thúc đo thời gian và in ra kết quả
end_time = time()
execution_time = end_time - start_time
print(f"Thời gian chạy của toàn bộ chương trình: {execution_time} giây")
print(f"Thời gian chạy của toàn bộ chương trình: {float(execution_time / 60)} phút")

# Đóng trình duyệt
driver.quit()
