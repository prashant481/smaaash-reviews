from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Smaash Reviews").worksheet("Reviews")

# Selenium setup (visible browser, no headless)
options = Options()
# options.add_argument("--headless")  # Keep commented to watch browser actions

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Google Maps reviews URL for Smaaash MBD Mall Ludhiana
url = "https://www.google.com/maps/place/Smaaash+MBD+Mall+Ludhiana/@30.8829538,75.7790861,840m/data=!3m2!1e3!4b1!4m6!3m5!1s0x391a817d1b176f73:0x85f95cec8e51ae4d!8m2!3d30.8829538!4d75.7816664!16s%2Fg%2F11ghn68m8t?entry=ttu&g_ep=EgoyMDI1MDcyMi4wIKXMDSoASAFQAw%3D%3D"

driver.get(url)

wait = WebDriverWait(driver, 15)

try:
    # Wait for the reviews section to load
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[jscontroller="H6eOGe"]')))
    time.sleep(2)  # Let page settle

    # Scroll to load more reviews
    scrollable_div = driver.find_element(By.CSS_SELECTOR, 'div[class="m6QErb DxyBCb kA9KIf dS8AEf ecceSd"]')
    for i in range(10):  # Scroll 10 times, adjust if needed
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        time.sleep(2)

    # Grab all reviews loaded
    reviews = driver.find_elements(By.CSS_SELECTOR, 'div[jscontroller="H6eOGe"]')
    print(f"Found {len(reviews)} reviews")

    data = []
    for review in reviews:
        try:
            name = review.find_element(By.CSS_SELECTOR, 'div[class*="d4r55"]').text
            rating = review.find_element(By.CSS_SELECTOR, 'span[aria-label*="stars"]').get_attribute('aria-label')
            date = review.find_element(By.CSS_SELECTOR, '.rsqaWe').text
            text = review.find_element(By.CSS_SELECTOR, 'span[jsname="bN97Pc"]').text
            data.append([url, date, name, rating, text])
        except Exception as e:
            print("Error reading a review:", e)
            continue

    if data:
        for row in data:
            sheet.append_row(row)
        print(f"Uploaded {len(data)} reviews to Google Sheets.")
    else:
        print("No data to upload.")

except Exception as e:
    print("Error:", e)

finally:
    print("Closing browser in 5 seconds...")
    time.sleep(5)
    driver.quit()
