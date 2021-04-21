from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

menu_markup = {
    'Главное меню': {
        'Хиты': None, 
        'Новинки': None, 
        'Интересные': None, 
        'Разделы': {
            'Зарубежная проза': None,                                                        
            'Российская проза': None,     
            'Любовные романы': None, 
            'Детективы, боевики': None, 
            'Русская классика': None, 
            'Бизнес-литература': None, 
            'Личностный рост': None, 
            'Психология': None, 
            'Воспитание и обучение': None,     
            'Православная литература': None, 
            'Сказки': None,    
            'Фантастика': None,    
            'Книги для детей': None,   
            'Аудиоспектакли': None, 
            'Приключения': None, 
            'Изучение английского': None, 
            'Биографии Мемуары': None, 
            'Советская классика': None, 
            'Философия и история': None, 
            'Фэнтези, мистика': None, 
            'Публицистика': None, 
            'Медицина и здоровье': None, 
            'Поэззия, драматургия': None, 
            'Юмор и развлечения': None, 
            'Путешествия и путеводители': None, 
            'Книги на английском': None, 
            'Полезные книги': None                               
        }
    }
}

back_button = KeyboardButton('Назад', resize=True)
back_menu = ReplyKeyboardMarkup()       
back_menu.row(back_button)

