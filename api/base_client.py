# Базовый класс с HTTP-методами (GET, POST) и сессиями
# api/base_client.py
import requests


class BaseClient:
    """
    Barcha API-klientlar uchun tayanch (base) klass.
    Barcha HTTP so'rovlar (GET, POST va h.k) shu klass orqali o'tadi.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()

        # Barcha so'rovlar uchun standart sarlavhalarni (Headers) o'rnatish
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Umumiy so'rov yuborish metodi.
        """
        url = f"{self.base_url}{endpoint}"

        # So'rovni amalga oshirish
        response = self.session.request(method, url, **kwargs)

        # Kelajakda bu yerga Allure loggerni qo'shamiz
        # log_api_call(response)

        # Agar server xatolik qaytarsa (masalan 500), konsolga chiqarish uchun yordamchi
        if response.status_code >= 400:
            print(f"XATOLIK ({response.status_code}): {method} {url} -> {response.text}")

        return response

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("PUT", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("DELETE", endpoint, **kwargs)

    def set_auth_token(self, token: str):
        """
        Avtorizatsiyadan so'ng tokenni sessiya sarlavhasiga qo'shish.
        Shundan so'ng barcha so'rovlar avtomatik ushbu token bilan ketadi.
        """
        self.session.headers.update({
            "Authorization": f"Bearer {token}"
        })