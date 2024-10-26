from aiogram.types import CallbackQuery

from bot.bot_buttons import back_to_support_keyboard


async def support_rules(call: CallbackQuery):
	await call.message.edit_text('<b>✅ Обращение может содержать:</b>\n'
                              '<i>• Пустое сообщение\n'
                              '• Не более ОДНОГО вложения\n'
                              '• Фотографию БЕЗ сжатия\n'
                              '• Файл</i>\n\n'
                              '<b>❌ Обращение НЕ может содержать:</b>\n'
                              '<i>• Несколько вложений\n'
                              '• Сжатую фотографию\n'
                              '• Голосовое сообщение\n'
                              '• Иные вложения, если это не документ</i>\n\n'
                              '<i>При отправке вложений, не предусмотренных системой, '
                              'поддержка их не получит — будет доставлено только '
                              'текстовое сообщение при наличии такового. При отправке '
                              'нескольких вложений будет доставлено только первое.</i>', 
                              parse_mode='HTML', reply_markup=back_to_support_keyboard)