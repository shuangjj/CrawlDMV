#!/usr/bin/env python
import os
import sys
import time

import urllib
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

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
    parser.add_argument('--reschedule', action='store_true',
                        help='New schedule or reschedule (default)')
    parser.add_argument('--interval', metavar="Interval", default=5, type=int,
                        help="Refresh interval in minutes")
    parser.add_argument('--account', required=True, metavar="AccountInfo", 
                        help="Text file containing Driver's number, Date of birth, Email and Mobile# each line")

    args = parser.parse_args()
    parser.print_help()
    check_interval = 60 * args.interval
    #print args, check_interval; return 0 
    # Get account info from credential file
    try:
        fp = open(args.account, 'r')
    except IOError:
        print '%s not found!' % (args.license)
        sys.exit()
    else:
        account_info = fp.readlines()
        fp.close()
    # The account information
    driverNum = account_info[0].strip()
    DOB = account_info[1].strip()
    Email = account_info[2].strip()
    Tel = account_info[3].strip()
    
    #print "Driver#: %s, DOB: %s, Email: %s, Tel: %s-%s-%s" % (driverNum, DOB, Email, Tel[0:3], Tel[3:6], Tel[6:])
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
    driverNum_element.send_keys(driverNum)
    # Date of Birth
    dob_element = driver.find_element_by_id("dob")
    dob_element.send_keys(DOB)
    # Login
    continueButton = driver.find_element_by_name("continueButton")
    continueButton.click()
    # Check if it is reschedule or not 
    ps = driver.page_source
    if ps.find("Reschedule my Class C Driver's Test") != -1:
        testRescheduleRadio = driver.find_element_by_id("selectedTestReschedule0")
        testRescheduleRadio.click()
        print 'Reschedule'
    # Scheduling info page
    includeCounty = driver.find_element_by_id("includeCountyCheckBox")
    checked = includeCounty.get_attribute("checked")
    if checked == "true":
        includeCounty.click()

    contButt = driver.find_element_by_name("continueButton")
    contButt.click()
    while True:
        ## Available times
        columbusCheckbox = driver.find_element_by_id("siteName0")
        #columbusCheckbox = driver.find_element(by='value', value='40108#COLUMBUS BLVD DL CENTER  ')
        checked = columbusCheckbox.get_attribute("checked")
        #print checked
        if checked != "true":
            columbusCheckbox.click()
        #checked = columbusCheckbox.get_attribute("checked")
        west_oak_lane = driver.find_element_by_id("siteName4")
        #west_oak_lane = driver.find_element(by='value', value='40121#WEST OAK LANE            ')
        if west_oak_lane.get_attribute("checked") != "true":
            west_oak_lane.click() 
        #checked = west_oak_lane.get_attribute("checked")
        #print checked

        contButt = driver.find_element_by_name("continueButton")
        contButt.click()
        page_source = driver.page_source
        
        findError = page_source.find("There are no exams available for the criteria that you selected.")
        if findError == -1: # Available time
            # Preregister
            site = 'UNKNOWN'
            testDateChoiceID = ['40108', '40121'] # Columbus BLVD, West OAK Lane
            if page_source.find("COLUMBUS BLVD DL CENTER") != -1 and addDate(testDateChoiceID[0]+"examChoice0", driver):
                print "date 0 added for COLUMBUS"
                site = 'COLUMBUS'
                register(site, Tel, Email, driver) 
                sys.exit(0)
            elif page_source.find("WEST OAK LANE") != -1 and addDate(testDateChoiceID[1]+"examChoice0", driver):
                print "date 0 added for West OAK LANE"
                site = 'WEST OAK LANE'
                register(site, Tel, Email, driver)
                sys.exit(0)
            else:
                # alert
                alert_msg = 'No available date'
                print alert_msg
                alert_by_mail(alert_msg, 'co.liang.ol@gmail.com')
                sys.exit(0)
        else:
            print "%s: No exams, sleep!" % (time.asctime())
            time.sleep(check_interval)

def register(site, Tel, Email, driver):
    # Daytime telphone number
    telNumPart1 = driver.find_element_by_name("telNumPart1"); telNumPart1.send_keys(Tel[0:3])
    telNumPart2 = driver.find_element_by_name("telNumPart2"); telNumPart2.send_keys(Tel[3:6])
    telNumPart3 = driver.find_element_by_name("telNumPart3"); telNumPart3.send_keys(Tel[6:])
    # Email
    custEmail = driver.find_element_by_name("custEmail")
    custEmail.send_keys(Email)
    #
    reserveRadio = driver.find_element_by_id("nextPageResrve")
    reserveRadio.click()

    contBut = driver.find_element_by_name("continueButton"); contBut.click()
    alert_msg = '''Road test registered for %s at %s
Check online at 'http://www.dot3.state.pa.us/centers/OnlineServicesCenter.shtml'
    ''' % (site, time.asctime())
    print alert_msg
    alert_by_mail(alert_msg, 'co.liang.ol@gmail.com')
    alert_by_sms(alert_msg, Tel, Email)
    driver.quit()

def addDate(dateID, driver):
    try:
        print dateID
        columbusDate0 = driver.find_element_by_id(dateID)
        columbusDate0.click()
    except NoSuchElementException:
        return False
    else:
        return True

def alert_by_mail(alert_msg, Email):
    from_addr = 'shuang@cis-du02.cis.temple.edu'
    recipients = [Email]
    
    msg = MIMEText(alert_msg)
    msg['Subject'] = "%s: Road Test Available" % (time.asctime())
    msg['From'] = from_addr
    msg['To'] = ', '.join(recipients)
    #s = smtplib.SMTP("smtp.gmail.com",587)
    #s = smtplib.SMTP("smtp.126.com",25)
    #s.ehlo()
    #s.starttls()
    #s.ehlo()
    #s.login(user, pswd)
    s = smtplib.SMTP("localhost")
    s.sendmail(from_addr, recipients, msg.as_string())
    s.quit()

def alert_by_sms(alert_msg, tel, email):
    from_addr = 'shuang@cis-du02.cis.temple.edu'
    attip5 = tel+'@txt.att.net' # @mms.att.net
    recipients = [attip5, email]
    
    msg = MIMEText(alert_msg)
    msg['Subject'] = "%s: Road Test Available" % (time.asctime())
    msg['From'] = from_addr
    msg['To'] = ', '.join(recipients)
    s = smtplib.SMTP("localhost")
    s.sendmail(from_addr, recipients, msg.as_string())
    s.quit()

   


if __name__ == "__main__":
    main()
