import logging
import re
import asyncio
from functools import wraps

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.executor import start_webhook

from bot import menu, catalog, description, listen
from bot.bot import bot, dp
from book_loader import update_books

logging.basicConfig(level=logging.INFO)

async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    await update_books()


async def on_shutdown(dp):
    # Close webhook
    await bot.delete_webhook()

    # Close DB connection
    await dp.storage.close()
    await dp.storage.wait_closed()

def main(): 
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,    
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )

if __name__ == '__main__':
    main()