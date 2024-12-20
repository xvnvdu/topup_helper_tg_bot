from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from .save_data import save_answer
from .page_texts import user_page_text, admin_page_text

from logger import logger
from bot.main_bot import Support, get_time, support_data_dict
from bot.bot_buttons import continue_application_keyboard, cancel_answer_keyboard, answer_message_keyboard


''' ОТВЕТ НА СООБЩЕНИЕ '''

async def answer_message(call: CallbackQuery, state: FSMContext):
    await state.set_state(Support.answer_message)
    
    file = call.message.document
    
    user_id = call.data.split('_')[2]
    number = call.data.split('_')[3]
    today = call.data.split('_')[4]
    time_now = call.data.split('_')[5] 
    
    await state.update_data(user_id=user_id)
    await state.update_data(number=number)
    await state.update_data(today=today)
    
    if file is not None:
        await call.message.edit_caption(caption=f'<b>✉️ Ответ на обращение</b> #{number}', parse_mode='HTML', 
                                        reply_markup=cancel_answer_keyboard(user_id, number, today, time_now))
    else:
        await call.message.edit_text(text=f'<b>✉️ Ответ на обращение</b> #{number}', parse_mode='HTML', 
                                        reply_markup=cancel_answer_keyboard(user_id, number, today, time_now))


''' ОТМЕНИТЬ ОТВЕТ '''

async def cancel_answer(call: CallbackQuery, state: FSMContext):    
    user_id = call.data.split('_')[2]
    number = call.data.split('_')[3]
    today = call.data.split('_')[4]
    time_now = call.data.split('_')[5]
    
    file = call.message.document
    
    user_message = support_data_dict[int(user_id)]['Dialogs'][number][today][time_now]['question']
    text = await admin_page_text(number, user_id, user_message)
    
    if file is not None:
        await call.message.edit_caption(caption=text, parse_mode='HTML', 
                                        reply_markup=answer_message_keyboard(user_id, number, today, time_now))
    else:
        await call.message.edit_text(text=text, parse_mode='HTML', 
                                        reply_markup=answer_message_keyboard(user_id, number, today, time_now))
    await state.clear()


''' ОТПРАВКА ОТВЕТА '''

async def send_answer(message: Message, bot: Bot, state: FSMContext):
    file = message.document
    
    doc_id = None
    
    if file is not None:
        doc_id = file.file_id
        answer = message.caption
    else:
        answer = message.text
    
    data = await state.get_data()
    user_id = data.get('user_id')
    number = data.get('number')
    today, time_now = await get_time()
    
    if answer is None:
        answer = ''
    
    text = await user_page_text(number, answer)
    
    logger.info(f'Ответ пользователю {user_id} | Обращение {number}: {answer}')
    
    await save_answer(user_id, number, today, time_now, answer, doc_id)
    
    if doc_id is not None:
        await bot.send_document(chat_id=user_id, document=doc_id, caption=text, parse_mode='HTML', 
                            reply_markup=continue_application_keyboard(user_id, number, today, time_now))
    else:
        await bot.send_message(chat_id=user_id, text=text, parse_mode='HTML', 
                            reply_markup=continue_application_keyboard(user_id, number, today, time_now))

    await message.answer(f'✅ Ответ на обращение #{number} отправлен!')
    
    await state.clear()
    