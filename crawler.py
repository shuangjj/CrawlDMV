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
    parser.add_argument('--interval', default=5, type=int,
                        help="Refresh interval in minutes")
    parser.add_argument('--mailbox', default='126.txt',
                        help="Email used to send alert message")
    args = parser.parse_args()
    check_interval = 60 * args.interval
    #print args, check_interval; return 0 
    # Get DMV login credentials from file
    try:
        fp = open(args.license, 'r')
    except IOError:
        print '%s not found!' % (args.license)
        sys.exit()
    else:
        credentials = fp.readlines()
        fp.close()
    # Get mail credentials from file
    '''
    try:
        fp = open(args.mailbox, 'r')
    except IOError:
        print '%s not found!' % (args.mailbox)
        sys.exit()
    else:
        smtp_mail = fp.readlines()
        fp.close()
    #alert_by_mail("hello, again", smtp_mail[0].strip(), smtp_mail[1].strip())
    '''
    #alert_by_sms("hello"); return
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
        #checked = columbusCheckbox.get_attribute("checked")
        west_oak_lane = driver.find_element_by_id("siteName3")
        if west_oak_lane.get_attribute("checked") != "true":
            west_oak_lane.click() 
        #checked = west_oak_lane.get_attribute("checked")
        #print checked

        contButt = driver.find_element_by_name("continueButton")
        contButt.click()
        page_source = driver.page_source
        
        findError = page_source.find("There are no exams available for the criteria that you selected.")
        if findError == -1: # Available time
            # alert
            alert_msg = '''Road Test Available at %s
Register online at 'http://www.dot3.state.pa.us/centers/OnlineServicesCenter.shtml'
Thank you!
''' % (time.asctime())
            print alert_msg
            alert_by_sms(alert_msg)
            # Preregister
            testDateChoiceID = ['40108', '40121'] # Columbus BLVD, West OAK Lane
            if page_souce.find("COLUMBUS BLVD DL CENTER") != -1:
                columbusDate0 = driver.find_element_by_id(testDateChoiceID[0]+"examChoice0")
                columbusDate0.click()
            elif page_souce.find("WEST OAK LANE") != -1:
                westOakDate0 = driver.find_element_by_id(testDateChoiceID[1]+"examChoice0")
                westOakDate0.click()
            else:
                sys.exit(0)
            # Daytime telphone number
            telNumPart1 = driver.find_element_by_name("telNumPart1"); telNumPart1.send_keys('215')
            telNumPart2 = driver.find_element_by_name("telNumPart2"); telNumPart2.send_keys('301')
            telNumPart3 = driver.find_element_by_name("telNumPart3"); telNumPart3.send_keys('4655')
            # Email
            custEmail = driver.find_element_by_name("custEmail")
            custEmail.send_keys("co.liang.ol@gmail.com")
            #
            reserveRadio = driver.find_element_by_id("nextPageResrve")
            reserveRadio.click()

            contBut = driver.find_element_by_name("continueButton"); contBut.click()

        else:
            print "%s: No exams, sleep!" % (time.asctime())
            time.sleep(check_interval)

def alert_by_mail(alert_msg, user, pswd):
    from_addr = user
    recipients = ['co.liang.ol@gmail.com', 'qcaisuda@gmail.com']
    
    msg = MIMEText(alert_msg)
    msg['Subject'] = "%s: Road Test Available" % (time.asctime())
    msg['From'] = from_addr
    msg['To'] = ', '.join(recipients)
    #s = smtplib.SMTP("smtp.gmail.com",587)
    s = smtplib.SMTP("smtp.126.com",25)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(user, pswd)
    s.sendmail(from_addr, recipients, msg.as_string())
    s.quit()

def alert_by_sms(alert_msg):
    from_addr = 'ubuntu@rungist.com'
    attip5 = '2153014655@txt.att.net' # @mms.att.net
    recipients = [attip5, 'co.liang.ol@gmail.com', 'qcaisuda@gmail.com']
    
    msg = MIMEText(alert_msg)
    msg['Subject'] = "%s: Road Test Available" % (time.asctime())
    msg['From'] = from_addr
    msg['To'] = ', '.join(recipients)
    s = smtplib.SMTP("localhost")
    s.sendmail(from_addr, recipients, msg.as_string())
    s.quit()

   


if __name__ == "__main__":
    main()
