import logging
import re
from functools import wraps

from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.bot import bot, dp
from menu_markup import back_menu
from books import get_chapters, get_book_url

@dp.callback_query_handler(regexp='/chapters_[1-9][0-9]*_[1-9][0-9]*(_respond)*')
async def update_chapters(query: types.CallbackQuery):        
    """Returns chapters for book `book_id` in range [ (page-1)*page_size; page*page_size ]."""
    # Parse query
    request = query.data.split('_')
    book_id = int(request[1])
    page = int(request[2])    
    respond = True if request[-1] == 'respond' else False   
        
    message = get_chapters(book_id, page)
    inline_keyboard = InlineKeyboardMarkup()
    inline_keyboard.row(
        InlineKeyboardButton('<', callback_data=f'/chapters_{book_id}_{page-1}'), 
        InlineKeyboardButton('>', callback_data=f'/chapters_{book_id}_{page+1}')
    )        
    
    await query.answer('')
    if not message: 
        return
    if respond:         
        await bot.send_message(query.from_user.id, text=message, reply_markup=back_menu)
    else: 
        bot.edit_message_text(
            text=message, 
            inline_message_id=query.inline_message_id
        )       
         
@dp.message_handler(regexp='/listen_[1-9][0-9]*_')
async def listen(message: types.Message):
    match = re.match('/listen_([1-9][0-9]*)_(.*)', message.text)        
    book_id = int(match.group(1))
    filename = match.group(2)
    book_url = get_book_url(book_id, filename)
    if book_url: 
        try: 
            await bot.send_audio(message.chat.id, book_url)
        except Exception as e: 
            await message.answer('Извините, запись временно недоступна')        
            logging.error(f'Could not load audio file: {e}')
    else: 
        await message.answer('Запись не найдена')        