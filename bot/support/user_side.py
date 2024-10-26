import asyncio

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from .save_data import save_question
from .page_texts import user_page_text, admin_page_text

from config import admin
from logger import logger
from bot.main_bot import Support, get_time, support_data_dict, id_generator
from bot.bot_buttons import continue_application_keyboard, answer_message_keyboard, support_keyboard, cancel_application_keyboard


user_locks = {}


''' ГЛАВНАЯ СТРАНИЦА РАЗДЕЛА ПОДДЕРЖКИ '''

async def bot_support(call: CallbackQuery):
    await call.message.edit_text('<strong>Поддержка TopUp Helper 🤖</strong>\n\n'
                                 '<b>Здесь вы можете оставить свое сообщение, если:</b>\n'
                                 '🐞 <i>Столкнулись с багом\n'
                                 '⛓️‍💥 Обнаружили уязвимость\n'
                                 '🛠 Возникли проблемы с работой бота\n'
                                 '💬 Есть идеи и предложения по улучшению\n'
                                 '❔ Появились вопросы (любые, касательно бота)</i>\n\n'
                                 '❗️Рекомендуется ознакомиться с правилами ниже', parse_mode='HTML', 
                                 reply_markup=support_keyboard)
    

''' ОТПРАВКА НОВОГО СООБЩЕНИЯ В ПОДДЕРЖКУ '''

async def message_to_support(message: Message, bot: Bot, state: FSMContext):
    user_id = message.from_user.id
    file = message.document
    doc_id = None
    
    if user_id not in user_locks:
        user_locks[user_id] = asyncio.Lock()
    
    if user_locks[user_id].locked():
        return
    
    async with user_locks[user_id]:
        if file is not None:
            doc_id = file.file_id
            user_message = message.caption
        else:
            user_message = message.text
        
        number = await id_generator()
        
        logger.info(f'Новое сообщение от пользователя {user_id} | Обращение {number}: {user_message}')
        
        if user_message is None:
            user_message = ''
        
        text = await admin_page_text(number, user_id, user_message)
        today, time_now = await get_time()
        
        await save_question(user_id, number, today, time_now, user_message, doc_id)
            
        await message.answer(f'✅ <b>Сообщение отправлено!</b> #{number}\n<i>Поддержка свяжется с вами в ближайшее время.\n'
                            'Не рекомендуется создавать новые обращения по одному вопросу, дождитесь ответа и, '
                            'при необходимости, продолжайте диалог в рамках одного обращения.</i>', parse_mode='HTML')
        await state.clear()
        
        if doc_id is not None:
            await bot.send_document(chat_id=admin, document=doc_id, caption=text, parse_mode='HTML', 
                                reply_markup=answer_message_keyboard(user_id, number, today, time_now))
        else:
            await bot.send_message(chat_id=admin, text=text, parse_mode='HTML', 
                                    reply_markup=answer_message_keyboard(user_id, number, today, time_now))
    del user_locks[user_id]
    
    
''' ПРОДОЛЖИТЬ ДИАЛОГ В РАМКАХ ОБРАЩЕНИЯ '''
    
async def continue_application(call: CallbackQuery, state: FSMContext):
    await state.set_state(Support.continue_application)
    
    file = call.message.document
    
    user_id = call.data.split('_')[2]
    number = call.data.split('_')[3]
    today = call.data.split('_')[4]
    time_now = call.data.split('_')[5]
    
    await state.update_data(user_id=user_id)
    await state.update_data(number=number)
    await state.update_data(today=today)
    
    if file is not None:
        await call.message.edit_caption(caption=f'<b>✉️ Сообщение в рамках обращения</b> #{number}', parse_mode='HTML', 
                                        reply_markup=cancel_application_keyboard(user_id, number, today, time_now))
    else:
        await call.message.edit_text(text=f'<b>✉️ Сообщение в рамках обращения</b> #{number}', parse_mode='HTML', 
                                     reply_markup=cancel_application_keyboard(user_id, number, today, time_now))
    
    
 
''' ОТМЕНИТЬ ОТПРАВКУ СООБЩЕНИЯ ПРИ ПРОДОЛЖЕНИИ ДИАЛОГА '''
 
async def cancel_application(call: CallbackQuery, state: FSMContext):
    user_id = call.data.split('_')[2]
    number = call.data.split('_')[3]
    today = call.data.split('_')[4]
    time_now = call.data.split('_')[5]
    
    file = call.message.document
    
    support_message = support_data_dict[int(user_id)]['Dialogs'][number][today][time_now]['answer']
    text = await user_page_text(number, support_message)
    
    if file is not None:
        await call.message.edit_caption(caption=text, parse_mode='HTML', 
                                        reply_markup=continue_application_keyboard(user_id, number, today, time_now))
    else:
        await call.message.edit_text(text=text, parse_mode='HTML', 
                                     reply_markup=continue_application_keyboard(user_id, number, today, time_now))
    
    await state.clear()
 
 
''' ОТПРАВИТЬ СООБЩЕНИЕ В РАМКАХ ОБРАЩЕНИЯ '''
 
async def send_application(message: Message, bot: Bot, state: FSMContext):
    user_id = message.from_user.id
    file = message.document
    doc_id = None
    
    if user_id not in user_locks:
        user_locks[user_id] = asyncio.Lock()
    
    if user_locks[user_id].locked():
        return
    
    async with user_locks[user_id]:  
        if file is not None:
            doc_id = file.file_id
            application = message.caption
        else:
            application = message.text

        data = await state.get_data()
        user_id = int(data.get('user_id'))
        number = data.get('number')
        today, time_now = await get_time()

        if application is None:
            application = ''

        text = await admin_page_text(number, user_id, application)

        logger.info(f'Сообщение от пользователя {user_id} | Обращение {number}: {application}')

        await save_question(user_id, number, today, time_now, application, doc_id)


        if doc_id is not None:
            await bot.send_document(chat_id=admin, document=doc_id, caption=text, parse_mode='HTML', 
                                reply_markup=answer_message_keyboard(user_id, number, today, time_now))
        else:
            await bot.send_message(chat_id=admin, text=text, parse_mode='HTML', 
                                reply_markup=answer_message_keyboard(user_id, number, today, time_now))

        await message.answer(f'✅ Ответ в рамках обращения #{number} отправлен!')
        await state.clear()
        
    del user_locks[user_id]
    