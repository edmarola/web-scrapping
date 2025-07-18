import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from extraction import prompt_template, structured_llm

options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.page_load_strategy = "eager"
driver = webdriver.Chrome(options=options)


driver.get("https://scribemedia.com/published-books/?sf_paged=96")
driver.implicitly_wait(5)
books = driver.find_elements(
    By.CSS_SELECTOR, value="#filteredbooks .book-entry-bio"
)
close_cmplz = driver.find_element(By.CSS_SELECTOR, value=".cmplz-close")
if close_cmplz:
    close_cmplz.click()
time.sleep(1)
books_data = []
try:
    for n in range(39):
        # for n in range(2):
        print(f"Page {n+1}")
        for book in books:
            book_title = book.find_element(
                By.CSS_SELECTOR, value="p > em"
            ).text.strip()
            book_authors = book.find_element(
                By.CSS_SELECTOR, value="p:last-child"
            ).text.strip()
            print(f"Processing book: {book_title} by {book_authors}")
            if not book_authors:
                if book_title == "Choose Better":
                    book_authors = "By Timothy Yen"
                if book_title == "The Underwear in My Shoe":
                    book_authors = "By Brett Russo"
            prompt = prompt_template.invoke({"authors": book_authors})
            authors = structured_llm.invoke(prompt)
            books_data.append(
                {
                    "Book title": book_title,
                    "Author": authors.first_author,  # type: ignore
                    "Co-authors": authors.co_authors,  # type: ignore
                }
            )

        print(f"Next page {n+2}")
        next_button = driver.find_element(By.CSS_SELECTOR, "a.next-posts-link")
        ActionChains(driver).scroll_to_element(next_button).perform()
        time.sleep(3)
        next_button.click()
        time.sleep(5)
        books = driver.find_elements(
            By.CSS_SELECTOR, value="#filteredbooks .book-entry-bio"
        )
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    print("Closing the browser...")
    driver.quit()
    df = pd.DataFrame(books_data)
    df.to_csv("scribe_books.csv", index=False)
