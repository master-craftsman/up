import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions

# Установка пути к драйверу браузера (например, Chrome)
options = ChromeOptions()
# options.add_argument("--headless=new")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
options.add_argument("--window-size=1920,1080")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Использование webdriver-manager для автоматической установки драйвера
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

# driver = webdriver.Chrome()


# Открытие сайта
driver.get('https://moscow.birge.ru/')

email_birge = os.getenv('EMAIL_BIRGE')
pass_birge = os.getenv('PASS_BIRGE')

# Вход на сайт (если требуется)
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Логин/Email" and @class="login"]'))).send_keys(email_birge)
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Пароль" and @class="pass"]'))).send_keys(pass_birge)
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//input[@value="Войти" and @class="submit"]'))).click()
driver.get('https://moscow.birge.ru/personal/my_ads/')
# WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//a[text()="Мой кабинет"]'))).click()

attempts = 0  # Счётчик попыток
max_attempts = 5  # Максимальное количество попыток

# Поиск и нажатие кнопок "Поднять объявление"
while True:
    try:
        buttons = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, '//i[@class="fa fa-refresh reload-link"]'))
        )
        for button in buttons:
            # button.click()
            print('Объявление поднято!')
        break
        # time.sleep(4 * 60 * 60)  # Пауза в 4 часа
    except Exception as e:
        # Если кнопки не найдены или возникла ошибка
        print(f'Ошибка: {e}')
        print('Кнопка "Поднять объявление" не найдена')
        attempts += 1
        if attempts >= max_attempts:
            print('Достигнуто максимальное количество попыток, выходим из цикла.')
            break  # Выходим из цикла после нескольких неудачных попыток

driver.save_screenshot('screenshot.png')
print(driver.page_source)
# Закрытие браузера
driver.quit()
