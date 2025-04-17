from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

driver.get("http://localhost:5000/login")
time.sleep(1)

driver.find_element(By.NAME, "username").send_keys("Serhiy2512")
driver.find_element(By.NAME, "password").send_keys("5555")
driver.find_element(By.XPATH, "//button[@type='submit']").click()

time.sleep(1)
driver.get("http://localhost:5000/profile")


lastname = driver.find_element(By.ID, "lastname").text
firstname = driver.find_element(By.ID, "firstname").text
print(f"Full name is {firstname} {lastname}")

driver.quit()
