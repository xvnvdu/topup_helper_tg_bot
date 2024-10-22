from typing import Any
import json, random, string
from datetime import datetime
from aiogram.fsm.state import StatesGroup, State


pending_payments = {}
pending_payments_info = {}
pending_sending_amount = {}
pending_sending_id = {}
pending_sending_message = {}
pending_sending_info = {}
pending_recieving_info = {}


async def get_time() -> Any:
    today = datetime.now().strftime('%d.%m.%Y')
    time_now = datetime.now().strftime('%H:%M:%S')
    return today,time_now


class CustomPaymentState(StatesGroup):
    waiting_for_custom_stars_amount = State()
    waiting_for_custom_rub_amount = State()


class SendToFriend(StatesGroup):
    amount_input = State()
    id_input = State()
    message_input = State()

 
try:
    with open('database/users_data.json', 'r', encoding='utf-8') as file:
        users_data = json.load(file)
except Exception as e:
    print(f"Ошибка при загрузке данных: {e}")
    users_data = []

try:
    with open('database/users_payments.json', 'r', encoding='utf-8') as up:
        users_payments = json.load(up)
except Exception as e:
    print(f"Ошибка при загрузке данных: {e}")
    users_payments = []

try:
    with open('database/total_values.json', 'r', encoding='utf-8') as total:
        total_data = json.load(total)
        total_values = total_data[0]
except Exception as e:
    print(f"Ошибка при загрузке данных: {e}")
    total_values = {}


users_data_dict = {person['ID']: person for person in users_data}
users_payments_dict = {person['ID']: person for person in users_payments}


async def save_data() -> Any:
    try:
        with open('database/users_data.json', 'w', encoding='utf-8') as file:
            json.dump(users_data, file, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}")

async def save_payments() -> Any:
    try:
        with open('database/users_payments.json', 'w', encoding='utf-8') as up:
            json.dump(users_payments, up, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}")

async def save_total() -> Any:
    try:
        with open('database/total_values.json', 'w', encoding='utf-8') as total:
            json.dump([total_values], total, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}")


async def id_generator() -> Any:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=7))
