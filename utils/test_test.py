import asyncio
import os
import json
import base64
import websockets
import pyautogui
import httpx
from dotenv import load_dotenv

load_dotenv()

# Настройки
BASE_URL = os.getenv("BASE_URL")
AUTH_TOKEN = os.getenv("STATIC_BEARER_TOKEN")
TARGET_KEY_NAME = "Кибрай клиник З"


# 1. Низкоуровневая подпись (WebSocket)
async def raw_sign(challenge_text: str, pin_code: str, target_file_name: str):
    uri = "ws://127.0.0.1:64646/service/cryptapi"
    async with websockets.connect(uri, origin="http://127.0.0.1") as ws:
        await ws.send(json.dumps({"plugin": "pfx", "name": "list_all_certificates"}))
        list_response = json.loads(await ws.recv())
        keys = list_response.get("certificates") or list_response.get("item", [])

        target_key = next((k for k in keys if k.get("name") == target_file_name), None)
        if not target_key:
            raise Exception(f"Ключ '{target_file_name}' не найден!")

        await ws.send(json.dumps({
            "plugin": "pfx", "name": "load_key",
            "arguments": [target_key['disk'], target_key['path'], target_key['name'], target_key['alias']]
        }))

        key_id = json.loads(await ws.recv()).get("keyId")
        challenge_b64 = base64.b64encode(challenge_text.encode('utf-8')).decode('utf-8')

        await ws.send(json.dumps({
            "plugin": "pkcs7", "name": "create_pkcs7",
            "arguments": [challenge_b64, key_id, "no"]
        }))

        await asyncio.sleep(1.5)
        pyautogui.write(pin_code)
        pyautogui.press('enter')

        res = json.loads(await ws.recv())
        return res.get("pkcs7_64")


# 2. ГЛАВНАЯ ФУНКЦИЯ: Подпись + Timestamper (Обертка)
async def get_signed_pkcs7(payload: dict, pin_code: str = '1'):
    """
    Принимает словарь, подписывает его и возвращает PKCS7 с меткой времени.
    """
    json_string = json.dumps(payload, separators=(',', ':'))

    # Сначала получаем сырую подпись
    raw_pkcs7 = await raw_sign(json_string, pin_code, TARGET_KEY_NAME)

    # Затем сразу идем за меткой времени
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    async with httpx.AsyncClient(verify=False) as client:
        ts_res = await client.post(
            f"{BASE_URL}/auth/user/frontend-timestamp",
            json={"pkcs7": raw_pkcs7},
            headers=headers
        )
        if ts_res.status_code != 200:
            raise Exception(f"Ошибка Timestamper: {ts_res.text}")

        return ts_res.json().get("result")