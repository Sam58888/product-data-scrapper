# Rim Class Import
from rim import Rim

# Data validation and Formatting import
import functions as fn

# Necessary Python Imports
import csv
import os
from time import sleep
from typing import List

# Necessary Selenium (automated web testing library) Imports
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def startSelenium(background: bool = False):
    """
    Starts Selenium with an option to run headless, returns browser instance

        Keyword Arguments:
            background -- boolean value to indicate headless or not

        Returns:
            browser (webdriver): the browser instance created
    """
    options = Options()
    if background:
        options.add_argument("headless")
        options.add_argument("--log-level=3")

    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    browser = webdriver.Chrome(options=options)
    return browser


def getKeystone(browser: webdriver):
    """
    Logs into the LKQ Keystone portal, assumes credentials are stored as
    environment variables.

        Keyword Arguments:
            browser (webdriver): browser instance
    """

    wait = WebDriverWait(browser, 10)
    login_url = "https://portal.lkqcorp.com"
    browser.get(login_url)

    username_field = wait.until(EC.visibility_of_element_located((By.ID, "username")))
    password_field = wait.until(EC.visibility_of_element_located((By.ID, "password")))

    username_field.send_keys(os.environ["LKQ_USERNAME"])
    password_field.send_keys(os.environ["LKQ_PASSWORD"], Keys.ENTER)

    # optional two‑factor prompt might appear
    try:
        otp_field = wait.until(EC.visibility_of_element_located((By.ID, "otp")))
        otp = input("Enter LKQ OTP code: ")
        otp_field.send_keys(otp, Keys.ENTER)
    except Exception:
        pass  # no OTP prompt


def hollanderField(browser: webdriver, hollander: str):
    """
    Access search bar, clear it, and send desired hollander

        Keyword Arguments:
            browser (webdriver): browser instance
            hollander (str): desired hollander
    """

    wait = WebDriverWait(browser, 10)
    hollField = r'//*[@id="search-field"]'
    hollSearch = wait.until(EC.element_to_be_clickable((By.XPATH, hollField)))
    hollSearch.clear()
    hollSearch.send_keys(hollander, Keys.ENTER)
    sleep(2)


# SPLIT INTO MULTIPLE FUNCTIONS, ACCOMPLISHES A LOT ALL IN ONE PLACE, WOULD BE HARDER TO ALTER
def stripInfo(browser: webdriver, rim: Rim):
    """
    Modifies a rim object to add necessary data

        Keyword Arguments:
            browser (webdriver): current browser instance
            rim (Rim): rim object being modified
    """

    def returnMatGridText(browser: webdriver, css_selector: str) -> List[str]:
        wait = WebDriverWait(browser, 10)
        matGrid = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))
        tools = matGrid.find_elements_by_tag_name("mat-grid-tile")
        textList = []
        for tool in tools:
            textList.append(tool.text)
        return textList

    cssSelector = r"app-product-card mat-grid-list"
    wait = WebDriverWait(browser, 10)

    try:
        dimPath = r'//*[@id="search-results-container"]/div/div/app-product-card[1]/div/section/div[2]/div[1]/h5'
        dimensions = wait.until(EC.visibility_of_element_located((By.XPATH, dimPath))).text
        text = dimensions.split(" ")
        rim.lugs = text[0]
        rim.bp = text[2]
        rim.size = text[5]
    except Exception:
        print(f"Failed to find dimension info for {rim.sku}")

    try:
        fitmentPath = r'//*[@id="search-results-container"]/div/div/app-product-card[1]/div/section/div[2]/div[2]/mat-grid-list'
        fitmentList = returnMatGridText(browser, fitmentPath)

        cssSelector = r"#search-results-container mat-grid-list"
        partDescriptionPath = r'//*[@id="search-results-container"]/div/div/app-product-card[1]/div/section/div[3]/span[2]'
        partDescription = wait.until(EC.visibility_of_element_located((By.XPATH, partDescriptionPath)))
        text = partDescription.text
        temp = text.split("\n")
        info = [temp[i][2:] for i in range(len(temp))]
    except Exception:
        print(f"No results for {rim.sku}")
        info = []

    # Validation done here!
    info = fn.validation(info)

    rim.finish = str(info[0])
    rim.style = str(info[1])
    rim.material = str(info[2])
    rim.width = str(info[3])
    rim.offset = str(info[4])
    rim.diameter = str(info[5])
    rim.model = fitmentList

    elementToSendKeys = browser.find_element_by_tag_name("html")
    elementToSendKeys.send_keys(Keys.TAB, Keys.RIGHT, Keys.ENTER)
    oemIDList = returnMatGridText(browser, cssSelector)
    fixedOEMIDList = [
        element for element in oemIDList[len(fitmentList) :] if element not in fitmentList and element.strip()
    ]
    rim.oemID = fixedOEMIDList


def restart(browser: webdriver, hollander: str):
    """
    Restart process when program stalls or fails to load properly

        Keyword Arguments:
            browser (webdriver): browser instance
            hollander (str): rejected hollander
    """
    rim = Rim(hollander)
    hollanderField(browser, rim.sku)
    stripInfo(browser, rim)
    allRims.append(rim)
    print(f"Hollander {rim.sku} successfully added to list.\n")


def addRejected(hollander: str):
    """
    Adds a not‑found hollander to unmatchedRims.csv

        Keyword Arguments:
            hollander (str): rejected hollander
    """
    file = unmatchedFile
    with open(file, "a", newline="") as rejected:
        rejectedWriter = csv.writer(rejected)
        rejectedWriter.writerow(["NF", hollander])


# -----------  file locations (edited)  -----------------
inputFile = os.path.join(os.getcwd(), "data", "input.csv")
outputFile = os.path.join(os.getcwd(), "data", "output.csv")
unmatchedFile = os.path.join(os.getcwd(), "data", "unmatchedRims.csv")
allRims: List[Rim] = []
hollanders: List[str] = []
# -------------------------------------------------------


# Opens input file to create a search list of unique hollanders
with open(inputFile, "r", newline="") as csvreader:
    reader = csv.reader(csvreader, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL)
    for row in reader:
        if row[1] not in hollanders:
            hollanders.append(row[1])

total = len(hollanders)
browser = startSelenium(background=False)
current = 1

# Runs for every hollander, tries twice before rejecting
getKeystone(browser)
for hollander in hollanders:
    print(f"{current} out of {total}")
    if current > 1:
        restart(browser, hollander)
    else:
        rim = Rim(hollander)
        hollanderField(browser, rim.sku)
        stripInfo(browser, rim)
        allRims.append(rim)
    current += 1

# Writes rim objects to output file
with open(outputFile, "w", newline="") as csvwriter:
    writer = csv.writer(csvwriter)
    writer.writerow(
        [
            "sku",
            "manufacturer",
            "rim_material",
            "size_wheel",
            "diameter",
            "width",
            "lugs",
            "bolt_pattern",
            "offset",
            "style",
            "finish",
            "year",
            "model",
            "condition",
            "hollander",
            "ucode",
            "mfr_and_alt_numbers",
            "fitment",
        ]
    )
    for rim in allRims:
        if rim is not None:
            writer.writerow(
                [
                    rim.sku,
                    rim.mfr,
                    rim.material,
                    rim.size,
                    rim.diameter,
                    rim.width,
                    rim.lugs,
                    rim.bp,
                    rim.offset,
                    rim.style,
                    rim.finish,
                    rim.years,
                    rim.model,
                    "",
                    rim.hollander,
                    rim.ucode,
                    rim.oemID,
                    rim.vehicleList,
                ]
            )
