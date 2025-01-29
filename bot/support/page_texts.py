''' ГЕНЕРАЦИЯ ТЕКСТА СООБЩЕНИЯ '''

async def admin_page_text(number: str, user_id: int, user_message: str, lang: str):
    if lang == 'RU':
        page_text = (f'🆘 <b>Сообщение от пользователя</b>\n<i>Обращение</i> #{number}\n\n'
                f'<b>ID:</b> <code>{user_id}</code>\n\n<b>📩 Сообщение:</b>\n{user_message}')
    else:
        page_text = (f'🆘 <b>Message from user</b>\n<i>Communication</i> #{number}\n\n'
                f'<b>ID:</b> <code>{user_id}</code>\n\n<b>📩 Message:</b>\n{user_message}')
    return page_text
 

async def user_page_text(number: str, answer: str, lang: str):
    if lang == 'RU':
        page_text = (f'🆘 <b>Сообщение от поддержки</b>\n<i>В рамках обращения</i> #{number}\n\n'
                    f'<b>📩 Ответ:\n</b>{answer}')
    else:
        page_text = (f'🆘 <b>Message from support</b>\n<i>In communication</i> #{number}\n\n'
                    f'<b>📩 Answer:\n</b>{answer}')
    return page_text
 