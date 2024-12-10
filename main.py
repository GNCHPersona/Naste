from crypt import methods
from types import MethodType

from flask import Flask, render_template, url_for, request, redirect, flash, session
from flask_login import LoginManager, login_user, login_required
import logging
import colorlog
from misc import send_request, Json
from config import load_config

from misc import PassAction, User, role_required, ProveData
from temp import student

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


@role_required("admin", "teacher", "student")
@login_required
@app.route('/diary')
async def diary():

    user_id = session['user_data']['id']  # Получаем ID пользователя из сессии

    if not user_id:
        flash("Are you the pirat?")
        redirect(url_for("about"))

    # payload = {
    #     "query": """
    #     SELECT
    #         t.day_of_week,
    #         t.start_time,
    #         t.end_time,
    #         s.subject_name,
    #         c.room_number,
    #         te.username AS teacher_name
    #     FROM
    #         Timetable t
    #     JOIN
    #         Subjects s ON t.subject_id = s.subject_id
    #     JOIN
    #         Classrooms c ON t.classroom_id = c.classroom_id
    #     JOIN
    #         Teachers te ON t.teacher_id = te.teacher_id
    #     JOIN
    #         Classes cl ON t.class_id = cl.class_id
    #     WHERE
    #         cl.class_id IN (
    #             SELECT class_id FROM Students WHERE user_id = $1
    #         )
    #     ORDER BY
    #         CASE
    #             WHEN t.day_of_week = 'Понедельник' THEN 1
    #             WHEN t.day_of_week = 'Вторник' THEN 2
    #             WHEN t.day_of_week = 'Среда' THEN 3
    #             WHEN t.day_of_week = 'Четверг' THEN 4
    #             WHEN t.day_of_week = 'Пятница' THEN 5
    #             WHEN t.day_of_week = 'Суббота' THEN 6
    #             WHEN t.day_of_week = 'Воскресенье' THEN 7
    #             ELSE 8  -- На случай, если день недели не соответствует ожидаемым значениям
    #         END,
    #         t.start_time
    #     """,
    #     "args": {"user_id": user_id}
    # }
    #
    # fetch = await send_request(server=app.config["server"], type="fetch", payload=payload)

    # schedule = fetch

    ###                                                                                   ^
    ### FETCH TEST, DELETE SCHEDULE BELOW | WHEN USING THE DATABASE, UNZIP THE ABOVE CODE |
    ###                                  \/

    schedule = [
        {"day_of_week": "Понедельник", "start_time": "8:30", "end_time": "09:55", "subject_name": "Технологии резрешения конфликтов", "room_number": "209", "teacher_name": "Гулевич Е.В."},
        {"day_of_week": "Понедельник", "start_time": "10:05", "end_time": "11:30", "subject_name": "Технологии резрешения конфликтов", "room_number": "209", "teacher_name": "Гулевич Е.В."},
        {"day_of_week": "Понедельник", "start_time": "11:40", "end_time": "13:05", "subject_name": "Практический курс перевода (2-го иностр. яз.)", "room_number": "214", "teacher_name": "Адамович С.В."},
        {"day_of_week": "Понедельник", "start_time": "13:30", "end_time": "14:55", "subject_name": "Практикум по культуре реч. общения (2 ин. яз.)", "room_number": "205", "teacher_name": "Адамович С.В."},
        {"day_of_week": "Понедельник", "start_time": "15:05", "end_time": "16:30", "subject_name": "Перевод специальных текстов", "room_number": "303", "teacher_name": "Нуретдинова А.Д."}
    ]

    required_keys = ["day_of_week", "start_time", "end_time", "subject_name", "room_number", "teacher_name"]

    if not all(all(key in item and item[key] for key in required_keys) for item in schedule):
        flash("Внутрення ошибка данных")
        redirect(url_for("MAIN"))
        raise Exception(f'Неполноценные данные required_keys = ["day_of_week", "start_time", "end_time", "subject_name", "room_number", "teacher_name"] schedule = {schedule}')

    return render_template("diary.html", schedule=schedule)

@app.route('/TeacherMain')
@role_required("teacher", "admin")
@login_required
async def TeacherMain():
    return render_template("TeacherMain.html")

