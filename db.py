from sqlalchemy import create_engine

DB_URL = "postgresql://postgres:jiyajain1204@localhost:5432/sales_db"

engine = create_engine(DB_URL)

