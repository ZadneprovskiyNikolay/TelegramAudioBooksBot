import logging

from sqlalchemy import create_engine, or_
from sqlalchemy.sql import exists, text
from sqlalchemy.orm.session import sessionmaker

import config
from models import base, Book

engine = create_engine(f'sqlite:///db.db')
# Create all tables
base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def add(model_instance, commit=True): 
    session.add(model_instance)
    if commit: 
        session.commit()

def get_or_create(model, defaults=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).one_or_none()    
    if instance:
        return instance
    else:
        kwargs |= defaults or {}
        instance = model(**kwargs)
        try:
            session.add(instance)
            session.commit()
        except Exception as e:  
            # The actual exception depends on the specific database so we catch all exceptions. 
            # This is similar to the official documentation: https://docs.sqlalchemy.org/en/latest/orm/session_transaction.html            
            session.rollback()    
            logging.error(f'Error inserting row="{kwargs}" into {model}: {e}')
            return None, False
        else:
            return instance, True
        finally: 
            session.close()




    