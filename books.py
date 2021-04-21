import asyncio
import json
import logging
import codecs
import xmltodict
import xml.dom.minidom
import shutil
import sys
import os

import aiohttp
import aiofiles
import requests
from html2text import html2text
from aiogram.utils.markdown import bold, escape_md

import resources
import config
from resources import audio_resources, chapters_resources
from db import session, Book
from sqlalchemy.sql import exists

# DB

def book_exists(book_id): 
    return session.query(exists().where(Book.book_id == book_id)).scalar()

def select_by_title_or_auth(search_text): 
    reg = f'"%{search_text}%"'
    with engine.connect() as con: 
        statement = text(f'SELECT * FROM book WHERE author LIKE {reg} OR title LIKE {reg}')
        res = con.execute(statement)
        return res.fetchall()


def find_books(request) -> str: 
    """Returns string containing all books found in db
    with links to get them"""
    res = ''
    books = select_by_title_or_auth(request)
    for book_id, title, author in books: 
        res += title + '\n' # special codes to make string bold
        res += author + '\n'
        res += f'Список глав: /chapters_{book_id}\n\n'
    return res    

# Uploading

def parse_chapters_xml(binary) -> list[tuple[str, str]]:
    """Returns tuples (filename, chapter string)"""
    res = []
    data = xmltodict.parse(binary)['plist']['dict']['array']['dict']
    for item in data: 
        chapter_info = list(item.items())[1][1]
        res.append(chapter_info)
    return res 

def get_chapters(book_id, page): 
    """Returns chapters in range [ (page-1)*page_size; page*page_size ]"""
    for source in chapters_resources: 
        # Download
        url = f'{source["url"]}/{book_id}/recordsList.plist'
        resp = requests.get(url, headers=source['headers'])
        if resp.status_code != 200: 
            logging.warning(f'Error loading chapters from {url}: {resp.status_code}')  
            continue
        # Generate result
        res = ''
        chapters = parse_chapters_xml(resp.content)
        page_size = config.chapters_page_size
        first_chapter, last_chapter = (page-1)*page_size,  page*page_size
        for idx, (filename, chapter) in enumerate(chapters[first_chapter:last_chapter]): 
            res += f'{chapter}' + '\n'
            res += f'Слушать: /listen_{book_id}_{filename.strip(".mp3")}' + '\n\n'                
        return res
    return None

def get_books_catalog(category, page, page_size) -> tuple[tuple, str]: 
    """Returns book ids and description of this books"""
    books = session.query(Book).with_entities(Book.book_id, Book.title, Book.author, Book.len).\
        filter_by(category=category).offset((page-1)*page_size).limit(page_size).all()                    
    book_ids = tuple(book[0] for book in books)
    # Form description for books
    books_info_concat = [] # [ [book_property_str1, book_property_str2,], ... ] - books with attribute strings
    for book_num, book in enumerate(books):  
        books_info_concat.append([])               
        for attr_idx, attr in enumerate(book[1:]):                        
            attr = escape_md(attr)
            if attr_idx == 0: 
                books_info_concat[book_num].append(f'{(page-1)*page_size+book_num+1}\) {attr}') # Add title                        
            else:                 
                books_info_concat[book_num].append(f'```{attr}```') # Add attribute with special font color                        
    books_info_concat = ['\n'.join(book_info) for book_info in books_info_concat]                            
    res_str = '\n\n'.join(books_info_concat)   
    if not book_ids: 
        return
    return book_ids, res_str

def get_book_description(book_id): 
    description = None    
    for resource_info in resources.description_resources: 
        domain = resource_info['url']
        headers = resource_info['headers']
        url = f'{domain}/{book_id}/desc.html'   
        r = requests.get(url, headers=headers)
        if r.status_code == 200: 
            r.encoding = 'utf-8' 
            description = html2text(r.text)
            break
    return description

def get_book_image_url(book_id): 
    for resource_info in resources.image_resources: 
        domain = resource_info['url']
        headers = resource_info['headers']
        url = f'{domain}/{book_id}/cover.jpg'        
        ret = requests.head(url, headers=headers)
        if ret.status_code == 200:
            return url    

def get_book_url(book_id, filename): 
    for resource_info in resources.audio_resources: 
        domain = resource_info['url']
        headers = resource_info['headers']
        url = f'{domain}/{book_id}/records/{filename}.mp3'        
        ret = requests.head(url, headers=headers)
        if ret.status_code == 200:
            return url    