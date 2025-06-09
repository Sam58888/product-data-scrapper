# Rim Class Import
from rim import Rim
import functions as fn

# Std‑lib
import csv, os, sys
from time import sleep
from typing import List

# Selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


# ───────────────────────── Selenium helper ─────────────────────────
def startSelenium(headless: bool = True) -> webdriver.Chrome:
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    # disguise as real Chrome
    opts.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/137 Safari/537.36"
    )
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=opts)


# ───────────────────────── Keystone login ─────────────────────────
def getKeystone(browser: webdriver.Chrome):
    """
    Logs into the LKQ Keystone portal.  Works with stock, Okta, or Azure AD
    login pages.  Saves both HTML and PNG so we can debug if selectors fail.
    """
    wait = WebDriverWait(browser, 45)
    browser.get("https://portal.lkqcorp.com")

    # dump first page
    with open("login_page.html", "w", encoding="utf-8") as f:
        f.write(browser.page_source)
    browser.save_screenshot("login_page.png")

    # --- 1) username field ---
    try:
        user_field = wait.until(
            EC.visibility_of_any_elements_located(
                (
                    (By.ID, "username"),               # generic
                    (By.ID, "okta-signin-username"),   # Okta
                    (By.NAME, "loginfmt"),             # Azure
                )
            )
        )[0]
        user_field.clear()
        user_field.send_keys(os.environ["LKQ_USERNAME"])
    except Exception as e:
        raise RuntimeError("Username field not found – inspect login_page.html") from e

    # click “Next/Submit” if present
    for by, sel in [
        (By.ID, "next"),
        (By.ID, "idSIButton9"),               # Azure
        (By.CSS_SELECTOR, "input[type=submit]"),
    ]:
        try:
            browser.find_element(by, sel).click()
            break
        except Exception:
            pass  # button not on this page

    # --- 2) password field ---
    try:
        pwd_field = wait.until(
            EC.visibility_of_any_elements_located(
                (
                    (By.ID, "password"),
                    (By.ID, "okta-signin-password"),
                    (By.NAME, "passwd"),              # Azure
                )
            )
        )[0]
        pwd_field.send_keys(os.environ["LKQ_PASSWORD"], Keys.ENTER)
    except Exception as e:
        raise RuntimeError("Password field not found – inspect login_page.html") from e

    # optional MFA (ignored if not present)
    try:
        otp = WebDriverWait(browser, 8).until(
            EC.visibility_of_element_located((By.ID, "otp"))
        )
        otp.send_keys(input("Enter LKQ OTP code: "), Keys.ENTER)
    except Exception:
        pass


# ───────────────────────── Scraper helpers ─────────────────────────
def hollanderField(browser: webdriver.Chrome, hollander: str):
    wait = WebDriverWait(browser, 20)
    search = wait.until(EC.element_to_be_clickable((By.XPATH, r'//*[@id="search-field"]')))
    search.clear()
    search.send_keys(hollander, Keys.ENTER)
    sleep(2)


def stripInfo(browser: webdriver.Chrome, rim: Rim):
    wait = WebDriverWait(browser, 20)

    def matgrid(css: str) -> List[str]:
        grid = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, css)))
        return [t.text for t in grid.find_elements(By.TAG_NAME, "mat-grid-tile")]

    # dimensions
    try:
        dim = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, r'//*[@id="search-results-container"]/div/div/app-product-card[1]/div/section/div[2]/div[1]/h5')
            )
        ).text.split(" ")
        rim.lugs, rim.bp, rim.size = dim[0], dim[2], dim[5]
    except Exception:
        print(f"Failed dimension scrape for {rim.sku}", file=sys.stderr)

    # fitment & description
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
        print(f"No results for {rim.sku}", file=sys.stderr)
        info, fitment = [], []

    rim.finish, rim.style, rim.material, rim.width, rim.offset, rim.diameter = (
        str(info[i]) if i < len(info) else "" for i in range(6)
    )
    rim.model = fitment

    # OEM IDs
    browser.find_element(By.TAG_NAME, "html").send_keys(Keys.TAB, Keys.RIGHT, Keys.ENTER)
    oem_raw = matgrid(r"#search-results-container mat-grid-list")
    rim.oemID = [x for x in oem_raw if x.strip() and x not in fitment]


# ───────────────────────── File paths ─────────────────────────
inputFile     = os.path.join(os.getcwd(), "data", "input.csv")
outputFile    = os.path.join(os.getcwd(), "data", "output.csv")
unmatchedFile = os.path.join(os.getcwd(), "data", "unmatchedRims.csv")
allRims: List[Rim] = []
hollanders: List[str] = []

# ───────────────────────── Read input.csv ─────────────────────────
with open(inputFile, newline="", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        sku = row.get("sku") or row.get("SKU") or row.get("\ufeffsku") or ""
        sku = sku.strip()
        if sku and sku not in hollanders:
            hollanders.append(sku)

if not hollanders:
    raise RuntimeError("input.csv had no SKUs – aborting run.")

# ───────────────────────── Scrape ─────────────────────────
browser = startSelenium(headless=True)
getKeystone(browser)

for idx, holl in enumerate(hollanders, start=1):
    print(f"{idx}/{len(hollanders)} – {holl}")
    rim = Rim(holl)
    hollanderField(browser, rim.sku)
    stripInfo(browser, rim)
    allRims.append(rim)

browser.quit()

# ───────────────────────── Write results ─────────────────────────
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
