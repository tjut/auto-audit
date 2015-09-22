#!/usr/bin/python
# vim: set fileencoding=utf8

# Author: HZJ @ TJUT
# Date: 2015.8.17
# Description: audit the accounts automatically using Selenium WebDriver
# 注：出于安全考虑，笔者隐去后台管理系统的网址、管理员用户名和密码


import sys;
import time;
from selenium import webdriver;
from selenium.common.exceptions import TimeoutException,NoSuchElementException;
from selenium.webdriver.support.ui import WebDriverWait;
from selenium.webdriver.common.by import By;
from selenium.webdriver.support import expected_conditions as EC;
from selenium.webdriver.common.keys import Keys;
from selenium.webdriver.support.ui import Select;   # Used to handle <select> control
from selenium.webdriver.common.alert import Alert;

# Global settings
siteURL = "http://***************/";
adminName = "************";
adminPassword = "************";

# Create a new instance of the Firefox driver
driver = webdriver.Firefox();

# Implicit wait is a better choice, but is confusing for beginner.
#driver.implicitly_wait(10);

# Open the management entry
driver.get(siteURL);

# Find the username & password input element by XPath
usernameBox = driver.find_element_by_xpath("html/body/div[1]/div[3]/form/table/tbody/tr[1]/td[2]/input");
passwordBox = driver.find_element_by_xpath("html/body/div[1]/div[3]/form/table/tbody/tr[2]/td[2]/input");
# Fill in the username and password
usernameBox.send_keys(adminName);
passwordBox.send_keys(adminPassword);

# Submit!
passwordBox.submit();

### Waiting for the result page to present
try:
	WebDriverWait(driver,10).until(
		EC.presence_of_element_located((By.XPATH, "html/body/div[3]/ul/li[2]/dl/dt")));
except TimeoutException:
	sys.exit("Time out in opening management page");


# Now, we have logined in and face the main management page
# Click the "用户管理" menu
driver.find_element_by_xpath("html/body/div[3]/ul/li[2]/dl/dt").click();
# Waiting for the sub-menu to display, otherwise the click operation will fail
WebDriverWait(driver,5).until(EC.visibility_of_element_located((By.XPATH,"html/body/div[3]/ul/li[2]/dl/dd[3]/a")));
driver.find_element_by_xpath("html/body/div[3]/ul/li[2]/dl/dd[3]/a").click();


# Switch the context to iframe named "content"
driver.switch_to_frame("content");
driver.maximize_window();
time.sleep(1);


# We only handle the last page here for simplicity
# Find the "最后页" link and click it
try:
	lastpagelink = driver.find_element_by_link_text("最后页");
	lastpagelink.click();
	time.sleep(1);
except NoSuchElementException:
	sys.exit("There is no lastpage link");


# Begin to audit the pending account

# Auditing Rules are are in this function
# Return True to pass, and False to refuse.
def audit(name, cardid, regtime, type):
	# you can use any rules to check the user's validity

	# just refuse simply here for demo
	return False;


lastpageURL = driver.current_url;
count = 0;
while True:
	path = "html/body/div[2]/table/tbody/tr[2]/td[7]/a[1]";
	try:
		auditbtn = driver.find_element_by_xpath(path);
	except NoSuchElementException:
		print("[%d]# processed! No more to handle in this page!" % count);
		break;
	count+=1;
	auditbtn.click();
	# waiting for refresh
	WebDriverWait(driver,5).until(EC.presence_of_element_located((By.ID,"button")));
	# extract the necessary info
	name = driver.find_element_by_xpath("html/body/div[2]/div/form/table/tbody/tr[1]/td[2]").text;
	regts = driver.find_element_by_xpath("html/body/div[2]/div/form/table/tbody/tr[1]/td[4]").text;
	cardid = driver.find_element_by_xpath("html/body/div[2]/div/form/table/tbody/tr[3]/td[4]").text;
	selectbox = driver.find_element_by_xpath("html/body/div[2]/div/form/table/tbody/tr[2]/td[4]/select");
	usrtype = Select(selectbox).first_selected_option.text;
	ret = audit(name, cardid, regts, usrtype);
	if ret:
		# pass through
		driver.find_element_by_id("button").click();
		# to-do: setting the expire date.
	else:
		# refused
		driver.find_element_by_link_text("删除").click();
		# wait 1 seconds specially for demo
		time.sleep(1);
		# handle the alert box
		# in fact, we can eliminate this alert by hacking <a>'s code using Javascript
		#alert = driver.switch_to_alert();
		#alert.accept();
		Alert(driver).accept();
	# return back to the original page
	# driver.get(lastpageURL);  # this method will open URL in the Top window
	driver.execute_script("window.location='"+lastpageURL+"';");  # the method of using js is perfect
	WebDriverWait(driver,5).until(EC.presence_of_element_located((By.LINK_TEXT,"最后页")));
	print("[" + ",".join([name,cardid,regts,usrtype]) +"] is processed!");



print("Process "+str(count)+" items successfully, Thank you!");
# come to the end. show 2 seconds for demo
time.sleep(2);
# quit this program
driver.quit();



