from functools import wraps

from aiogram import types
from aiogram.types import KeyboardButton

import resources
from bot.bot import dp
from .catalog import catalog_page
from menu_markup import menu_markup, back_menu, back_button

users_menu_state = {} # Mapping of user id to the stack of menus

def reg_menu_state(fun):     
    """Decorator that stores stack of functions called to allow navigation"""
    global users_menu_state
    @wraps(fun)
    def _wrapper(*args, **kwargs): 
        message = args[0]
        user_id = message.from_user.id
        stack = users_menu_state.get(user_id)
        if stack is None:
            users_menu_state[user_id] = []            
        users_menu_state[user_id].append(_wrapper)        
        return fun(*args, **kwargs) 
    return _wrapper           

@dp.message_handler(regexp='/start')
@reg_menu_state
async def main_menu(message: types.Message):
    # Create inline keyboard
    keyboard = types.ReplyKeyboardMarkup()       
    row1 = [
        KeyboardButton("Хиты"), 
        KeyboardButton("Новинки"), 
        KeyboardButton("Интересные"), 
    ]
    row2 = [KeyboardButton("Каталог книг")]
    keyboard.row(*row1)
    keyboard.row(*row2)
    await message.answer('Вы в главном меню', reply_markup=keyboard)

@dp.message_handler(regexp='Каталог книг')
@reg_menu_state
async def catalog(message):     
    # Create keyboard  
    keyboard = types.ReplyKeyboardMarkup()         
    n = 2 # Number of buttons in one line of menu
    buttons_text = list(menu_markup['Главное меню']['Разделы'].keys())
    buttons_text_rows = [ # Lists with  button text for each menu row
        buttons_text[i:i+n] for i in range(0, len(buttons_text), n)
    ] 
    for buttons_text_row in buttons_text_rows:
        row = [ 
            KeyboardButton(text) for text in buttons_text_row
        ]
        keyboard.row(*row)
    keyboard.row(back_button)    

    await message.answer('Вы в каталоге книг', reply_markup=keyboard)

def make_categories_handler(category): 
    global dp
    @dp.message_handler(regexp=category)
    @reg_menu_state
    async def _func(query):  
        # Redirect calls to `catalog_page` inline handler
        query.data = f'catalog_{category}_1'
        await catalog_page(query, callback=False)
    return _func    

categories_handlers = [ 
    make_categories_handler(resource_info['category']) \
        for resource_info in (resources.catalog + resources.trends) 
]

@dp.message_handler(regexp='Назад')
async def back(message):
    """Navigation to previous menu"""   
    user_id = message.from_user.id
    stack = users_menu_state.get(user_id)
    if not stack:             
        await main_menu(message)
        return        
    stack.pop() 
    if stack:    
        await stack.pop()(message)        
    else: 
        await main_menu(message)