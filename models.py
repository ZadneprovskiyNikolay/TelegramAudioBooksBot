import logging

from sqlalchemy import Column, String, Integer, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

import config

base = declarative_base()

class Book(base): 
    __tablename__ = 'book'
    id = Column(Integer, primary_key=True)    
    book_id = Column(Integer)
    category = Column(String)
    title = Column(String)    
    publisher = Column(String)
    narrator = Column(String, nullable=True)
    author = Column(String)
    len = Column(String)
    __table_args__ = ( UniqueConstraint('book_id', name='_book_id_uc'), )    

    def __repr__(self): 
        return '<Book(id="{}", book_id="{}")>'.format(self.id, self.book_id)

    @classmethod
    def from_json(cls, book_info):  
        res = { 
            'book_id': int(book_info['book_id']),        
            'title': book_info['title'],
            'category': book_info['category'],
            'publisher': book_info['pub'],     
            'narrator': book_info.get('narrator'), 
            'author': book_info['author'], 
            'len': book_info['length'], 
        }    
        return cls(**res)




    

