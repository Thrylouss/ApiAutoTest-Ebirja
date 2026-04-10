# tests/api/test_schedule.py
import os
import pytest
from utils.test_test import get_signed_pkcs7

eimzo_id = os.getenv("EIMZO-ID")

@pytest.fixture
def plan_item_id(authorized_api_client):
    response = authorized_api_client.get("/common/plan-schedule/index?currentPage=0&perPage=10&status=300&expand=isUsed")
    assert response.status_code == 200
    data = response.json()["result"]["data"]
    if not data:
        pytest.skip("Список планов пуст")
    return data[0]["id"]

def test_get_plan_schedule(authorized_api_client, plan_item_id):
    assert plan_item_id is not None

def test_get_view_plan_schedule(authorized_api_client, plan_item_id):
    response = authorized_api_client.get(
        f"/common/plan-schedule/view?id={plan_item_id}&expand=planScheduleClassifiers.classifier,isUsed"
    )
    assert response.status_code == 200