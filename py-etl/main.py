from sqlalchemy import *
# from sqlalchemy.orm import *
# from sqlalchemy.schema import *

from app import *

if __name__ == "__main__":
    db = create_engine('sqlite:///var/test.db')
    # db.echo = True
    Base.metadata.create_all(db) 
