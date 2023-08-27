import time
from selenium import webdriver
from selenium.webdriver.common.by import By


import sqlite3
con = sqlite3.connect("data.sqlite")
cur = con.cursor()

#URL of page to be scraped
URL = "https://pdonline.frasercoast.qld.gov.au/#/applications/results?q=submitted-this-month"

#Delay between loading pages. Increase if slow page loads are causing errors
DELAY = 2

#Select Chrome webdriver and maximise
driver = webdriver.Chrome() 
driver.maximize_window()

#Load the webpage
driver.get(URL)

#Find and click the agree button
Agree_Button = driver.find_element(By.ID, 'disclaimer-button-agree') 
driver.execute_script("arguments[0].click();", Agree_Button)

#initiate arrays
records = []
time.sleep(DELAY)
items = driver.find_element(By.XPATH, "//*[@id='grid-app-results']/div/span[2]").text
item = items.split(" ")
items = int(item[item.index("items")-1])

#for all items on the main page
for x in range(1,items+1):
    record = {}
    time.sleep(DELAY)

    #if there's more than 8 items show 100 by using the dropdown box
    if (items > 8):
     DropDown = driver.find_element(By.XPATH, "//*[@id='grid-app-results']/div/span[1]/span/span[2]")
     DropDown.click()
     time.sleep(1)
     Selection = driver.find_element(By.XPATH, "/html/body/div[6]/div/div/div[2]/ul/li[4]")
     Selection.click()
    
    #wait for page to load
    time.sleep(DELAY)

    #click show button
    Show_Button = driver.find_element(By.XPATH, "//tr[" + str(x) + "]/td[4]/button") 
    driver.execute_script("arguments[0].click();", Show_Button)

    #show page for 1 secs
    time.sleep(DELAY)

    #scrape the page and store the data in variables
    council_reference = driver.find_element(By.XPATH, "//*[@id='content']/div/div[1]/div[1]").text
    address = driver.find_element(By.XPATH, "//div/div[13]/a").text
    info_url = driver.current_url
    
    date_received = driver.find_element(By.XPATH, "//*[@id='content']/div/div[3]/table/tbody/tr[2]/td[2]").text
    date_scraped = time.strftime("%d/%m/%Y")
    description = driver.find_element(By.XPATH, "//*[@id='content']/div/div[3]/table/tbody/tr[1]/td[2]").text
    
    #navigate back to main page - refresh required as dropdown fails to load on back
    driver.back()
    driver.refresh()

    #Check database if council reference already exists
    cur.execute("SELECT * FROM data WHERE council_reference=?", (council_reference,))

    #If council reference found update the existing record
    if len(cur.fetchall()) >0:
        
        print("record found, performing update on " + council_reference)
        cur.execute("UPDATE data SET council_reference=?,address=?, info_url=?,date_received=?,date_scraped=?,description=? WHERE council_reference=?",(council_reference, address, info_url, date_received, date_scraped, description, council_reference))
    
    #If council reference not found create one
    else:
        print("no record found, performing insert on " + council_reference)
        cur.execute("INSERT INTO data (council_reference, address, info_url, date_received, date_scraped, description) VALUES (?,?,?,?,?,?)", (council_reference, address, info_url, date_received, date_scraped, description))
    
    #cur.execute("UPDATE data SET council_reference, address, info_url, date_received, date_scraped, description) VALUES (?,?,?,?,?,?)",(council_reference, address, info_url, date_received, date_scraped, description))

    
#print(records)

con.commit()
cur.close()
con.close()

driver.quit()

