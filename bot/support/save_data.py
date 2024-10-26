from bot.main_bot import support_data_dict, support_data, save_application


''' СОХРАНЕНИЕ ОБРАЩЕНИЯ В БД '''

async def save_question(user_id: int, number: str, today: str, time_now: str, user_message: str, document: str):
    if user_id not in support_data_dict:
        user = {
            'ID': user_id,
            'Dialogs': {
                number: {
                    today: {
                        time_now: {
                            'question': user_message,
                            'document': document
                        }
                    }
                }
            }
        }
        support_data.append(user)
        support_data_dict[user_id] = user
    else:
        dialogs = support_data_dict[int(user_id)]['Dialogs'] 
        if number not in dialogs:
            dialogs[number] = {
                today: {
                    time_now: {
                        'question': user_message,
                        'document': document
                    }
                }
            }
        else:
            if today not in dialogs[number]:
                dialogs[number][today] = {
                    time_now: {
                        'question': user_message,
                        'document': document
                    }
                }
            else:
                dialogs[number][today][time_now] = {
                    'question': user_message,
                    'document': document
                }
    await save_application()
    

''' СОХРАНЕНИЕ ОТВЕТА НА ОБРАЩЕНИЕ В БД '''

async def save_answer(user_id: int, number: str, today: str, time_now: str, answer: str, document: str):
    dialogs_num = support_data_dict[int(user_id)]['Dialogs'][number]
    
    if today not in dialogs_num:
        dialogs_num[today] = {
            time_now: {
                'answer': answer,
                'document': document
            }
        }
    else:
        dialogs_num[today][time_now] = {
            'answer': answer,
            'document': document
        }
    await save_application()
