import asyncio
import json
import logging
import codecs

import aiohttp
    
from resources import catalog, trends
from models import Book
from db import session, get_or_create, add
from books import book_exists

async def fetch_and_update_books(source, http_session): 
    """Loads all books from source into db"""
    url = source['url']
    try: 
        async with http_session.get(url, headers=source['headers'], ssl=False) as resp:                                  
            if resp.status != 200:
                logging.warning(f'Error loading category="{source["category"]}" ' \
                    f'from {url}: {resp.status}')  
                return

            resp_text = await resp.text()
            decoded_data = codecs.decode(resp_text.encode(), 'utf-8-sig')
            data = json.loads(decoded_data)                                         
            books_info = data['books']
                    
            for book_info in books_info:                 
                if not book_exists(book_info['book_id']): 
                    book_info['category'] = source['category']                
                    add(Book.from_json(book_info), commit=False)                
    except Exception as e: 
        logging.warning(f'Error loading category="{source["category"]}" ' \
            f'from {url}: {e}')     

async def update_books(): 
    logging.info('Updating books info in local db...')
    async with aiohttp.ClientSession() as http_session:     
        await asyncio.gather(
            *[
                fetch_and_update_books(
                    source, 
                    http_session
                ) for source in (catalog + trends)
            ]
        )      
    session.commit()    # Commit all new books at once for speedup
    logging.info('books info update complete')