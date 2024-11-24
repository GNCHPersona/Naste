import asyncio
from config import load_config
from postgres import Database, DbnLink
from misc import PassAction

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


async def insert_users():

    db = Database()
    dsn = await DbnLink(config=config.db)

    # Подключение к базе
    await db.connect(dsn=dsn)

    password = PassAction.hash_passwords("password1")

    # Пример: создание таблицы
    await db.execute("""
    INSERT INTO users (username, password, role)
    VALUES ($1, $2, $3)
    ON CONFLICT (username) DO NOTHING
    """, 'user1', password, 'admin')

    await db.disconnect()

# password1 = generate_password_hash('password1')
# password2 = generate_password_hash('password2')
# password3 = generate_password_hash('password3')
#
# # Добавляем пользователей
# await add_user('user4', password1, 'admin')
# await add_user('user5', password2, 'user')
# await add_user('user6', password3, 'user')

asyncio.run(insert_users())