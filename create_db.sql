CREATE TABLE book(
    id INTEGER PRIMARY KEY, 
    book_id integer UNIQUE,  
    category TEXT,    
    title TEXT, 
    publisher TEXT, 
    narrator TEXT, 
    author TEXT, 
    len TEXT
)