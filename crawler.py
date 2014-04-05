#!/usr/bin/env python
import os
import sys
import time

import urllib
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import smtplib
from email.mime.text import MIMEText


check_interval = 60*5

def main():
    dmv_url = "http://www.dot4.state.pa.us/centers/OnlineServicesCenter.shtml"
    register_url = "https://www.dot4.state.pa.us/exam_scheduling/eslogin.jsp#top?20140405115120899=20140405115120899"
    #print urllib.urlopen(register_url).read()
    ## Load ChromeDriver
    chromedriver = "/opt/drivers/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver
    driver = webdriver.Chrome(chromedriver)
    ##  Schedule page to login page
    driver.get(dmv_url)

    links = driver.find_elements_by_css_selector("td#centerSubTitle a")
    links[-3].click()

    # Setup driver number
    driverNum_element = driver.find_element_by_id("driverNum")
    driverNum_element.send_keys("31433298")
    # Date of Birth
    dob_element = driver.find_element_by_id("dob")
    dob_element.send_keys("12/01/1988")
    # Login
    continueButton = driver.find_element_by_name("continueButton")
    continueButton.click()
    # Scheduling info page
    includeCounty = driver.find_element_by_id("includeCountyCheckBox")
    checked = includeCounty.get_attribute("checked")
    if checked == "true":
        includeCounty.click()
    contButt = driver.find_element_by_name("continueButton")
    contButt.click()
    #driver.quit()
    while True:
        ## Available times
        columbusCheckbox = driver.find_element_by_id("siteName0")
        checked = columbusCheckbox.get_attribute("checked")
        #print checked
        if checked != "true":
            columbusCheckbox.click()
        checked = columbusCheckbox.get_attribute("checked")
        #print checked

        contButt = driver.find_element_by_name("continueButton")
        contButt.click()
        page_source = driver.page_source
        
        findError = page_source.find("There are no exams available for the criteria that you selected.")
        if findError == -1: # Available time
            # alert
            alert_by_mail("Road Test Available at " % (time.asctime()))
            sys.exit(0)
        else:
            print "No exams, sleep!"
            time.sleep(check_interval)

def alert_by_mail(msg):
    from_addr = "tue68607@temple.edu"
    to_addr = "co.liang.ol@gmail.com"
    msg = MIMEText(msg)
    msg['Subject'] = msg
    msg['From'] = from_addr
    msg['To'] = to_addr
    s = smtplib.SMTP('localhost')
    s.sendmail(from_addr, to_addr, msg.as_string())
    s.quit()


   


if __name__ == "__main__":
    main()
