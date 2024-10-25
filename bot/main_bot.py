from typing import Any
from logger import logger
import json, random, string
from datetime import datetime
from aiogram.fsm.state import StatesGroup, State


''' ВРЕМЕННЫЕ ХРАНИЛИЩА ДАННЫХ ПРИ ПОПОЛНЕНИИ '''

pending_payments = {}
pending_payments_info = {}
pending_sending_amount = {}
pending_sending_id = {}
pending_sending_message = {}
pending_sending_info = {}
pending_recieving_info = {}


''' ПОЛУЧЕНИЕ ВРЕМЕНИ '''

async def get_time() -> Any:
    today = datetime.now().strftime('%d.%m.%Y')
    time_now = datetime.now().strftime('%H:%M:%S')
    return today,time_now


''' ОЖИДАНИЕ ИНПУТА ОТ ПОЛЬЗОВАТЕЛЯ '''

class CustomPaymentState(StatesGroup):
    waiting_for_custom_stars_amount = State()
    waiting_for_custom_rub_amount = State()

class SendToFriend(StatesGroup):
    amount_input = State()
    id_input = State()
    message_input = State()

class Support(StatesGroup):
    message_to_support = State()
    answer_message = State()
    continue_application = State()

 
''' ВЗАИМОДЕЙСТВИЕ С БД '''

try:
    with open('database/users_data.json', 'r', encoding='utf-8') as file:
        users_data = json.load(file)
except Exception as e:
    logger.critical(f'Ошибка при загрузке данных: {e}')
    users_data = []

try:
    with open('database/users_payments.json', 'r', encoding='utf-8') as up:
        users_payments = json.load(up)
except Exception as e:
    logger.critical(f'Ошибка при загрузке данных: {e}')
    users_payments = []

try:
    with open('database/total_values.json', 'r', encoding='utf-8') as total:
        total_data = json.load(total)
        total_values = total_data[0]
except Exception as e:
    logger.critical(f'Ошибка при загрузке данных: {e}')
    total_values = {}

try:
    with open('database/user_support.json', 'r', encoding='utf-8') as sup:
        support_data = json.load(sup)
except Exception as e:
    logger.critical(f'Ошибка при загрузке данных: {e}')
    support_data = []


''' УПРОЩЕННОЕ ОБРАЩЕНИЕ К БД '''

users_data_dict = {person['ID']: person for person in users_data}
support_data_dict = {person['ID']: person for person in support_data}
users_payments_dict = {person['ID']: person for person in users_payments}


''' СОХРАНЕНИЕ ДАННЫХ В БД '''

async def save_data() -> Any:
    try:
        with open('database/users_data.json', 'w', encoding='utf-8') as file:
            json.dump(users_data, file, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.critical(f'Ошибка при сохранении данных: {e}')

async def save_payments() -> Any:
    try:
        with open('database/users_payments.json', 'w', encoding='utf-8') as up:
            json.dump(users_payments, up, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.critical(f'Ошибка при сохранении данных: {e}')

async def save_total() -> Any:
    try:
        with open('database/total_values.json', 'w', encoding='utf-8') as total:
            json.dump([total_values], total, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.critical(f'Ошибка при сохранении данных: {e}')

async def save_application() -> Any:
    try:
        with open('database/user_support.json', 'w', encoding='utf-8') as sup:
            json.dump(support_data, sup, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.critical(f'Ошибка при сохранении данных: {e}')


''' ГЕНЕРАТОР ID '''

async def id_generator() -> Any:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=7))
