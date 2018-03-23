#!/usr/bin/env python3

from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_argument('window-size=1280x720')

driver = webdriver.Chrome(chrome_options=options)

# Wikipedia is nice because its elements are named cohesively
driver.get("https://en.wikipedia.org/wiki/Main_Page")

# Find search element
search = driver.find_element_by_id('searchInput')

# We obviously need to get a broad list of "snakes" from this search term
# Yet obviously not something scientific, unless we do some wild card random to please the gods
search.send_keys('list of snakes by common name')
driver.find_element_by_id('searchButton').click()

# Now we build some cool shit to scrape a bunch of snakes!
# From a FUCKING MASSIVE list of shite
result = driver.find_element_by_class_name('mw-parser-output')

# So we're pulling the UL out of the above div
newresults = result.find_elements_by_tag_name("ul")

# Now we're just iterating over that and pulling the text element to see it works
for each in newresults:
    print(each.text)

driver.close()
