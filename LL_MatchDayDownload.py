import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import getpass
from webdriver_manager.chrome import ChromeDriverManager  # auto manages driver

# Config
#ll_Login = ""
#ll_pw = getpass.getpass("Enter your LearnedLeague password: ")
profile_url = "https://www.learnedleague.com/profiles.php?58091&7"
output_folder = r"C:\DataAnalysis\Learned League\Match Days"
os.makedirs(output_folder, exist_ok=True)

# Set Chrome options
options = Options()
# options.add_argument("--headless")  # uncomment to run without opening browser window

# Setup ChromeDriver service with webdriver_manager
service = Service(ChromeDriverManager().install())

# Initialize driver
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://www.learnedleague.com/")

# Wait and log in
time.sleep(2)
#driver.find_element(By.NAME, "name").send_keys(ll_Login)
#driver.find_element(By.NAME, "pw").send_keys(ll_pw)

# Wait for login to complete
time.sleep(3)

# Visit your profile page
driver.get(profile_url)
time.sleep(2)

# Grab cookies from logged-in session
cookies = driver.get_cookies()
session = requests.Session()
for cookie in cookies:
    session.cookies.set(cookie['name'], cookie['value'])

# Parse profile page
soup = BeautifulSoup(driver.page_source, 'html.parser')
match_links = soup.find_all('a', href=True)
match_ids = set()

for link in match_links:
    href = link['href']
    if "/match.php?id=" in href:
        match_id = href.split('=')[-1]
        match_ids.add(match_id)

driver.quit()

print(f"🔍 Found {len(match_ids)} match IDs. Downloading...")

# Download each match page with cookies
for match_id in match_ids:
    match_url = f"https://www.learnedleague.com/match.php?id={match_id}"
    file_path = os.path.join(output_folder, f"{match_id}.htm")

    r = session.get(match_url)
    if r.status_code == 200:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(r.text)
        print(f"✅ Saved {match_id}.htm")
    else:
        print(f"❌ Failed to download {match_id} (Status: {r.status_code})")
