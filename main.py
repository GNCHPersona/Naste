from flask import Flask, render_template, url_for, request, redirect, flash, session
from flask_login import LoginManager, login_user, login_required
import logging
import colorlog
from misc import send_request
from config import load_config

from misc import PassAction, User, role_required, ProveData
# from database.postgres import Database, DbLink

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
app.secret_key = 'your_secret_key'  # Замените на свой секретный ключ
app.config['Server'] = load_config(".env").server

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    if user_id:
        user_data = session.get("user_data")
        print("user_data=", user_data)
        if user_data and str(user_data['id']) == user_id:
            print("user_data=", user_data)
            return User(user_data['id'], user_data['username'], user_data['role'])

    return None


@app.route('/about', methods=['GET', 'POST'])
async def about():
    print(session)
    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')
        payload = {
            "query": "SELECT * FROM users WHERE username = $1",
            "args": {"username": username}
        }
        user = await send_request(server=app.config["Server"], type="fetch", payload=payload)
        if user:
            print(f'Fetched user: {user}')  # Показываем полученного пользователя
            user = user[0]
            if PassAction.verify_password(user['password'], password):
                session['user_data'] = {
                    'id': user['id'],
                    'username': user['username'],
                    'role': user['role']
                }
                print(True)
                login_user(User(user['id'], user['username'], user['role']))
                return redirect(url_for('MAIN'))
            else:
                flash("Пароль неверный")
                print("Password check failed")  # Debug output
        else:
            flash("Пользователь не найден")
            print("User not found")  # Debug output
    return render_template("about.html")


@app.route('/addTeacher', methods=['GET', 'POST'])
@role_required("admin")
@login_required
async def addTeacher():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        subject_id = request.form.get('subject_id')
        password = request.form.get('password')
        repeat_password = request.form.get('repeat_password')

        accept = ProveData.validate_user_email(email)
        if not accept['val']:
            flash(f"{accept["err"]}")
            return render_template("addTeacher.html")

        if not password == repeat_password:
            flash("Passwords are not the same")
            return render_template("addTeacher.html")

        payload={
            "query": "WITH new_user AS (INSERT INTO users (username, password, role) VALUES ($1, $2, $3) RETURNING id) INSERT INTO teacher (user_id, email, subject_id, phone, username) SELECT id, $4, $5, $6, $7 FROM new_user;",
            "args": {
                "username": username,
                "password": PassAction.hash_passwords(password),
                "role": "teacher",
                "email": email,
                "subject_id": int(subject_id),
                "phone": phone,
                "username1": username
            }
        }

        response = await send_request(server=app.config['Server'], type='execute', payload=payload)
        flash("Teacher added successfully!")

    return render_template("addTeacher.html")

@app.route('/addParent', methods=['GET', 'POST'])
@role_required("admin")
@login_required
async def addParent():
    if request.method == 'POST':
        username = request.form.get('username')
        student_username = request.form.get('student_username')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')
        repeat_password = request.form.get('repeat_password')

        accept = ProveData.validate_user_email(email)
        if not accept['val']:
            flash(f"{accept["err"]}")
            return render_template("addStudent.html")

        if not password == repeat_password:
            flash("Passwords are not the same")
            return render_template("addStudent.html")

        # payload = {
        #     "query": "select * from"
        # }
        #
        # await send_request(server=app.config['Server'], type="execute", payload=payload)

        payload = {
            "query": "WITH new_user AS (INSERT INTO users (username, password, role) VALUES ($1, $2, $3) RETURNING id) INSERT INTO parents "
                     "(user_id, email, phone, username) SELECT id, $4, $5, $6 FROM new_user;",
            "args": {
                "username": username,
                "password": PassAction.hash_passwords(password),
                "role": "parent",
                "email": email,
                "phone": phone,
                "username1": username
            }
        }

        response = await send_request(server=app.config['Server'], type="execute", payload=payload)
        print(response)
        flash("Parent added successfully!")
    return render_template("addParent.html")


@app.route('/addStudent', methods=['GET', 'POST'])
@role_required("admin")
@login_required
async def addStudent():
    if request.method == 'POST':
        username = request.form.get('username')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')
        repeat_password = request.form.get('repeat_password')

        accept = ProveData.validate_user_email(email)
        if not accept['val']:
            flash(f"{accept["err"]}")
            return render_template("addStudent.html")

        if not password == repeat_password:
            flash("Passwords are not the same")
            return render_template("addStudent.html")

        payload = {
            "query": "WITH new_user AS (INSERT INTO users (username, password, role) VALUES ($1, $2, $3) RETURNING id) INSERT INTO student "
                     "(user_id, email, phone, username) SELECT id, $4, $5, $6 FROM new_user;",
            "args": {
                "username": username,
                "password": PassAction.hash_passwords(password),
                "role": "student",
                "email": email,
                "phone": phone,
                "username1": username
            }
        }

        response = await send_request(server=app.config['Server'], type="execute", payload=payload)
        print(response)
        flash("Student added successfully!")
    return render_template("addStudent.html")


@app.route('/adminMain')
@role_required("admin")
@login_required
def adminMain():
    return render_template("adminMain.html")

@app.route('/Student')
def Student():
    return render_template("Student.html")

@app.route('/diary')
def diary():
    return render_template("diary.html")

@app.route('/adminStudent')
def adminStudent():
    return render_template("adminStudent.html")

@app.route('/adminTeacher')
def adminTeacher():
    return render_template("adminTeacher.html")

@app.route('/adminDiary')
def adminDiary():
    return render_template("adminDiary.html")

@app.route('/adminParent')
def adminParent():
    return render_template("adminParent.html")

@app.route('/MAIN')
@login_required
async def MAIN():
    return render_template("MAIN.html")

@app.route('/')
def index():
    return render_template("index.html")


# from misc import PassAction
# from postgres import Database
#
# import asyncio
#
# async def main():
#     dsn = await DbLink(config=app.config["DbConfig"])
#
#     db = Database()
#     await db.connect(dsn)
#     password1 = PassAction().hash_passwords('password1')
#
#
#     user = await db.execute("""
#     CREATE TABLE Student (
#     id SERIAL PRIMARY KEY,
#     user_id INTEGER,
#     email VARCHAR(255),
#     class_id INTEGER,
#     parent_id INTEGER,
#     phone VARCHAR(255),
#     username VARCHAR(255),
#     FOREIGN KEY (user_id) REFERENCES "users"(id),
#     );""")
#                             # , 'pirat', password1, 'pirats')
#
# asyncio.run(main())


if __name__ == "__main__":
    app.run(debug=True)  # Запуск приложения
