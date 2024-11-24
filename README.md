# Naste

Разбросал код по файлам для удобства!

ГЛАВНЫЕ ФАЙЛЫ:
postgres.py
main.py
misc.py
config.py

второстепенные файлы:
temp.py - разобранный исходный код
test_bd - код для тестирования, изменения / добавления в базу данных.
.env - !!!ПЕРЕПИШИ СВОИ ДАННЫК ДЛЯ БД


coonfig.py ->
Загружает информацию из .env создает класс
Этот класс автоматически добавляется в app.config при загрузке main.py

  //app = Flask(__name__)  # Создаем объект приложения
  //app.config['DbConfig'] = load_config(".env").db

Необходим для созданния dsn сслыки для postgres:
  dsn = await DbLink(config=app.config["DbConfig"])
  Выглядит как:
    "postgresql://myuser:mypassword@localhost/mydatabase"
                  ^-user ^-password ^-host    ^-db_name

postgres.py ->
1) Добавил логгирование для красоты
2) Классы для работы:
  DbLink
  Database

Для использования обяхательные след. строки:
  dsn = await DbLink(config=app.config["DbConfig"]) -> Берет из app.config данные о бд создает dsn сыылку

  db = Database() -> Объект базы данных
  await db.connect(dsn) -> Подключение к бд
  user = await db.fetchrow("SELECT * FROM users WHERE username = $1", username) -> Использование // db.func(query: str, arg: Any)
  await db.disconnect() -> Отключаемся от базы

  Внизу файла есть пример кода async def main()

main.py -> Переписанный код flask - готово только проверка на пароли.

misk.py -> "Разное"
  class: PassAction -> Работа с хэшированием и проверки пароля



