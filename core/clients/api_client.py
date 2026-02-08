import requests
import os
from dotenv import load_dotenv
from core.settings.environments import Environment
from core.clients.endpoints import Endpoints
from core.settings.config import Users, Timeouts, Ids
from core.schemas.booking_schema import BOOKING_SCHEMA
import allure

load_dotenv()

class APIClient():
    def __init__(self):
        environment_str = os.getenv("ENVIRONMENT")
        try:
            environment = Environment[environment_str]
        except KeyError:
            raise ValueError(f"Unsupported environment value: {environment_str}")

        self.base_url = self.get_base_url(environment)
        self.session = requests.Session()
        self.session.headers = {
            'Content-Type': 'application/json'
        }

    def get_base_url(self, environment: Environment) -> str:
        if environment == Environment.TEST:
            return os.getenv("TEST_BASE_URL")
        elif environment == Environment.PROD:
            return os.getenv("PROD_BASE_URL")
        else:
            raise ValueError(f"Unsupported environment: {environment}")

    def get(self, endpoint, params=None, status_code=200):
        url = self.base_url + endpoint
        response = requests.get(url, headers=self.headers, params=params)
        if status_code:
            assert response.status_code == status_code
        return response.json()

    def post(self, endpoint, data=None, status_code=200):
        url = self.base_url + endpoint
        response = requests.post(url, headers=self.headers, json=data)
        if status_code:
            assert response.status_code == status_code
        return response.json()

    def ping(self):
        with allure.step("Пингуем АПИ клиент"):
            url = f"{self.base_url}{Endpoints.PING_ENDPOINT}"
            response = self.sessipn.get(url)
            response.raise_for_status()
        with allure.step("Проверка статуса ответа"):
            assert response.status_code == 201, f"Ожидали статус 201, но получили {response.status_code}"
        return response.status_code

    def auth(self):
        with allure.step("Отправка запроса аутентификации"):
            url = f"{self.base_url}{Endpoints.AUTH_ENDPOINT}"
            payload = {"username": Users.USERNAME, "password": Users.PASSWORD}
            response = self.session.post(url, json=payload, timeout=Timeouts.TIMEOUT)
            response.raise_for_status()
        with allure.step("Проверка статуса ответа"):
            assert response.status_code == 200, f"Ожидали код ответа 200, а получили {response.status_code}"
        token = response.json().get("token")
        with allure.step("Обновляем хэдер авторизации"):
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def get_booking_by_id(self):
        with allure.step("Делаем запрос для получения информации по id"):
            url = f"{self.base_url}{Endpoints.BOOKING_ENDPOINT}{Ids.ID}"
            response = requests.get(url, headers={"Accept": "application/json"}, timeout=Timeouts.TIMEOUT)
        with allure.step("Проверка статус-кода ответа"):
            assert response.status_code == 200, f"Ожидали код ответа 200, а получили {response.status_code}"
        with allure.step("Проверка, что в боди ответа JSON объект"):
            body = response.json()
            assert isinstance(body, dict)
        with allure.step("Проверка, что объект в ответе содержит нужные поля"):
            expected_keys = {
                "firstname",
                "lastname",
                "totalprice",
                "depositpaid"
            }
            assert expected_keys.issubset(body.keys())
        with allure.step("Проверка ответа на соответствие схеме"):
            jsonschema.validate(response_json, BOOKING_SCHEMA)



