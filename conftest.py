# conftest.py
import os
import pytest
from dotenv import load_dotenv
from api.base_client import BaseClient

load_dotenv()


@pytest.fixture(scope="session")
def base_url():
    return os.getenv("BASE_URL")


@pytest.fixture(scope="session")
def get_token():
    return os.getenv("STATIC_BEARER_TOKEN")


@pytest.fixture(scope="session")
def authorized_api_client(base_url, get_token):
    # """
    # Bu fikshtura barcha API testlar uchun tayyor, avtorizatsiyadan o'tgan
    # BaseClient obyektini qaytaradi.
    # """
    # # 1. Ehtiyojga qarab login URL va test INN ni olamiz
    # login_url = "https://test-app.ebirja.uz/uz/auth/open-auth-loginkey"  # Haqiqiy login sahifa URL'i
    # buyurtmachi_inn = os.getenv("TEST_BUYURTMACHI_INN")
    #
    # # 2. UI orqali tokenni olamiz (faqat 1 marta bajariladi)
    # token = get_token_via_eimzo(login_url=login_url, inn=buyurtmachi_inn, pin_code="1")

    # 3. BaseClient ni yaratamiz va unga tokenni o'rnatamiz
    client = BaseClient(base_url)
    client.set_auth_token(get_token)

    return client