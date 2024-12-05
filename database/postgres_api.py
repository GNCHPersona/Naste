import asyncio
import asyncpg
import uvicorn
from typing import Optional
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from config import DbConfig
from postgres import DatabaseConnect, DatabaseDisconnect, Database
from pydantic_models import QueryModel, PostgresRequest


class AppState:
    pool: Optional[asyncpg.Pool] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = DbConfig.from_env(".env")
    app.state = AppState()

    try:
        app.state.pool = await DatabaseConnect(dsn=config.db_url)
    except Exception as e:
        raise RuntimeError(f"Ошибка подключения к базе данных: {e}")

    yield

    if app.state.pool:
        await DatabaseDisconnect(app.state.pool)


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "When you die, cats will be well fed"}


@app.post("/execute")
async def execute(raw_query: QueryModel):
    query = raw_query.query  # Получаем SQL-запрос
    args = list(raw_query.args.values())  # Получаем параметры запроса

    return await Database(pool=app.state.pool).execute(query, *args)


@app.post("/fetch")
async def request(raw_query: QueryModel):
    args = None
    query = raw_query.query
    try:
        args = list(raw_query.args.values())  # Получаем параметры запроса
    except:
        pass
    if args:
        return await Database(pool=app.state.pool).fetch(query, *args)
    return await Database(pool=app.state.pool).fetch(query, None)


async def main():

    config = uvicorn.Config(
        app,  # Передаем наше FastAPI приложение
        host="127.0.0.1",  # Слушаем на всех доступных интерфейсах
        port=8432,
        reload=True  # Перезагружать при изменениях
    )

    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
