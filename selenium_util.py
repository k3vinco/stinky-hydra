from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Get text of unique element by searching for class
def getElementTextByClass(driver, url, className):
	
	try:
		driver.get(url)

		#Wait for element
		element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, className)))

		#Store the title
		elementText = self.driver.find_element_by_class_name(className).text

		return elementText

	except TimeoutException:
		return("ERROR: Timed out")