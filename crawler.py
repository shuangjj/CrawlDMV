#!/usr/bin/env python
import os
import sys
import time

import urllib
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import smtplib
from email.mime.text import MIMEText

import argparse
from argparse import RawDescriptionHelpFormatter

from pyvirtualdisplay import Display

check_interval = 60*5

def main():
    dmv_url = "http://www.dot4.state.pa.us/centers/OnlineServicesCenter.shtml"
    register_url = "https://www.dot4.state.pa.us/exam_scheduling/eslogin.jsp#top?20140405115120899=20140405115120899"
    # alert
    alert_msg = "Road Test Available at %s\n" % (time.asctime())
    alert_msg = alert_msg + '''Register online at 'http://www.dot3.state.pa.us/centers/OnlineServicesCenter.shtml'
Thank you!'''
    alert_by_mail(alert_msg)
    print alert_msg
    sys.exit(0)

    #
    prompt = '''
    +------------------------------------------------------+
    | Crawl DMV for Road Test Registration.                |
    | Written by somebody who failed the exam 4 times.     |
    +------------------------------------------------------+
    '''
    parser = argparse.ArgumentParser(description=prompt, formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('--server', action='store_true',
                        help='Running the program on server with virtual display.')
    parser.add_argument('--license', default='license.txt', 
                        help="License file containing driver's number and date of birth on each line")
    args = parser.parse_args()
    
    # Get login credentials from file
    try:
        fp = open(args.license, 'r')
    except IOError:
        print '%s not found!' % (args.license)
        sys.exit()
    else:
        credentials = fp.readlines()
        fp.close()
    # Run on server
    if args.server:
        display = Display(visible=0, size=(800, 600))
        display.start()

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
    driverNum_element.send_keys(credentials[0].strip())
    # Date of Birth
    dob_element = driver.find_element_by_id("dob")
    dob_element.send_keys(credentials[1].strip())
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
            alert_msg = "Road Test Available at %s" % (time.asctime())
            alert_msg.append('''Register online at 'http://www.dot3.state.pa.us/centers/OnlineServicesCenter.shtml'
Thank you!''')
            alert_by_mail(alert_msg)
            print alert_msg
            sys.exit(0)
        else:
            print "%s: No exams, sleep!" % (time.asctime())
            time.sleep(check_interval)

def alert_by_mail(alert_msg):
    from_addr = "tue68607@temple.edu"
    recipients = ['co.liang.ol@gmail.com', 'qcaisuda@gmail.com']
    to_addr = "co.liang.ol@gmail.com"
    
    msg = MIMEText(alert_msg)
    msg['Subject'] = "Road Test Available"
    msg['From'] = from_addr
    msg['To'] = ', '.join(recipients)
    s = smtplib.SMTP('localhost')
    s.sendmail(from_addr, recipients, msg.as_string())
    s.quit()


   


if __name__ == "__main__":
    main()
