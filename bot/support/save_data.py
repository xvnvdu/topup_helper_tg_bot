from bot.main_bot import support_data_dict, support_data, save_application


async def save_question(user_id: int, number: str, today: str, time_now: str, user_message: str):
    if user_id not in support_data_dict:
        user = {
            'ID': user_id,
            'Dialogs': {
                number: {
                    today: {
                        time_now: {
                            'question': user_message
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
                        'question': user_message
                    }
                }
            }
        else:
            if today not in dialogs[number]:
                dialogs[number][today] = {
                    time_now: {
                        'question': user_message
                    }
                }
            else:
                dialogs[number][today][time_now] = {
                    'question': user_message
                }
    await save_application()
    

async def save_answer(user_id: int, number: str, today: str, time_now: str, answer: str):
    dialogs_num = support_data_dict[int(user_id)]['Dialogs'][number]
    
    if today not in dialogs_num:
        dialogs_num[today] = {
            time_now: {
                'answer': answer
            }
        }
    else:
        dialogs_num[today][time_now] = {
            'answer': answer
        }
    await save_application()
