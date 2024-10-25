from datetime import datetime
from aiogram.types import CallbackQuery

from .main_bot import users_payments_dict


# ГЕНЕРАЦИЯ ЛОГА ТРАНЗАКЦИЙ
async def sorted_payments(call: CallbackQuery):
    user_id = call.from_user.id
    user_transactions_info = users_payments_dict[user_id]['Transactions']
    sorted_dates = sorted(user_transactions_info.keys(), key=lambda date: datetime.strptime(date, '%d.%m.%Y'), reverse=True)
    trx_log = []

    line_count = 0
    for date in sorted_dates:
        trx_log.append(f'✧<strong>{date}</strong>')
        line_count += 1
        trx_by_time = sorted(user_transactions_info[date].keys(), reverse=True)

        for count, time in enumerate(trx_by_time):
            trx = user_transactions_info[date][time]
            rub_amount = trx['RUB']
            trx_id = trx['trx_id']
            trx_type = trx['type']
            usd_amount = trx['USD']
            price = f'{rub_amount}₽' if usd_amount == 0 else f'{usd_amount}$'

            time_input = datetime.strptime(time, '%H:%M:%S')
            time_output = time_input.strftime('%H:%M')

            if count < len(trx_by_time)-1:
                line_count += 1
                if (line_count - 1) % 15 == 0:
                    trx_log.append(f'✧<strong>{date}</strong>')
                    line_count += 1
                trx_log.append(f'├ <i>{time_output}</i> - <code>{price}</code> -'
                               f'<i>{trx_type}</i> - (<code>№{trx_id}</code>)')
            else:
                line_count += 1
                if (line_count - 1) % 15 == 0:
                    trx_log.append(f'✧<strong>{date}</strong>')
                    line_count += 1
                trx_log.append(f'└ <i>{time_output}</i> - <code>{price}</code> - '
                               f'<i>{trx_type}</i> - (<code>№{trx_id}</code>)')
                trx_log.append('')
                line_count += 1
    return trx_log
