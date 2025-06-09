# Rim Class Import
from rim import Rim

#Data validation and Formatting import
import functions as fn

# Necessary Python Imports
from time import sleep
from typing import List

# Necessary Selenium (automated web testing library) Imports 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# More Python Imports
import os
import csv
import urllib.request

# Enjoy

def validation(info: list) -> list:

    # NEED TO GENERALIZE A ROOT FUNCTION
    # ALL THE FUNCTION REVOLVE AROUND A SHARED BASIC IDEA
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    def splitFinishBP(info: list) -> list:
        """
        Splits up Finish and BP when they appear on the same bullet point on lkq
        """
        row = info[0]
        splitIndex = row.index("BP") + 2
        boltPattern = row[:splitIndex].strip()
        finish = row[splitIndex:].strip()
        outp = [finish, boltPattern]
        for row in info[1:]:
            outp.append(row.strip())
        return outp
    
    def splitBPLug(info: list) -> list:
        """
        Splits up BP and Lug when they appear on the same bullet point on lkq
        """
        row = info[1]
        splitIndex = row.index("STUD/LUG") + len("STUD/LUG")
        boltPattern = row[splitIndex:].strip()
        lug = row[:splitIndex].strip()
        outp = [info[0].strip(), boltPattern, lug]
        for row in info[2:]:
            outp.append(row.strip())
        return outp
    
    def splitLugSpoke(info):
        row = info[2]
        splitIndex = row.index("STUD/LUG") - 2
        spoke = row[splitIndex:].strip()
        lug = row[:splitIndex].strip()
        outp = [info[0].strip(), info[1].strip(), spoke, lug]
        for row in info[3:]:
            outp.append(row.strip())
        return outp
    
    def splitOffsetSpoke(info):
        row = info[3]
        splitIndex = row.index("OFFSET") + len("OFFSET")
        spoke = row[splitIndex:].strip()
        offset = row[:splitIndex].strip()
        outp = [info[0].strip(), info[1].strip(), info[2], spoke, offset]
        for row in info[4:]:
            outp.append(row.strip())
        return outp

    def splitSizeOffset(info):
        row = info[4]
        splitIndex = row.find(" ", row.index(" x ") + len(" x "))
        offset = row[splitIndex:].strip()
        size = row[:splitIndex].strip()
        outp = [info[0].strip(), info[1].strip(), info[2], info[3], offset, size]
        return outp

    # Case in which info appears to be fine
    if len(info) == 6:
        outp = []
        for row in info:
            outp.append(row.strip())
        return outp

    elif len(info) < 6:
        # look for what shouldnt be in each row (row beneath always added to front of row above)
        # once you find it return the fuction for that specific case

        # case one (finish and bp combination)
        if " BP" in info[0]:
            return splitFinishBP(info)
            
        # case two (bp lug combined)
        elif "STUD/LUG" in info[1]:
            return splitBPLug(info)

        # case three (lug and spoke combined)
        elif info[2].index('G') > len("## Stud/Lug") - 1:
            return splitLugSpoke(info)

        # case four (spoke and offset)
        elif " OFFSET " in info[3]:
            return splitOffsetSpoke(info)

        # case five (offset and size)
        elif " x " in info[4]:
            return splitSizeOffset(info)
        pass
    
    elif len(info) > 6:
        return validation(info[1:])

