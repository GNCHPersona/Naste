import asyncpg
import asyncio

from flask import Flask, render_template, url_for, request, redirect, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Замените на свой секретный ключ

login_manager = LoginManager()
login_manager.init_app(app)





class User(UserMixin):
    def __init__(self, user_id, username, role):
        self.id = user_id
        self.username = username
        self.role = role



@login_manager.user_loader

async def load_user(user_id):
    conn = await get_db_connection()
    try:
        user = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
        if user:
            return User(user[0], user[1], user[3])  # id, username, role
    finally:
        await conn.close()
    return None

@app.route('/Student')
def student():
    return render_template("Student.html")


@app.route('/about', methods=['GET', 'POST'])
async def abaut():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = await get_user_by_username(username)
        if user:
            print(f'Fetched user: {user}')  # Показываем полученного пользователя
            print(f'Хеш пароля: {user[2]}')  # Выводим хеш пароля из базы данных
            print(f'Введённый пароль: {password}')  # Выводим введённый пароль

            if await verify_password(user['password'], password):
                login_user(User(user['user_id'], user['username'], user['role']))
                return redirect(url_for('MAIN'))
            else:
                flash("Пароль неверный")
                print("Password check failed")  # Debug output
        else:
            flash("Пользователь не найден")
            print("User not found")  # Debug output

    return render_template("about.html")

async def get_user_by_username(username):
    conn = await get_db_connection()
    try:
        return await conn.fetchrow("SELECT * FROM users WHERE username = $1", username)
    except Exception as e:
        flash(f'Ошибка базы данных: {e}')
        return None
    finally:
        await conn.close()




@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('about'))

if __name__ == "__main__":
    app.run(debug=True)