import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

# Установка пути к драйверу браузера (например, Chrome)
driver = webdriver.Chrome()

# Открытие сайта
driver.get('http://jerdesh.ru/')

tel_jerdesh = os.getenv('tel_jerdesh')
pass_jerdesh = os.getenv('pass_jerdesh')

# Вход на сайт (если требуется)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'login_open'))).click()
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'tel'))).send_keys(tel_jerdesh)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[text()="Далее"]'))).click()
next = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'password'))).send_keys(pass_jerdesh)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[text()="Войти"]'))).click()
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//a[text()="Мои объявления"]'))).click()
# Поиск и нажатие кнопки "Поднять объявление"
while True:
    try:
        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a[@class="del_button"]'))
        )
        button.click()
        print('Объявление поднято!')
        time.sleep(4 * 60 * 60)  # Пауза в 4 часа
    except:
        print('Кнопка "Поднять объявление" не найдена. Производится перезагрузка страницы...')
        driver.refresh()

# Закрытие браузера
driver.quit()
