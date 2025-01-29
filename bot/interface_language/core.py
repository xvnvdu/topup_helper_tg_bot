from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.main_bot import users_data_dict, save_data

from .english import EnglishLanguage
from .russian import RussianLanguage


''' ФУНКЦИЯ ВОЗВРАТА ПЕРЕВОДА ЭЛЕМЕНТОВ ИНТЕРФЕЙСА '''

def phrases(language: str, settings = None):
	if language == 'RU':
		settings = RussianLanguage()
	if language == 'EN':
		settings = EnglishLanguage()
	return settings


''' КНОПКИ РАЗДЕЛА СМЕНЫ ЯЗЫКА '''

def language_keyboard(call: CallbackQuery):
	user_id = call.from_user.id
	user_data = users_data_dict[user_id]
	lang = phrases(user_data['Language'])
	
	language_buttons = [
		[InlineKeyboardButton(text='🇷🇺 Русский', callback_data='lang_ru'),
		InlineKeyboardButton(text='🇺🇸 English', callback_data='lang_en')],
		[InlineKeyboardButton(text=lang.back, callback_data='account')]
	]
	return InlineKeyboardMarkup(inline_keyboard=language_buttons)


''' ГЛАВНАЯ СТРАНИЦА СМЕНЫ ЯЗЫКА '''

async def select_language(call: CallbackQuery, language: str):
	user_id = call.from_user.id
	user_data = users_data_dict[user_id]
	lang = phrases(language)
	
	await call.message.edit_text(lang.select_interface_language, parse_mode='HTML', reply_markup=language_keyboard(call))
	
	
''' ФУНКЦИЯ СМЕНЫ ЯЗЫКА '''
 
async def change_language(call: CallbackQuery, language: str):
	user_id = call.from_user.id
	user_data = users_data_dict[user_id]
	
	user_data['Language'] = language
	await save_data()
	