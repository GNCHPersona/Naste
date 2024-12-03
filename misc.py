import asyncio

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from flask import abort
from functools import wraps
from email_validator import validate_email, EmailNotValidError
import aiohttp
from config import ServerConfig

class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role


class PassAction:

    @staticmethod
    def hash_passwords(password: str) -> str:
        return generate_password_hash(password)

    @staticmethod
    def verify_password(hashed_password: str, input_password: str) -> bool:
        return check_password_hash(hashed_password, input_password)

class ProveData:

    @staticmethod
    def validate_user_email(email: str):
        try:
            return {"val": True} if validate_email(email) else False
        except EmailNotValidError as e:
            return {"val": False, "err": str(e)}


def role_required(*roles):
    """
    Декоратор для ограничения доступа на основе роли.
    :param roles: роли, которые имеют доступ к маршруту
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                # Если пользователь не авторизован, перенаправляем на страницу входа
                abort(401)  # Unauthorized
            if current_user.role not in roles:
                # Если у пользователя недостаточно прав, возвращаем "403 Forbidden"
                abort(403)  # Forbidden
            return func(*args, **kwargs)
        return wrapper
    return decorator


async def send_request(server: ServerConfig, type: str,  payload: dict):

    url = "http://"+server.host+':'+str(server.port)+'/'+type

    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, json=payload) as response:

            # Проверяем статус ответа
            if response.status == 200:
                return await response.json()
            else:
                print(f"Ошибка {response.status}: {await response.text()}")

#
# async def main():
#     payload = {
#         "query": "SELECT * FROM users WHERE username = $1",
#         "args": {"username": "user1"}
#     }
#
#     a = await send_request(url="127.0.0.1", port=8432, type="fetch", payload=payload)
#     print(a)
#
# asyncio.run(main())