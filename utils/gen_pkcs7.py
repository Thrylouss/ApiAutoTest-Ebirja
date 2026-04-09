import asyncio
import os
import random
import websockets
import json
import base64
import pyautogui
import httpx  # Установите через pip install httpx
from dotenv import load_dotenv

load_dotenv()

# Настройки стенда
BASE_URL = os.getenv("BASE_URL")  # Замените на ваш актуальный домен
AUTH_TOKEN = "FmF6Syb9FOCGMNI_wT5ODTwEw0k_i99s"  # Токен из заголовка Authorization


async def sign_with_eimzo(challenge_text: str, pin_code: str = "1"):
    uri = "ws://127.0.0.1:64646/service/cryptapi"
    target_file_name = "Кибрай клиник З"

    async with websockets.connect(uri, origin="http://127.0.0.1") as ws:
        # 1. Получаем список сертификатов
        await ws.send(json.dumps({
            "plugin": "pfx",
            "name": "list_all_certificates"
        }))
        list_response = json.loads(await ws.recv())

        keys = list_response.get("certificates") or list_response.get("item", [])
        target_key = next((k for k in keys if k.get("name") == target_file_name), None)

        if not target_key:
            raise Exception(f"Ключ '{target_file_name}' не найден!")

        # 2. Загружаем ключ
        await ws.send(json.dumps({
            "plugin": "pfx",
            "name": "load_key",
            "arguments": [
                target_key.get("disk"),
                target_key.get("path"),
                target_key.get("name"),
                target_key.get("alias")
            ]
        }))

        load_response = json.loads(await ws.recv())
        key_id = load_response.get("keyId")

        # 3. Создаем базовый PKCS#7
        challenge_b64 = base64.b64encode(challenge_text.encode('utf-8')).decode('utf-8')
        await ws.send(json.dumps({
            "plugin": "pkcs7",
            "name": "create_pkcs7",
            "arguments": [challenge_b64, key_id, "no"]
        }))

        # Ожидание и ввод пароля
        await asyncio.sleep(1.5)
        pyautogui.write(pin_code)
        pyautogui.press('enter')

        pkcs7_response = json.loads(await ws.recv())
        return pkcs7_response.get("pkcs7_64")


async def main():
    # ДАННЫЕ ДЛЯ ДОБАВЛЕНИЯ СЧЕТА
    # Фиксированная часть
    fixed = "34531323"

    # Генерируем 9 случайных цифр для начала и 3 для конца
    prefix = ''.join([str(random.randint(0, 9)) for _ in range(9)])
    suffix = ''.join([str(random.randint(0, 9)) for _ in range(3)])

    # account_number = f"{prefix}{fixed}{suffix}"
    account_number = "12122112134531323555"
    mfo = "00001"
    is_main = 1

    # 1. ПОЛУЧЕНИЕ FRESH EIMZO_ID (CHALLENGE)
    # В реальном тесте этот ID нужно получить от сервера (GET запрос на эндпоинт челленджа)
    # Если он у вас уже есть, используем его:
    eimzo_id = "1e74cd4132feb98364e46344ca8afd5b"

    # 2. ФОРМИРУЕМ СТРОКУ ДЛЯ ПОДПИСИ (Строго по формату бэкенда)
    data_to_sign = {
        "account_number": account_number,
        "mfo": mfo,
        "is_main": is_main,
        "eimzoId": eimzo_id
    }
    # Компактный JSON без пробелов
    json_to_sign = json.dumps(data_to_sign, separators=(',', ':'))

    # 3. ПОДПИСЫВАЕМ ЛОКАЛЬНО
    print("--- Шаг 1: Подписание в E-IMZO ---")
    raw_pkcs7 = await sign_with_eimzo(json_to_sign, pin_code="1")

    # 4. ПОЛУЧАЕМ TIMESTAMP ОТ СЕРВЕРА
    print("--- Шаг 2: Получение метки времени (Timestamper) ---")
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}

    async with httpx.AsyncClient() as client:
        # Отправляем сырую подпись на сервис штампов времени
        ts_res = await client.post(
            f"{BASE_URL}/auth/user/frontend-timestamp",
            json={"pkcs7": raw_pkcs7},
            headers=headers
        )

        if ts_res.status_code != 200:
            print(f"Ошибка Timestamper: {ts_res.text}")
            return

        # Получаем усиленный PKCS7 из поля 'result' (как в вашем JS коде)
        final_pkcs7 = ts_res.json().get("result")
        print("Метка времени успешно получена.")

        # 5. ФИНАЛЬНЫЙ ЗАПРОС: ДОБАВЛЕНИЕ БАНКОВСКОГО АККАУНТА
        print("--- Шаг 3: Отправка запроса на добавление счета ---")
        bank_payload = {
            "pkcs7": final_pkcs7,
            "account_number": account_number,
            "mfo": mfo,
            "is_main": is_main
        }

        # Эндпоинт добавления счета (уточните в Swagger)
        add_account_url = f"{BASE_URL}/common/company/add-bank-account"

        final_res = await client.delete(
            add_account_url,
            json=bank_payload,
            headers=headers
        )

        print(f"Статус ответа: {final_res.status_code}")
        print(f"Тело ответа: {final_res.text}")