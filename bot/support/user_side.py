import asyncio

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from .save_data import save_question
from .page_texts import user_page_text, admin_page_text

from config import admin
from logger import logger
from bot.interface_language.core import phrases
from bot.main_bot import Support, get_time, support_data_dict, id_generator, users_data_dict
from bot.bot_buttons import continue_application_keyboard, answer_message_keyboard, support_keyboard, cancel_application_keyboard


user_locks = {}


''' ГЛАВНАЯ СТРАНИЦА РАЗДЕЛА ПОДДЕРЖКИ '''

async def bot_support(call: CallbackQuery):
    user_id = call.from_user.id
    user_data = users_data_dict[user_id]
    lang = user_data['Language']
    lang_settings = phrases(lang)
    
    await call.message.edit_text(lang_settings.support_main_page, parse_mode='HTML', reply_markup=support_keyboard(lang))
    

''' ОТПРАВКА НОВОГО СООБЩЕНИЯ В ПОДДЕРЖКУ '''

async def message_to_support(message: Message, bot: Bot, state: FSMContext):
    user_id = message.from_user.id
    user_data = users_data_dict[user_id]
    lang = user_data['Language']
    
    admin_data = users_data_dict[admin]
    admin_lang = admin_data['Language']
    
    lang_settings = phrases(lang)
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
        
        text = await admin_page_text(number, user_id, user_message, admin_lang)
        today, time_now = await get_time()
        
        await save_question(user_id, number, today, time_now, user_message, doc_id)
            
        await message.answer(f'{lang_settings.support_message_delivered} #{number}\n\n'
                             f'{lang_settings.support_message_delivered_recommendation}', parse_mode='HTML')
        await state.clear()
        
        if doc_id is not None:
            await bot.send_document(chat_id=admin, document=doc_id, caption=text, parse_mode='HTML', 
                                reply_markup=answer_message_keyboard(user_id, number, today, time_now, admin_lang))
        else:
            await bot.send_message(chat_id=admin, text=text, parse_mode='HTML', 
                                    reply_markup=answer_message_keyboard(user_id, number, today, time_now, admin_lang))
    del user_locks[user_id]
    
    
''' ПРОДОЛЖИТЬ ДИАЛОГ В РАМКАХ ОБРАЩЕНИЯ '''
    
async def continue_application(call: CallbackQuery, state: FSMContext):
    await state.set_state(Support.continue_application)
    
    file = call.message.document
    
    user_id = call.data.split('_')[2]
    number = call.data.split('_')[3]
    today = call.data.split('_')[4]
    time_now = call.data.split('_')[5]
    
    user_data = users_data_dict[int(user_id)]
    lang = user_data['Language']
    lang_settings = phrases(lang)
    
    await state.update_data(user_id=user_id)
    await state.update_data(number=number)
    await state.update_data(today=today)
    
    if file is not None:
        await call.message.edit_caption(caption=f'{lang_settings.communication_reference} #{number}', parse_mode='HTML', 
                                        reply_markup=cancel_application_keyboard(user_id, number, today, time_now, lang))
    else:
        await call.message.edit_text(text=f'{lang_settings.communication_reference} #{number}', parse_mode='HTML', 
                                     reply_markup=cancel_application_keyboard(user_id, number, today, time_now, lang))
    
    
 
''' ОТМЕНИТЬ ОТПРАВКУ СООБЩЕНИЯ ПРИ ПРОДОЛЖЕНИИ ДИАЛОГА '''
 
async def cancel_application(call: CallbackQuery, state: FSMContext):
    user_id = call.data.split('_')[2]
    number = call.data.split('_')[3]
    today = call.data.split('_')[4]
    time_now = call.data.split('_')[5]
    
    user_data = users_data_dict[int(user_id)]
    lang = user_data['Language']
    
    file = call.message.document
    
    support_message = support_data_dict[int(user_id)]['Dialogs'][number][today][time_now]['answer']
    text = await user_page_text(number, support_message, lang)
    
    if file is not None:
        await call.message.edit_caption(caption=text, parse_mode='HTML', 
                                        reply_markup=continue_application_keyboard(user_id, number, today, time_now, lang))
    else:
        await call.message.edit_text(text=text, parse_mode='HTML', 
                                     reply_markup=continue_application_keyboard(user_id, number, today, time_now, lang))
    
    await state.clear()
 
 
''' ОТПРАВИТЬ СООБЩЕНИЕ В РАМКАХ ОБРАЩЕНИЯ '''
 
async def send_application(message: Message, bot: Bot, state: FSMContext):
    user_id = message.from_user.id
    user_data = users_data_dict[user_id]
    lang = user_data['Language']
    
    admin_data = users_data_dict[admin]
    admin_lang = admin_data['Language']
    
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

        text = await admin_page_text(number, user_id, application, admin_lang)

        logger.info(f'Сообщение от пользователя {user_id} | Обращение {number}: {application}')

        await save_question(user_id, number, today, time_now, application, doc_id)


        if doc_id is not None:
            await bot.send_document(chat_id=admin, document=doc_id, caption=text, parse_mode='HTML', 
                                reply_markup=answer_message_keyboard(user_id, number, today, time_now, admin_lang))
        else:
            await bot.send_message(chat_id=admin, text=text, parse_mode='HTML', 
                                reply_markup=answer_message_keyboard(user_id, number, today, time_now, admin_lang))

        if lang == 'RU':
            await message.answer(f'✅ Ответ в рамках обращения #{number} отправлен!')
        else:
            await message.answer(f'✅ Answer in communication #{number} is sent!')
        await state.clear()
        
    del user_locks[user_id]
    