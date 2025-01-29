from aiogram.types import CallbackQuery

from bot.interface_language.core import phrases
from bot.bot_buttons import back_to_support_keyboard


async def support_rules(call: CallbackQuery, lang: str):
    lang_settings = phrases(lang)
    await call.message.edit_text(lang_settings.support_rules_page, parse_mode='HTML', reply_markup=back_to_support_keyboard(lang))