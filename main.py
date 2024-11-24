from flask import Flask, render_template, url_for, request, redirect, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from config import load_config
import logging
import colorlog

from misc import PassAction
from postgres import Database, DbLink

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
logger = colorlog.getLogger("FlaskLogger")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)  # Уровень логирования


app = Flask(__name__)  # Создаем объект приложения
app.config['DbConfig'] = load_config(".env").db


@app.route('/about', methods=['GET', 'POST'])
async def about():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # user = await get_user_by_username(username)
        dsn = await DbLink(config=app.config["DbConfig"])

        db = Database()
        await db.connect(dsn)
        user = await db.fetchrow("SELECT * FROM users WHERE username = $1", username)

        if user:
            print(f'Fetched user: {user}')  # Показываем полученного пользователя
            print(f'Хеш пароля: {user[2]}')  # Выводим хеш пароля из базы данных
            print(f'Введённый пароль: {password}')  # Выводим введённый пароль

            if PassAction.verify_password(user['password'], password):
                print(True)
                # login_user(User(user['user_id'], user['username'], user['role']))
                # return redirect(url_for('MAIN'))
            else:
                flash("Пароль неверный")
                print("Password check failed")  # Debug output
        else:
            flash("Пользователь не найден")
            print("User not found")  # Debug output
        await db.disconnect()
    return render_template("about.html")


@app.route('/')
def index():
    return render_template("index.html")



if __name__ == "__main__":
    app.run(debug=True)  # Запуск приложения
