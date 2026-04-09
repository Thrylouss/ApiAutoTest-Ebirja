# tests/api/test_profile.py
import os
import random
import pytest
import json
from utils.test_test import get_signed_pkcs7

eimzo_id = os.getenv("EIMZO-ID")

def test_get_my_profile(authorized_api_client):
    """
    Avtorizatsiya to'g'ri ishlagani va token yaroqli ekanligini
    profil ma'lumotlarini olish orqali tekshiramiz.
    """
    # E-birja API dagi profilni oladigan endpointni yozasiz (masalan /users/me)
    response = authorized_api_client.get("/auth/user/me")

    assert response.status_code == 200
    print("\nAPI test muvaffaqiyatli o'tdi! Ma'lumotlar olindi.")


def test_get_phone_list(authorized_api_client):
    response = authorized_api_client.get("/common/company/phone-list")
    assert response.status_code == 200
    print("Phone List success")


def test_get_bank_account(authorized_api_client):
    response = authorized_api_client.get("/common/company/bank-account?expand=bank&currentPage=0&perPage=10&expand=bank")
    assert response.status_code == 200
    print("Bank account success")


# Добавляем маркер, чтобы pytest знал, что это асинхронный тест
@pytest.mark.asyncio
async def test_create_bank_account(authorized_api_client):
    fixed = "34531323"

    # Генерируем случайный номер счета
    prefix = ''.join([str(random.randint(0, 9)) for _ in range(9)])
    suffix = ''.join([str(random.randint(0, 9)) for _ in range(3)])
    account_number = f"{prefix}{fixed}{suffix}"

    # Данные для подписи
    data_to_sign = {
        "account_number": account_number,
        "mfo": "00001",
        "is_main": "1",
        "eimzoId": "1e74cd4132feb98364e46344ca8afd5b"  # Не забудь определить или получить eimzo_id
    }

    # ИСПРАВЛЕНИЕ: Добавляем await, чтобы дождаться выполнения функции и получить строку PKCS7
    # Также передай все нужные аргументы, если функция их требует (pin_code и т.д.)
    final_pkcs7 = await get_signed_pkcs7(data_to_sign, pin_code="1")

    json_payload = {
        "pkcs7": final_pkcs7,
        "account_number": account_number,
        "mfo": "00001",  # Исправил "0001" на "00001" для соответствия data_to_sign
        "is_main": "1"
    }

    # Если твой authorized_api_client синхронный (requests), вызываем обычно.
    # Если асинхронный (httpx), тоже добавь await
    response = authorized_api_client.post("/common/company/add-bank-account", json=json_payload)

    assert response.status_code == 200
    print("Create bank account success")
