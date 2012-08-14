from sqlalchemy import *
# from sqlalchemy.orm import *
# from sqlalchemy.schema import *

from app import *

# ========
# = Main =
# ========

if __name__ == "__main__":
    getDb().echo = True
    initDb()
