from dataclasses import dataclass

import asyncpg
from typing import Any, List, Optional

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

@dataclass
class DatabaseConnect:

    dsn: str

    async def __call__(self):
        """
        Устанавливает соединение с базой данных через пул подключений.
        """

        try:
            self.pool = await asyncpg.create_pool(dsn=self.dsn, min_size=1, max_size=10)
            logger.info("Подключение к базе данных успешно установлено.")
            return self.pool
        except Exception as e:
            logger.error("Ошибка при подключении к базе данных:\n%s", e)
            raise

    def __await__(self):
        return self().__await__()


@dataclass
class DatabaseDisconnect:

    pool: Optional[asyncpg.Pool]

    async def __call__(self):
        """
        Закрывает пул подключений.
        """

        try:
            if self.pool:
                await self.pool.close()
                logger.info("Соединение с базой данных успешно закрыто.")
        except Exception as e:
            logger.error("Ошибка при закрытии соединения с базой данных:\n%s", e)

    def __await__(self):
        return self().__await__()


class Database:

    def __init__(self, pool: Optional[asyncpg.Pool]):
        self.pool = pool

    async def execute(self, query: str, *args: list) -> str:
        print("query:", query)
        print("args:", args)

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
            return f"Ошибка при выполнении запроса без возврата результата:\n{e}"

    async def fetch(self, query: str, *args: list | None) -> List[asyncpg.Record]:
        print("args=", args)
        """
        Выполняет SELECT-запрос и возвращает список строк.

        :param query: SQL-запрос.
        :param args: Аргументы для подстановки в SQL.
        :return: Список строк из базы данных.
        """
        try:
            async with self.pool.acquire() as connection:
                if not args or args == (None,):
                    rows = await connection.fetch(query)
                else:
                    rows = await connection.fetch(query, *args)

                logger.info(f"SELECT-запрос успешно выполнен.\nrows: {rows}")
                return rows
        except Exception as e:
            logger.error("Ошибка при выполнении SELECT-запроса:\n%s", e)
            raise

    async def fetchrow(self, query: str, *args: list) -> Optional[asyncpg.Record]:
        """
        Выполняет SELECT-запрос и возвращает одну строку.

        :param query: SQL-запрос.
        :param args: Аргументы для подстановки в SQL.
        :return: Одна строка из базы данных или None.
        """
        try:
            async with self.pool.acquire() as connection:
                if not args or args == (None,):
                    row = await connection.fetchrow(query)
                else:
                    row = await connection.fetchrow(query, *args)

                logger.info(f"SELECT-запрос успешно выполнен.\nrow: {row}")
                return row
        except Exception as e:
            logger.error("Ошибка при выполнении SELECT-запроса:\n%s", e)
            raise

    async def fetchval(self, query: str, *args: list) -> Any:
        """
        Выполняет SELECT-запрос и возвращает одно значение.

        :param query: SQL-запрос.
        :param args: Аргументы для подстановки в SQL.
        :return: Одно значение из базы данных.
        """
        try:
            async with self.pool.acquire() as connection:
                if not args or args == (None,):
                    value = await connection.fetchval(query)
                else:
                    value = await connection.fetchval(query, *args)
                return value
        except Exception as e:
            logger.error("Ошибка при выполнении SELECT-запроса:\n%s", e)
            raise
