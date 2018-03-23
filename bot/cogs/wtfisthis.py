#!/usr/bin/env python3

from selenium import webdriver
from time import sleep

options = webdriver.ChromeOptions()
options.add_argument('window-size=1280x720')

driver = webdriver.Chrome(chrome_options=options)

driver.get("https://en.wikipedia.org/wiki/Main_Page")
search = driver.find_element_by_id('searchInput')
search.send_keys('snakes')
driver.find_element_by_id('searchButton').click()

sleep(5)

driver.close()