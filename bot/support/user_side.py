from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from .save_data import save_question
from .page_texts import user_page_text, admin_page_text

from config import admin
from logger import logger
from bot.main_bot import Support, get_time, support_data_dict, id_generator
from bot.bot_buttons import continue_application_keyboard, answer_message_keyboard, support_keyboard, cancel_application_keyboard


async def bot_support(call: CallbackQuery):
    await call.message.edit_text('<strong>Поддержка TopUp Helper 🤖</strong>\n\n'
                                 '<b>Здесь вы можете оставить свое сообщение, если:</b>\n'
                                 '🐞 <i>Столкнулись с багом\n'
                                 '⛓️‍💥 Обнаружили уязвимость\n'
                                 '🛠 Возникли проблемы с работой бота\n'
                                 '💬 Есть идеи и предложения по улучшению\n'
                                 '❔ Появились вопросы (любые, касательно бота)</i>', parse_mode='HTML', 
                                 reply_markup=support_keyboard)
    

async def message_to_support(message: Message, bot: Bot, state: FSMContext):
    user_id = message.from_user.id
    user_message = message.text
    
    number = await id_generator()
    
    logger.info(f'Новое сообщение от пользователя {user_id} | Обращение {number}: {user_message}')
    
    text = await admin_page_text(number, user_id, user_message)
    today, time_now = await get_time()
    
    await save_question(user_id, number, today, time_now, user_message)
        
    await message.answer(f'✅ <b>Сообщение отправлено!</b> #{number}\n<i>Поддержка свяжется с вами в ближайшее время.\n'
                         'Не рекомендуется создавать новые обращения по одному вопросу, дождитесь ответа и, '
                         'при необходимости, продолжайте диалог в рамках одного обращения.</i>', parse_mode='HTML')
    await state.clear()
    
    await bot.send_message(chat_id=admin, text=text, parse_mode='HTML', reply_markup=answer_message_keyboard(user_id, number, today, time_now))
    
    
async def continue_application(call: CallbackQuery, state: FSMContext):
    await state.set_state(Support.continue_application)
    
    user_id = call.data.split('_')[2]
    number = call.data.split('_')[3]
    today = call.data.split('_')[4]
    time_now = call.data.split('_')[5]
    
    await state.update_data(user_id=user_id)
    await state.update_data(number=number)
    await state.update_data(today=today)
    
    await call.message.edit_text(f'<b>✉️ Сообщение в рамках обращения #{number}</b>', parse_mode='HTML', 
                                 reply_markup=cancel_application_keyboard(user_id, number, today, time_now))
 
 
async def cancel_application(call: CallbackQuery, state: FSMContext):
    user_id = call.data.split('_')[2]
    number = call.data.split('_')[3]
    today = call.data.split('_')[4]
    time_now = call.data.split('_')[5]
    
    support_message = support_data_dict[int(user_id)]['Dialogs'][number][today][time_now]['answer']
    text = await user_page_text(number, support_message)
    
    await call.message.edit_text(text, parse_mode='HTML', reply_markup=continue_application_keyboard(user_id, number, today, time_now))
    await state.clear()
 
 
async def send_application(message: Message, bot: Bot, state: FSMContext):
	application = message.text

	data = await state.get_data()
	user_id = int(data.get('user_id'))
	number = data.get('number')
	today, time_now = await get_time()

	text = await admin_page_text(number, user_id, application)

	logger.info(f'Сообщение от пользователя {user_id} | Обращение {number}: {application}')

	await save_question(user_id, number, today, time_now, application)

	await bot.send_message(chat_id=admin, text=text, parse_mode='HTML', reply_markup=answer_message_keyboard(user_id, number, today, time_now))
	await message.answer(f'✅ Ответ в рамках обращения #{number} отправлен!')

	await state.clear()
    