@app.route('/journal', methods=['GET', 'POST'])
@role_required("teacher", "admin")
@login_required
async def journal():

    if request.method == 'POST':
        grade = request.form.get('grades')
        remark = request.form.get('remarks')
        student_id = request.form.get('student_ids')
        student_username = request.form.get('student_username')

        if grade:
            payload = {
                "query": "INSERT INTO grades (student_id, subject_id, grade) VALUES ($1, $2, $3);",
                "args": {
                    "student_id": student_id,
                    "subject_id": 0,  # Изменить на релизе!!! > добавить id предмета по которому ставиться оценка
                    "grade": grade
                }
            }
            fetch = await send_request(server=app.config['Server'], type="execute", payload=payload)
            flash(f"Оценка: {grade} успешно сохранена для: {student_username}")

        if remark:

            remark_data={
                "user_id": student_id,
                "username": student_username,
                "remark": remark
            }

            try:
                await Json(file_path="json_files/remarks.json",
                           data=remark_data).append_json_file()
            except Exception as e:
                print(e)
            flash(f"Замечание сохранено для: {student_username}")
        redirect(url_for("journal"))


    payload = {
        "query": "SELECT * FROM users WHERE role=$1;",
        "args": {"role": "student"}
    }

    fetch = await send_request(server=app.config['Server'], type="fetch", payload=payload)
    students = fetch

    return render_template("journal.html", students=students)

@app.route('/adminStudent')
@role_required("admin")
@login_required
async def adminStudent():

    payload = {
        "query": "SELECT * FROM student;",
        "args": None
    }

    students = await send_request(server=app.config['Server'], type="fetch", payload=payload)
    id = request.args.get('student_id')
    method = request.args.get('method')
    user_id = request.args.get('user_id')

    if method == "delete":
        payload = {
            "query": """
                    WITH deleted_student AS (
                        DELETE FROM student WHERE student_id = $1 RETURNING user_id
                    )
                    DELETE FROM users WHERE id IN (SELECT user_id FROM deleted_student);
                """,
            "args": {"id": int(id)}
        }
        execute = await send_request(server=app.config["Server"], type="execute", payload=payload)

        try:
            await Json(file_path="json_files/deleted_users.json",
                       data=[student for student in students if student["student_id"] == int(id)][0]).append_json_file()
        except Exception as e:
            print(e)
        flash("Student deleted successfully!")

        return redirect(url_for('adminStudent'))

    if method == "edit":

        return render_template("editStudent.html",
                               student=[student for student in students if student["student_id"] == int(id)][0])

    return render_template("adminStudent.html", students=students)


@app.route('/adminStudent/edit', methods=['GET', 'POST'])
@role_required("admin")
@login_required
async def edit_student():
    username = request.form.get('username')
    email = request.form.get('email')
    grade_id = request.form.get('grade_id')
    parent_id = request.form.get('parent_id')
    phone = request.form.get('phone')
    id = request.form.get('id')

    if not all([username, email, grade_id, parent_id, phone]):
        flash("Все поля должны быть заполнены.", "error")
        return redirect(url_for('adminStudent'))  # Возвращаемся к странице с учителями

    payload = {
        "query": """
            WITH updated_user AS (
                UPDATE users
                SET username = $1
                WHERE id = (
                    SELECT user_id FROM student WHERE student_id = $6
                )
                RETURNING id
            )
            UPDATE student
            SET username = $1, email = $2, grade_id = $3, parent_id = $4, phone = $5
            WHERE student_id = $6;
            """,
        "args": {
            "username": username,  # Имя
            "email": email,  # Email
            "grade_id": int(grade_id),  # Предмет
            "parent_id": int(parent_id),  # Предмет
            "phone": phone,  # Телефон
            "id": int(id)  # ID учителя
        }
    }

    # Отправляем запрос на сервер
    execute = await send_request(server=app.config["Server"], type="execute", payload=payload)
    return redirect(url_for('adminStudent'))


