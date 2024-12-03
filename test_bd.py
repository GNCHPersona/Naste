from config import load_config
from database.postgres import Database, DbnLink

config = load_config(".env")


async def create_table():

    db = Database()
    dsn = await DbnLink(config=config.db)

    # Подключение к базе
    await db.connect(dsn=dsn)

    # Пример: создание таблицы
    await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL, 
            role VARCHAR(20) NOT NULL,          
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP            
            );
    """)

    await db.disconnect()

