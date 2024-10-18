import requests

# URL и заголовки
url = 'https://moscow.birge.ru/include/functions.php'
headers = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'en-KZ,en;q=0.9,ru-KZ;q=0.8,ru;q=0.7,en-GB;q=0.6,en-US;q=0.5',
    'cookie': 'BITRIX_SM_LOGIN=malover15%40yandex.ru; BITRIX_SM_SOUND_LOGIN_PLAYED=Y; PHPSESSID=radif5u1qkk1m8op0v9i29qh77; BITRIX_SM_SALE_UID=24768326; BITRIX_SM_GUEST_ID=47949404; BITRIX_SM_NCC=Y; BITRIX_SM_BANNERS=1_711_28_09102024%2C1_651_8_09102024%2C1_679_8_09102024; BITRIX_SM_LAST_VISIT=02.10.2024+10%3A51%3A02',
    'priority': 'u=1, i',
    'referer': 'https://moscow.birge.ru/personal/my_ads/',
    'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest'
}

# Массив values
values = [873937, 873658, 873390, 852797,884847,884846,884845,865705,884848]

# Функция для выполнения запроса
def send_request(value):
    params = {
        'action': 'update_ads',
        'values': value
    }
    response = requests.get(url, headers=headers, params=params, verify=False)
    
    # Проверка статуса запроса и вывод результата
    if response.status_code == 200:
        print(f"Запрос успешно выполнен для значения {value}: {response.text}")
    else:
        print(f"Ошибка при выполнении запроса для значения {value}: {response.status_code}")

# Цикл по значениям массива
for value in values:
    send_request(value)
