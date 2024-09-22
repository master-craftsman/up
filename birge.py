import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
import os

# Установка пути к драйверу браузера (например, Chrome)
options = ChromeOptions()
options.add_argument("--headless=new")
driver = webdriver.Chrome(options=options)

# Открытие сайта
driver.get('https://moscow.birge.ru/')

email_birge = os.getenv('EMAIL_BIRGE')
pass_birge = os.getenv('PASS_BIRGE')

# Вход на сайт (если требуется)
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Логин/Email" and @class="login"]'))).send_keys(email_birge)
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Пароль" and @class="pass"]'))).send_keys(pass_birge)
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//input[@value="Войти" and @class="submit"]'))).click()
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//a[text()="Мой кабинет"]'))).click()

# Поиск и нажатие кнопок "Поднять объявление"
while True:
    try:
        buttons = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//i[@class="fa fa-refresh reload-link"]'))
        )
        for button in buttons:
            button.click()
            print('Объявление поднято!')
        # button.click()
        time.sleep(4 * 60 * 60)  # Пауза в 4 часа
    except:
        print('Кнопка "Поднять объявление" не найдена. Производится перезагрузка страницы...')
        driver.refresh()

# Закрытие браузера
driver.quit()
