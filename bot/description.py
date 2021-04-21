import re
from functools import wraps

from aiogram import types
from aiogram.types import InlineKeyboardButton

from bot.bot import bot, dp
from menu_markup import back_button
from books import get_book_description, get_book_image_url

@dp.callback_query_handler(regexp='book_info_[0-9]*')
async def book_info(query):         
    """Returns book description"""         
    # Parse query 
    match = re.match(r'book_info_(.*)', query.data)
    book_id = int(match.group(1))

    # Get book description
    book_description = get_book_description(book_id)
    # Get link for book cover
    photo_url = get_book_image_url(book_id)    

    # Send response      
    await query.answer('')
    user_id = query.from_user.id
    if photo_url is not None: 
        await bot.send_photo(user_id, photo_url)
    inline_keyboard = types.InlineKeyboardMarkup()       
    inline_keyboard.add(InlineKeyboardButton('Слушать', callback_data=f'/chapters_{book_id}_1_respond'))
    await bot.send_message(user_id, book_description, reply_markup=inline_keyboard)    
