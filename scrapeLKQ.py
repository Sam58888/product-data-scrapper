# Rim Class Import
from rim import Rim

# Data validation and Formatting import
import functions as fn

# Std‑lib
import csv, os
from time import sleep
from typing import List

# Selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


# ───────────────────────── helpers ─────────────────────────
def startSelenium(headless: bool = False):
    opts = Options()
    if headless:
        opts.add_argument("headless")
        opts.add_argument("--log-level=3")
    opts.add_argument("--ignore-certificate-errors")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=opts)


def getKeystone(browser: webdriver):
    wait = WebDriverWait(browser, 10)
    browser.get("https://portal.lkqcorp.com")

    wait.until(EC.visibility_of_element_located((By.ID, "username"))).send_keys(
        os.environ["LKQ_USERNAME"]
    )
    wait.until(EC.visibility_of_element_located((By.ID, "password"))).send_keys(
        os.environ["LKQ_PASSWORD"], Keys.ENTER
    )

    # optional MFA
    try:
        otp = WebDriverWait(browser, 5).until(
            EC.visibility_of_element_located((By.ID, "otp"))
        )
        otp.send_keys(input("Enter LKQ OTP code: "), Keys.ENTER)
    except Exception:
        pass


def hollanderField(browser: webdriver, hollander: str):
    wait = WebDriverWait(browser, 10)
    search = wait.until(EC.element_to_be_clickable((By.XPATH, r'//*[@id="search-field"]')))
    search.clear()
    search.send_keys(hollander, Keys.ENTER)
    sleep(2)


def stripInfo(browser: webdriver, rim: Rim):
    wait = WebDriverWait(browser, 10)

    def matgrid(css: str) -> List[str]:
        grid = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, css)))
        return [t.text for t in grid.find_elements(By.TAG_NAME, "mat-grid-tile")]

    # size / bolt‑pattern / offset
    try:
        dim = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, r'//*[@id="search-results-container"]/div/div/app-product-card[1]/div/section/div[2]/div[1]/h5')
            )
        ).text.split(" ")
        rim.lugs, rim.bp, rim.size = dim[0], dim[2], dim[5]
    except Exception:
        print(f"Failed dimension scrape for {rim.sku}")

    # fitment + description
    try:
        fitment = matgrid(
            r'//*[@id="search-results-container"]/div/div/app-product-card[1]/div/section/div[2]/div[2]/mat-grid-list'
        )

        desc = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, r'//*[@id="search-results-container"]/div/div/app-product-card[1]/div/section/div[3]/span[2]')
            )
        ).text.split("\n")
        info = fn.validation([d[2:] for d in desc])
    except Exception:
        print(f"No results for {rim.sku}")
        info, fitment = [], []

    rim.finish, rim.style, rim.material, rim.width, rim.offset, rim.diameter = (
        str(info[i]) if i < len(info) else "" for i in range(6)
    )
    rim.model = fitment

    # OEM IDs
    browser.find_element(By.TAG_NAME, "html").send_keys(Keys.TAB, Keys.RIGHT, Keys.ENTER)
    oem_raw = matgrid(r"#search-results-container mat-grid-list")
    rim.oemID = [x for x in oem_raw if x.strip() and x not in fitment]


def addRejected(hollander: str):
    with open(unmatchedFile, "a", newline="") as f:
        csv.writer(f).writerow(["NF", hollander])


# ───────────────────────── paths ─────────────────────────
inputFile     = os.path.join(os.getcwd(), "data", "input.csv")
outputFile    = os.path.join(os.getcwd(), "data", "output.csv")
unmatchedFile = os.path.join(os.getcwd(), "data", "unmatchedRims.csv")
allRims: List[Rim] = []
hollanders: List[str] = []

# ───────────────────────── read CSV (DictReader fixes header mismatch) ─────────────────────────
with open(inputFile, newline="") as f:
    for row in csv.DictReader(f):
        sku = row.get("sku", "").strip()
        if sku and sku not in hollanders:
            hollanders.append(sku)

total = len(hollanders)
browser = startSelenium(headless=False)
getKeystone(browser)

for idx, holl in enumerate(hollanders, start=1):
    print(f"{idx}/{total} – {holl}")
    rim = Rim(holl)
    hollanderField(browser, rim.sku)
    stripInfo(browser, rim)
    allRims.append(rim)

# ───────────────────────── write results ─────────────────────────
with open(outputFile, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(
        [
            "sku", "manufacturer", "rim_material", "size_wheel", "diameter", "width",
            "lugs", "bolt_pattern", "offset", "style", "finish", "year", "model",
            "condition", "hollander", "ucode", "mfr_and_alt_numbers", "fitment",
        ]
    )
    for r in allRims:
        w.writerow(
            [
                r.sku, r.mfr, r.material, r.size, r.diameter, r.width, r.lugs, r.bp,
                r.offset, r.style, r.finish, r.years, r.model, "", r.hollander, r.ucode,
                r.oemID, r.vehicleList,
            ]
        )
