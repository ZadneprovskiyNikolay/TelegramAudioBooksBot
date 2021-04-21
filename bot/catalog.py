from functools import wraps

from aiogram import types
from aiogram.types import InlineKeyboardButton
from utils import matches

import config
from bot.bot import bot, dp
from menu_markup import back_menu
from books import get_books_catalog

@dp.callback_query_handler(regexp='catalog_[^_]+_[1-9]+\d*')
async def catalog_page(query, callback=True):         
    """Returns string with book descriptions for parameters
    `category` and `page` from event.data. Navigation inline 
    buttons and inline buttons to select particular book are added"""         
    page_size = config.catalog_page_size    
    # Parse query 
    data = query.data.split('_')        
    category = data[1]
    page = int(data[-1])
    
    # Get message(page) and books id    
    books_returned = get_books_catalog(category=category, page=page, page_size=3)    
    if not books_returned: # Do nothing if there is no data
        return
    book_ids, message = books_returned

    # Create inline keyboard
    inline_keyboard = types.InlineKeyboardMarkup()       
    select_buttons = [] # 1st row
    navigation_buttons = [] # 2nd row
    for idx, book_id in enumerate(book_ids): 
        button_text = str((page - 1) * page_size + idx + 1) # Number of book in the list
        select_buttons.append(
            InlineKeyboardButton(button_text, callback_data=f'book_info_{book_id}')
        )    
    navigation_buttons.extend(    
        [
            InlineKeyboardButton('<', callback_data=f'catalog_{category}_{page-1}'),
            InlineKeyboardButton(f'Страница {page}', callback_data=f'catalog_{category}_{page}'),
            InlineKeyboardButton('>', callback_data=f'catalog_{category}_{page+1}')
        ]
    )   
    inline_keyboard.row(*select_buttons)
    inline_keyboard.row(*navigation_buttons)

    # Respond
    if callback:
        await query.answer('')
    else: 
        await bot.send_message(query.from_user.id, category, reply_markup=back_menu)
    await bot.send_message(
        query.from_user.id, 
        text=message, 
        reply_markup=inline_keyboard, 
        parse_mode='MarkdownV2'
    )