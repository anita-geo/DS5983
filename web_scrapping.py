from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pymysql
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'khoury'
}

service = Service('/opt/homebrew/bin/chromedriver')
driver = webdriver.Chrome(service=service)
driver.get("https://www.khoury.northeastern.edu/abouçt/people/")

time.sleep(2)

# Select dropdown
dropdown = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "people-dropdown-faculty-research-area"))
)
select = Select(dropdown)
select.select_by_visible_text("Artificial Intelligence")

time.sleep(15)

parent_div = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.ID, "people-page-results"))
)

ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
time.sleep(2)  
ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
time.sleep(2)  
ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
time.sleep(2)  
ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
time.sleep(2)  
ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
time.sleep(2)  
ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
time.sleep(2)  

parent_divs = parent_div.find_elements(By.XPATH, './div')

print('Starting processing...')
def extract_section(driver, header_text):
    try:
        header_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//h2[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{header_text.lower()}')]"))
        )

        if header_text.lower() == 'biography':
            paragraphs = header_element.find_elements(By.XPATH, "following-sibling::p")
            return "\n\n".join([p.text for p in paragraphs])

        sibling = header_element.find_element(By.XPATH, "following-sibling::*[1]")
        if sibling.tag_name == 'ul':
            return "\n\n".join([li.text for li in sibling.find_elements(By.TAG_NAME, 'li')])
        elif sibling.tag_name == 'p':
            return sibling.text
    except Exception as e:
        return None

# Connect to the database
connection = pymysql.connect(**db_config)
cursor = connection.cursor()

for index, div in enumerate(parent_divs):
    try:
        name = div.find_element(By.CLASS_NAME, 'headline').text
        title = div.find_element(By.CLASS_NAME, 'position-list').text

        print('***********************************************')
        print(f"\n\n Processing: {name} - {title}")

        div.click()

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "copy"))
        )
        time.sleep(5)

        research_interests = extract_section(driver, 'Research Interests')
        if not research_interests:
            research_interests = extract_section(driver, 'Research areas')
        education = extract_section(driver, 'Education')
        biography = extract_section(driver, 'Biography')
        if not biography:
            biography = extract_section(driver, 'Bio')

        print("Research Interests:", research_interests if research_interests else "Not Found")
        print("Education:", education if education else "Not Found")
        print("Biography:", biography if biography else "Not Found")

        insert_query = """
        INSERT INTO khoury_people (Name, Title, Education, Biography, ResearchInterest)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (name, title, education, biography, research_interests))
        connection.commit()

        print("Inserted into database:", name)

        driver.back()

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "people-page-results"))
        )
        parent_divs = driver.find_elements(By.XPATH, "//div[@id='people-page-results']/div")

    except Exception as e:
        print(f"Error processing item {index + 1}: {e}")
        driver.back()
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "people-page-results"))
        )
        parent_divs = driver.find_elements(By.XPATH, "//div[@id='people-page-results']/div")

driver.quit()
