import asyncpg
from typing import Any, Dict, List, Optional

from config import DbConfig


import logging
import colorlog
# Настройка цветного логгера
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'white',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
))
logger = colorlog.getLogger("DatabaseLogger")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)  # Уровень логирования

class DbLink:

    def __init__(self, config: DbConfig):

        self.config = config

    async def __call__(self):
        return f"postgresql://{self.config.user}:{self.config.password}@{self.config.host}/{self.config.database}"

    def __await__(self):
        return self().__await__()

class Database:

    async def connect(self, dsn: str):
        """
        Инициализация объекта для работы с базой данных.
        Устанавливает соединение с базой данных через пул подключений.

        :param dsn: Data Source Name (строка подключения)
        """

        self.dsn = dsn
        self.pool: Optional[asyncpg.Pool] = None

        try:
            self.pool = await asyncpg.create_pool(dsn=self.dsn, min_size=1, max_size=10)
            logger.info("Подключение к базе данных успешно установлено.")
        except Exception as e:
            logger.error("Ошибка при подключении к базе данных:\n%s", e)
            raise

    async def disconnect(self):
        """
        Закрывает пул подключений.
        """

        try:
            if self.pool:
                await self.pool.close()
                logger.info("Соединение с базой данных успешно закрыто.")
        except Exception as e:
            logger.error("Ошибка при закрытии соединения с базой данных:\n%s", e)



    async def execute(self, query: str, *args: Any) -> str:
        """
        Выполняет запрос без возврата результата (например, INSERT, UPDATE, DELETE).

        :param query: SQL-запрос.
        :param args: Аргументы для подстановки в SQL.
        :return: Количество строк, которые затронул запрос.
        """
        try:
            async with self.pool.acquire() as connection:
                result = await connection.execute(query, *args)
                logger.info(f"Запрос без возврата результата успешно выполнен.\nresult: {result}")
                return result
        except Exception as e:
            logger.error("Ошибка при выполнении запроса без возврата результата:\n%s", e)
            raise

    async def fetch(self, query: str, *args: Any) -> List[asyncpg.Record]:
        """
        Выполняет SELECT-запрос и возвращает список строк.

        :param query: SQL-запрос.
        :param args: Аргументы для подстановки в SQL.
        :return: Список строк из базы данных.
        """
        try:
            async with self.pool.acquire() as connection:
                rows = await connection.fetch(query, *args)
                logger.info(f"SELECT-запрос успешно выполнен.\nrows: {rows}")
                return rows
        except Exception as e:
            logger.error("Ошибка при выполнении SELECT-запроса:\n%s", e)
            raise

    async def fetchrow(self, query: str, *args: Any) -> Optional[asyncpg.Record]:
        """
        Выполняет SELECT-запрос и возвращает одну строку.

        :param query: SQL-запрос.
        :param args: Аргументы для подстановки в SQL.
        :return: Одна строка из базы данных или None.
        """
        try:
            async with self.pool.acquire() as connection:
                row = await connection.fetchrow(query, *args)
                logger.info(f"SELECT-запрос успешно выполнен.\nrow: {row}")
                return row
        except Exception as e:
            logger.error("Ошибка при выполнении SELECT-запроса:\n%s", e)
            raise

    async def fetchval(self, query: str, *args: Any) -> Any:
        """
        Выполняет SELECT-запрос и возвращает одно значение.

        :param query: SQL-запрос.
        :param args: Аргументы для подстановки в SQL.
        :return: Одно значение из базы данных.
        """
        try:
            async with self.pool.acquire() as connection:
                value = await connection.fetchval(query, *args)
                return value
        except Exception as e:
            logger.error("Ошибка при выполнении SELECT-запроса:\n%s", e)
            raise


# Пример использования
async def main():
    db = Database()

    # Подключение к базе
    await db.connect(dsn="postgresql://myuser:mypassword@localhost/mydatabase")

    # Пример: создание таблицы
    await db.execute("""
        CREATE TABLE IF NOT EXISTS users12 (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            age INT NOT NULL
        )
    """)

    # Пример: добавление данных
    await db.execute("INSERT INTO users12 (name, age) VALUES ($1, $2)", "Alice", 25)

    # Пример: получение всех пользователей
    users = await db.fetch("SELECT * FROM users12")
    print(users)

    # Пример: получение одного пользователя
    user = await db.fetchrow("SELECT * FROM users12 WHERE id = $1", 1)
    print(user)

    # Закрытие соединения
    await db.disconnect()


# # Для выполнения
# import asyncio
#
# asyncio.run(main())