#def startSelenium(background=False):
#    """
#    Starts Selenium with an option to run headless, returns browser instance
#
#        Keyword Arguments:
#            background -- boolean value to indicate headless or not
#
#        Returns: 
#            browser (webdriver): the browser instance created
#    """
#    options = Options()
#    if background == True:
#        options.add_argument('headless')
#        options.add_argument('--log-level=3')
#    
#    # Local path of chromedriver
#    #
#    # I can point this to the current directory and add to PATH (necessary to run)
#    browser = webdriver.Chrome(
#        r"C:\Users\fww\Desktop\Danny\Python\ChromeDriver\chromedriver.exe",
#        options = options)
#    return browser
#
#def getKeystone(browser: webdriver):
#    """
#    Logs in to LKQ website
#
#        Keyword Arguments:
#            browser (webdriver): current browser instance
#    """
#    username = "James.Doyle"
#    password = "FWW@DMIN1211"
#    browser.get("https://portal.lkqcorp.com/login")
#    userField = browser.find_element_by_id("username")
#    userField.send_keys(username)
#    passField = browser.find_element_by_id("passwordTextBox")
#    passField.send_keys(password)
#    passField.send_keys(Keys.ENTER)
#    
#def hollanderField(browser: webdriver, hollander: str):
#    """
#    Selects and enters hollander into search field
#
#        Keyword Arguments:
#            browser (webdriver): current browser instance
#            hollander (str): hollander to search
#    """
#    wait = WebDriverWait(browser, 5)
#    shopAM = r'//*[@id="main-content-area"]/app-landing/div/div[1]/div/div[1]/div/div/button'
#    shopAMButton = wait.until(EC.element_to_be_clickable((By.XPATH, shopAM)))
#    shopAMButton.click()
#    sleep(2)
#    crashParts = r'/html/body/app-root/app-nav-bar/div/div[3]/div[2]/app-side-bar-search/div[1]'
#    crashPartsButton = wait.until(EC.element_to_be_clickable((By.XPATH, crashParts)))
#    crashPartsButton.click()
#    sleep(2)
#    hollField = r'/html/body/app-root/app-nav-bar/div/div[3]/div[2]/app-side-bar-search/div[1]/div[2]/input'
#    hollSearch = wait.until(EC.element_to_be_clickable((By.XPATH, hollField)))
#    hollSearch.send_keys(hollander, Keys.ENTER)
#    sleep(2)
#
#def restart(browser: webdriver, hollander: str):
#    """
#    Modified restarting procedure
#
#        Keyword Arguments:
#            browser (webdriver): current browser instance
#            hollander (str): hollander to search
#    """
#    wait = WebDriverWait(browser, 5)
#    browser.get(r'https://preview.orderkeystone.com/')
#    sleep(2)
#    crashParts = r'/html/body/app-root/app-nav-bar/div/div[3]/div[2]/app-side-bar-search/div[1]'
#    crashPartsButton = wait.until(EC.element_to_be_clickable((By.XPATH, crashParts)))
#    crashPartsButton.click()
#    sleep(2)
#    hollField = r'/html/body/app-root/app-nav-bar/div/div[3]/div[2]/app-side-bar-search/div[1]/div[2]/input'
#    hollSearch = wait.until(EC.element_to_be_clickable((By.XPATH, hollField)))
#    hollSearch.clear()
#    hollSearch.send_keys(hollander, Keys.ENTER)
#    sleep(2)
#
#
## SPLIT INTO MULTIPLE FUNCTIONS, ACCOMPLISHES A LOT ALL IN ONE PLACE, WOULD BE HARDER TO ALTER
#def stripInfo(browser: webdriver, rim: Rim):
#    """
#    Modifies a rim object to add necessary data
#
#        Keyword Arguments:
#            browser (webdriver): current browser instance
#            rim (Rim): rim object being modified
#    """
#    def returnMatGridText(browser: webdriver, css_selector: str) -> List[str]:
#        """
#        Selects and enters hollander into search field
#
#            Keyword Arguments:
#                browser (webdriver): current browser instance
#                css_selector (str): css selector for specific element type
#
#            Returns:
#                outp (list): list of data elements
#        """
#        elements = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, cssSelector)))
#        elements = browser.find_elements_by_css_selector(css_selector)
#        outp = []
#        for element in elements:
#            outp.append(element.text.strip())
#        return outp
#    
#    # Strip Shown Details
#    wait = WebDriverWait(browser, 5)
#    try:
#        partDescriptionPath = r'//*[@id="search-results-container"]/div/div/app-product-card/div/section/div[3]/span[2]'
#        partDescription = wait.until(EC.visibility_of_element_located((By.XPATH, partDescriptionPath)))
#        text = partDescription.text
#        temp = text.split('\n')
#        info = []
#        for i in range(len(temp)):
#            info.append(temp[i][2:])
#    except:
#        try:
#            partDescriptionPath = r'//*[@id="search-results-container"]/div/div/app-product-card[1]/div/section/div[3]/span[2]'
#            partDescription = wait.until(EC.visibility_of_element_located((By.XPATH, partDescriptionPath)))
#            text = partDescription.text
#            temp = text.split('\n')
#            info = []
#            for i in range(len(temp)):
#                info.append(temp[i][2:])
#        except:
#            print(f"No results for {rim.sku}")
#    
#    # Info list will be passed in
#    # Validation done here!
#    info = fn.validateDescription(info)
#
#    rim.finish = str(info[0])
#    rim.bp = str(info[1])
#    rim.lugs = str(info[2])
#    rim.style = str(info[3])
#    rim.offset = str(info[4])
#    rim.size = str(info[5])
#
#    # Strip Image    
#    # Tries to access the other information by clicking image first
#    # Otherwise click on first one that has a partial link text match
#    try:
#        imagePath = r'//*[@id="search-results-container"]/div/div/app-product-card/div/section/div[2]/img'
#        image = browser.find_element_by_xpath(imagePath)
#    except:
#        imagePath = r'//*[@id="search-results-container"]/div/div/app-product-card[1]/div/section/div[2]/img'
#        image = browser.find_element_by_xpath(imagePath)
#    try:
#        imageSRC = image.get_attribute('src')
#        imageSavePath = os.getcwd()
#        imageSavePath += rf'\images\{rim.sku}.png'
#        urllib.request.urlretrieve(imageSRC, imageSavePath)
#        print(f'Image for hollander {rim.sku} successfully added to images folder as "{rim.sku}.png"')
#        image.click()
#    except:
#        print("Error selecting and saving image")
#
#    # Strip Year, Make, Model Info and OEM ID's
#    try:
#        sleep(2)
#        cssSelector = 'span.modal-detail-content.grid-text'
#        fitmentList = returnMatGridText(browser, cssSelector)
#        rim.model = fitmentList
#        elementToSendKeys = browser.find_element_by_tag_name('html')
#        elementToSendKeys.send_keys(Keys.TAB, Keys.RIGHT, Keys.ENTER)
#        oemIDList = returnMatGridText(browser, cssSelector)
#        fixedOEMIDList = []
#        for element in oemIDList[len(fitmentList):]:
#            if element not in fitmentList or element != '' or element != ' ':
#                fixedOEMIDList.append(element)
#        rim.oemID = fixedOEMIDList
#    except:
#        print(f'Failed to retrieve extra info for {rim.sku}')
#
#def addRejected(hollander: str):
#    """
#    Adds a not found hollander to rejectedHollanders.csv
#
#        Keyword Arguments:
#            hollander (str): rejected hollander
#    """
#    file = os.getcwd() + r'\data\rejectedHollanders.csv'
#    with open(file, 'a', newline = '') as rejected:
#        rejectedWriter = csv.writer(rejected)
#        rejectedWriter.writerow(['NF', hollander])
#
#def createHollList(unmatchedRimsFile: str, hollanders):
#    with open(unmatchedRimsFile, 'r', newline = '') as csvreader:
#        reader = csv.reader(csvreader, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
#        for row in reader:
#            if row[1] not in hollanders:
#                hollanders.append(row[1])
#
#def run(search_hollander: function, browser: webdriver, allRims: List[Rim], hollanders: List[str], unmatchedRimsFile: str):
#    createHollList(unmatchedRimsFile, hollanders)
#    total = len(hollanders)
#    count = 0
#    for hollander in hollanders:
#        print(f'{count} out of {total}')
#        try:
#            search_hollander(browser, hollander, browser, hollander, allRims, count)
#        except:
#            print(f'{hollander} appended to rejectedHollanders.csv \n')
#            addRejected(hollander)
#        count += 1
#
#@run
#def search_hollander(browser: webdriver, hollander: str, allRims: List[Rim], count: int):
#    """
#    Combines all function into one all inclusive function
#
#        Keyword Arguments:
#            browser (webdriver): browser instance
#            hollander (str): rejected hollander
#    """
#    rim = Rim(hollander)
#    if count > 1:
#        if rim.sku[-1].upper() == 'N':
#            restart(browser, rim.sku[:len(rim.sku) - 1])
#        else:
#            restart(browser, rim.sku)
#    else:
#        hollanderField(browser, rim.sku)
#    stripInfo(browser, rim)
#    allRims.append(rim)
#    print(f'Hollander {rim.sku} successfully added to list.\n')