@app.route('/adminParent')
@role_required("admin")
@login_required
async def adminParent():
    payload = {
        "query": "SELECT * FROM parents;",
        "args": None
    }

    parents = await send_request(server=app.config['Server'], type="fetch", payload=payload)
    id = request.args.get('parent_id')
    method = request.args.get('method')
    user_id = request.args.get('user_id')

    if method == "delete":
        payload = {
            "query": """
                        WITH deleted_parent AS (
                            DELETE FROM parents WHERE parent_id = $1 RETURNING user_id
                        )
                        DELETE FROM users WHERE id IN (SELECT user_id FROM deleted_parent);
                    """,
            "args": {"id": int(id)}
        }
        execute = await send_request(server=app.config["Server"], type="execute", payload=payload)

        try:
            await Json(file_path="trash/deleted_users.json",
                       data=[parent for parent in parents if parent["parent_id"] == int(id)][0]).append_json_file()
        except Exception as e:
            print(e)
        flash("Parent deleted successfully!")

        return redirect(url_for('adminParent'))

    if method == "edit":
        return render_template("editParent.html",
                               parent=[parent for parent in parents if parent["parent_id"] == int(id)][0])

    return render_template("adminParent.html", parents=parents)


@app.route('/adminParent/edit', methods=['GET', 'POST'])
@role_required("admin")
@login_required
async def edit_parent():
    username = request.form.get('username')
    email = request.form.get('email')
    phone = request.form.get('phone')
    id = request.form.get('id')

    if not all([username, email, phone]):
        flash("Все поля должны быть заполнены.", "error")
        return redirect(url_for('adminParent'))  # Возвращаемся к странице с учителями

    payload = {
        "query": """
                WITH updated_user AS (
                    UPDATE users
                    SET username = $1
                    WHERE id = (
                        SELECT user_id FROM parents WHERE parent_id = $4
                    )
                    RETURNING id
                )
                UPDATE parents
                SET username = $1, email = $2, phone = $3
                WHERE parent_id = $4;
                """,
        "args": {
            "username": username,  # Имя
            "email": email,  # Email
            "phone": phone,  # Телефон
            "id": int(id)  # ID учителя
        }
    }

    # Отправляем запрос на сервер
    execute = await send_request(server=app.config["Server"], type="execute", payload=payload)
    return redirect(url_for('adminParent'))


@app.route('/adminTeacher', methods=['GET', 'POST'])
@role_required("admin")
@login_required
async def adminTeacher():
    payload = {
        "query": "SELECT * FROM teacher;",
        "args": None
    }

    teachers = await send_request(server=app.config['Server'], type="fetch", payload=payload)


    id = request.args.get('teacher_id')
    method = request.args.get('method')
    user_id = request.args.get('user_id')

    if method == "delete":
        payload = {
            "query": """
                WITH deleted_teacher AS (
                    DELETE FROM teacher WHERE id = $1 RETURNING user_id
                )
                DELETE FROM users WHERE id IN (SELECT user_id FROM deleted_teacher);
            """,
            "args": {"id": int(id)}
        }
        execute = await send_request(server=app.config["Server"], type="execute", payload=payload)

        try:
            await Json(file_path="trash/deleted_users.json", data=[teacher for teacher in teachers if teacher["id"] == int(id)][0]).append_json_file()
        except Exception as e:
            print(e)
        flash("Teacher deleted successfully!")

        return redirect(url_for('adminTeacher'))

    if method == "edit":
        return render_template("editTeacher.html", teacher=[teacher for teacher in teachers if teacher["id"] == int(id)][0])

    return render_template("adminTeacher.html", teachers=teachers)

@app.route('/adminTeacher/edit', methods=['GET', 'POST'])
@role_required("admin")
@login_required
async def edit_teacher():
    username = request.form.get('username')
    email = request.form.get('email')
    subject_id = request.form.get('subject_id')
    phone = request.form.get('phone')
    id = request.form.get('id')

    if not all([username, email, subject_id, phone]):
        flash("Все поля должны быть заполнены.", "error")
        return redirect(url_for('adminTeacher'))  # Возвращаемся к странице с учителями

    payload = {
        "query": """
        WITH updated_user AS (
            UPDATE users
            SET username = $1
            WHERE id = (
                SELECT user_id FROM teacher WHERE id = $5
            )
            RETURNING id
        )
        UPDATE teacher
        SET username = $1, email = $2, subject_id = $3, phone = $4
        WHERE id = $5;
        """,
        "args": {
            "username": username,        # Имя
            "email": email,          # Email
            "subject": int(subject_id),      # Предмет
            "phone": phone,          # Телефон
            "id": int(id)         # ID учителя
        }
    }

    # Отправляем запрос на сервер
    execute = await send_request(server=app.config["Server"], type="execute", payload=payload)
    return redirect(url_for('adminTeacher'))

@app.route('/adminDiary')
def adminDiary():
    return render_template("adminDiary.html")

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
