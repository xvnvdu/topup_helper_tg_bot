''' ГЕНЕРАЦИЯ ТЕКСТА СООБЩЕНИЯ '''

async def admin_page_text(number: str, user_id: int, user_message: str):
    page_text = (f'🆘 <b>Сообщение от пользователя</b>\n<i>Обращение</i> #{number}\n\n'
            f'<b>ID:</b> <code>{user_id}</code>\n\n<b>📩Сообщение:</b>\n{user_message}')
    return page_text
 

async def user_page_text(number: str, answer: str):
    page_text = (f'🆘 <b>Сообщение от поддержки</b>\n<i>В рамках обращения</i> #{number}\n\n'
                 f'<b>📩 Ответ:\n</b>{answer}')
    return page_text
 