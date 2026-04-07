# tests/api/test_profile.py
import os


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
