#!/usr/bin/env python3

from selenium import webdriver
from time import sleep

options = webdriver.ChromeOptions()
options.add_argument('window-size=1280x720')

driver = webdriver.Chrome(chrome_options=options)

# Wikipedia is nice because its elements are named cohesively
driver.get("https://en.wikipedia.org/wiki/Main_Page")

# Find search element
search = driver.find_element_by_id('searchInput')

# We obviously need to get a broad list of "snakes" from this search term
# Yet obviously not something scientific, unless we do some wild card random to please the gods
search.send_keys('list of snakes')
driver.find_element_by_id('searchButton').click()

sleep(5)

driver.close()