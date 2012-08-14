from sqlalchemy import *
# from sqlalchemy.orm import *
# from sqlalchemy.schema import *

from app import *

if __name__ == "__main__":
    db = create_engine(config.get('db', 'uri'))
    # db.echo = True
    Base.metadata.create_all(db) 
