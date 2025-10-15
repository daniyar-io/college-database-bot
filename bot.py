import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any
import requests
import time
import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Настройки базы данных из .env
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "college_db"),
    "user": os.getenv("DB_USER", "postgres"), 
    "password": os.getenv("DB_PASSWORD", "2008"),
    "port": os.getenv("DB_PORT", "5432")
}

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8443013412:AAEBU9thmjqggPGPKCO9z13dNYA_l_Myx2M")

class CollegeDatabase:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        try:
            self.connection = psycopg2.connect(**DB_CONFIG)
            print("✅ Connected to PostgreSQL database")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params or ())
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                self.connection.commit()
                return []
        except Exception as e:
            print(f"❌ Query execution error: {e}")
            self.connection.rollback()
            return []
    
    # GET методы
    def get_all_students(self) -> List[Dict]:
        query = """
        SELECT s.*, g.name as group_name 
        FROM students s 
        LEFT JOIN groups g ON s.group_id = g.id
        ORDER BY s.id
        """
        return self.execute_query(query)
    
    def get_all_teachers(self) -> List[Dict]:
        query = """
        SELECT t.*, d.name as department_name 
        FROM teachers t 
        LEFT JOIN departments d ON t.department_id = d.id
        ORDER BY t.id
        """
        return self.execute_query(query)
    
    def get_all_groups(self) -> List[Dict]:
        query = "SELECT * FROM groups ORDER BY id"
        return self.execute_query(query)
    
    def get_all_departments(self) -> List[Dict]:
        query = "SELECT * FROM departments ORDER BY id"
        return self.execute_query(query)
    
    def get_all_subjects(self) -> List[Dict]:
        query = "SELECT * FROM subjects ORDER BY id"
        return self.execute_query(query)
    
    def get_all_grades(self) -> List[Dict]:
        query = """
        SELECT g.*, s.first_name as student_first_name, s.last_name as student_last_name,
               sub.name as subject_name, t.first_name as teacher_first_name, t.last_name as teacher_last_name
        FROM grades g
        JOIN students s ON g.student_id = s.id
        JOIN subjects sub ON g.subject_id = sub.id
        JOIN teachers t ON g.teacher_id = t.id
        ORDER BY g.id
        """
        return self.execute_query(query)
    
    def get_student_by_id(self, student_id: int) -> Dict:
        query = """
        SELECT s.*, g.name as group_name 
        FROM students s 
        LEFT JOIN groups g ON s.group_id = g.id 
        WHERE s.id = %s
        """
        result = self.execute_query(query, (student_id,))
        return result[0] if result else {}
    
    def get_teacher_by_id(self, teacher_id: int) -> Dict:
        query = """
        SELECT t.*, d.name as department_name 
        FROM teachers t 
        LEFT JOIN departments d ON t.department_id = d.id 
        WHERE t.id = %s
        """
        result = self.execute_query(query, (teacher_id,))
        return result[0] if result else {}

    def get_grade_by_id(self, grade_id: int) -> Dict:
        query = """
        SELECT g.*, s.first_name as student_first_name, s.last_name as student_last_name,
               sub.name as subject_name, t.first_name as teacher_first_name, t.last_name as teacher_last_name
        FROM grades g
        JOIN students s ON g.student_id = s.id
        JOIN subjects sub ON g.subject_id = sub.id
        JOIN teachers t ON g.teacher_id = t.id
        WHERE g.id = %s
        """
        result = self.execute_query(query, (grade_id,))
        return result[0] if result else {}

    # ADD методы
    def add_student(self, first_name: str, last_name: str, email: str, phone: str, group_id: int) -> bool:
        query = """
        INSERT INTO students (first_name, last_name, email, phone, group_id, enrollment_date)
        VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)
        """
        try:
            self.execute_query(query, (first_name, last_name, email, phone, group_id))
            return True
        except Exception as e:
            print(f"❌ Error adding student: {e}")
            return False
    
    def add_teacher(self, first_name: str, last_name: str, email: str, phone: str, department_id: int) -> bool:
        query = """
        INSERT INTO teachers (first_name, last_name, email, phone, department_id, hire_date)
        VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)
        """
        try:
            self.execute_query(query, (first_name, last_name, email, phone, department_id))
            return True
        except Exception as e:
            print(f"❌ Error adding teacher: {e}")
            return False
    
    def add_grade(self, student_id: int, subject_id: int, grade: int, teacher_id: int) -> bool:
        query = """
        INSERT INTO grades (student_id, subject_id, grade, teacher_id, exam_date)
        VALUES (%s, %s, %s, %s, CURRENT_DATE)
        """
        try:
            self.execute_query(query, (student_id, subject_id, grade, teacher_id))
            return True
        except Exception as e:
            print(f"❌ Error adding grade: {e}")
            return False

    # UPDATE методы
    def update_student(self, student_id: int, first_name: str, last_name: str, email: str, phone: str, group_id: int) -> bool:
        query = """
        UPDATE students 
        SET first_name = %s, last_name = %s, email = %s, phone = %s, group_id = %s
        WHERE id = %s
        """
        try:
            self.execute_query(query, (first_name, last_name, email, phone, group_id, student_id))
            return True
        except Exception as e:
            print(f"❌ Error updating student: {e}")
            return False
    
    def update_teacher(self, teacher_id: int, first_name: str, last_name: str, email: str, phone: str, department_id: int) -> bool:
        query = """
        UPDATE teachers 
        SET first_name = %s, last_name = %s, email = %s, phone = %s, department_id = %s
        WHERE id = %s
        """
        try:
            self.execute_query(query, (first_name, last_name, email, phone, department_id, teacher_id))
            return True
        except Exception as e:
            print(f"❌ Error updating teacher: {e}")
            return False
    
    def update_grade(self, grade_id: int, grade: int) -> bool:
        query = """
        UPDATE grades 
        SET grade = %s
        WHERE id = %s
        """
        try:
            self.execute_query(query, (grade, grade_id))
            return True
        except Exception as e:
            print(f"❌ Error updating grade: {e}")
            return False

    # DELETE методы
    def delete_student(self, student_id: int) -> bool:
        query = "DELETE FROM students WHERE id = %s"
        try:
            self.execute_query(query, (student_id,))
            return True
        except Exception as e:
            print(f"❌ Error deleting student: {e}")
            return False
    
    def delete_teacher(self, teacher_id: int) -> bool:
        query = "DELETE FROM teachers WHERE id = %s"
        try:
            self.execute_query(query, (teacher_id,))
            return True
        except Exception as e:
            print(f"❌ Error deleting teacher: {e}")
            return False
    
    def delete_grade(self, grade_id: int) -> bool:
        query = "DELETE FROM grades WHERE id = %s"
        try:
            self.execute_query(query, (grade_id,))
            return True
        except Exception as e:
            print(f"❌ Error deleting grade: {e}")
            return False

# Инициализация бота и базы данных
bot = telebot.TeleBot(TELEGRAM_TOKEN)
db = CollegeDatabase()

# Состояния для многошаговых операций
user_states = {}

def create_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        "🎓 Все студенты", "👨‍🏫 Все преподаватели", "📚 Все оценки",
        "➕ Добавить студента", "➕ Добавить преподавателя", "📝 Добавить оценку",
        "✏️ Редактировать студента", "✏️ Редактировать преподавателя", "✏️ Редактировать оценку",
        "🗑️ Удалить студента", "🗑️ Удалить преподавателя", "🗑️ Удалить оценку",
        "📊 Статистика"
    ]
    # Добавляем кнопки в 2 колонки
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            keyboard.add(KeyboardButton(buttons[i]), KeyboardButton(buttons[i+1]))
        else:
            keyboard.add(KeyboardButton(buttons[i]))
    return keyboard

@bot.message_handler(commands=['start', 'help'])
def start_message(message):
    user_states[message.chat.id] = None
    bot.send_message(
        message.chat.id,
        "🏫 Добро пожаловать в базу данных колледжа!\n"
        "Выберите действие из меню:",
        reply_markup=create_main_keyboard()
    )

# ПРОСМОТР ДАННЫХ
@bot.message_handler(func=lambda message: message.text == "🎓 Все студенты")
def all_students(message):
    try:
        students = db.get_all_students()
        if not students:
            bot.send_message(message.chat.id, "❌ Студенты не найдены")
            return
            
        response = "🎓 ВСЕ СТУДЕНТЫ:\n\n"
        for student in students[:15]:
            response += f"#{student['id']} {student['first_name']} {student['last_name']}"
            if student.get('group_name'):
                response += f" - {student['group_name']}"
            response += f"\n📧 {student.get('email', 'Нет email')}\n"
            response += "─" * 20 + "\n"
        
        if len(students) > 15:
            response += f"\n... и еще {len(students) - 15} студентов"
            
        bot.send_message(message.chat.id, response)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

@bot.message_handler(func=lambda message: message.text == "👨‍🏫 Все преподаватели")
def all_teachers(message):
    try:
        teachers = db.get_all_teachers()
        if not teachers:
            bot.send_message(message.chat.id, "❌ Преподаватели не найдены")
            return
            
        response = "👨‍🏫 ВСЕ ПРЕПОДАВАТЕЛИ:\n\n"
        for teacher in teachers:
            response += f"#{teacher['id']} {teacher['first_name']} {teacher['last_name']}"
            if teacher.get('department_name'):
                response += f" - {teacher['department_name']}"
            response += f"\n📧 {teacher.get('email', 'Нет email')}\n"
            response += "─" * 20 + "\n"
        
        bot.send_message(message.chat.id, response)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

@bot.message_handler(func=lambda message: message.text == "📚 Все оценки")
def all_grades(message):
    try:
        grades = db.get_all_grades()
        if not grades:
            bot.send_message(message.chat.id, "❌ Оценки не найдены")
            return
            
        response = "📚 ВСЕ ОЦЕНКИ:\n\n"
        for grade in grades[:10]:
            response += f"#{grade['id']} {grade['student_first_name']} {grade['student_last_name']}\n"
            response += f"📖 {grade['subject_name']}: {grade['grade']} баллов\n"
            response += f"👨‍🏫 {grade['teacher_first_name']} {grade['teacher_last_name']}\n"
            response += f"📅 {grade['exam_date']}\n"
            response += "─" * 20 + "\n"
        
        if len(grades) > 10:
            response += f"\n... и еще {len(grades) - 10} оценок"
            
        bot.send_message(message.chat.id, response)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

# ДОБАВЛЕНИЕ ДАННЫХ (остаются те же функции)
@bot.message_handler(func=lambda message: message.text == "➕ Добавить студента")
def add_student_start(message):
    user_states[message.chat.id] = "awaiting_student_data"
    
    groups = db.get_all_groups()
    groups_info = "\n".join([f"#{g['id']} - {g['name']}" for g in groups])
    
    bot.send_message(
        message.chat.id,
        f"📝 ДОБАВЛЕНИЕ СТУДЕНТА\n\n"
        f"Доступные группы:\n{groups_info}\n\n"
        f"Введите данные в формате:\n"
        f"<Имя> <Фамилия> <Email> <Телефон> <ID_группы>\n\n"
        f"Пример:\nИван Иванов ivan@mail.ru +79991234567 1"
    )

@bot.message_handler(func=lambda message: message.text == "➕ Добавить преподавателя")
def add_teacher_start(message):
    user_states[message.chat.id] = "awaiting_teacher_data"
    
    departments = db.get_all_departments()
    dept_info = "\n".join([f"#{d['id']} - {d['name']}" for d in departments])
    
    bot.send_message(
        message.chat.id,
        f"👨‍🏫 ДОБАВЛЕНИЕ ПРЕПОДАВАТЕЛЯ\n\n"
        f"Доступные отделы:\n{dept_info}\n\n"
        f"Введите данные в формате:\n"
        f"<Имя> <Фамилия> <Email> <Телефон> <ID_отдела>\n\n"
        f"Пример:\nПетр Петров petr@college.ru +79998887766 1"
    )

@bot.message_handler(func=lambda message: message.text == "📝 Добавить оценку")
def add_grade_start(message):
    user_states[message.chat.id] = "awaiting_grade_data"
    
    students = db.get_all_students()[:10]
    subjects = db.get_all_subjects()[:10]
    teachers = db.get_all_teachers()[:10]
    
    students_info = "\n".join([f"#{s['id']} - {s['first_name']} {s['last_name']}" for s in students])
    subjects_info = "\n".join([f"#{s['id']} - {s['name']}" for s in subjects])
    teachers_info = "\n".join([f"#{t['id']} - {t['first_name']} {t['last_name']}" for t in teachers])
    
    bot.send_message(
        message.chat.id,
        f"📚 ДОБАВЛЕНИЕ ОЦЕНКИ\n\n"
        f"Студенты:\n{students_info}\n\n"
        f"Предметы:\n{subjects_info}\n\n"
        f"Преподаватели:\n{teachers_info}\n\n"
        f"Введите данные в формате:\n"
        f"<ID_студента> <ID_предмета> <Оценка> <ID_преподавателя>\n\n"
        f"Пример:\n1 1 5 1\n\n"
        f"Оценка: от 1 до 5"
    )

# РЕДАКТИРОВАНИЕ ДАННЫХ
@bot.message_handler(func=lambda message: message.text == "✏️ Редактировать студента")
def edit_student_start(message):
    user_states[message.chat.id] = "awaiting_student_edit"
    
    students = db.get_all_students()[:10]
    groups = db.get_all_groups()
    
    students_info = "\n".join([f"#{s['id']} - {s['first_name']} {s['last_name']}" for s in students])
    groups_info = "\n".join([f"#{g['id']} - {g['name']}" for g in groups])
    
    bot.send_message(
        message.chat.id,
        f"✏️ РЕДАКТИРОВАНИЕ СТУДЕНТА\n\n"
        f"Студенты:\n{students_info}\n\n"
        f"Группы:\n{groups_info}\n\n"
        f"Введите данные в формате:\n"
        f"<ID_студента> <Имя> <Фамилия> <Email> <Телефон> <ID_группы>\n\n"
        f"Пример:\n1 Иван Иванов ivan@mail.ru +79991234567 1"
    )

@bot.message_handler(func=lambda message: message.text == "✏️ Редактировать преподавателя")
def edit_teacher_start(message):
    user_states[message.chat.id] = "awaiting_teacher_edit"
    
    teachers = db.get_all_teachers()[:10]
    departments = db.get_all_departments()
    
    teachers_info = "\n".join([f"#{t['id']} - {t['first_name']} {t['last_name']}" for t in teachers])
    dept_info = "\n".join([f"#{d['id']} - {d['name']}" for d in departments])
    
    bot.send_message(
        message.chat.id,
        f"✏️ РЕДАКТИРОВАНИЕ ПРЕПОДАВАТЕЛЯ\n\n"
        f"Преподаватели:\n{teachers_info}\n\n"
        f"Отделы:\n{dept_info}\n\n"
        f"Введите данные в формате:\n"
        f"<ID_преподавателя> <Имя> <Фамилия> <Email> <Телефон> <ID_отдела>\n\n"
        f"Пример:\n1 Петр Петров petr@college.ru +79998887766 1"
    )

@bot.message_handler(func=lambda message: message.text == "✏️ Редактировать оценку")
def edit_grade_start(message):
    user_states[message.chat.id] = "awaiting_grade_edit"
    
    grades = db.get_all_grades()[:10]
    grades_info = "\n".join([f"#{g['id']} - {g['student_first_name']} {g['student_last_name']}: {g['grade']} по {g['subject_name']}" for g in grades])
    
    bot.send_message(
        message.chat.id,
        f"✏️ РЕДАКТИРОВАНИЕ ОЦЕНКИ\n\n"
        f"Оценки:\n{grades_info}\n\n"
        f"Введите данные в формате:\n"
        f"<ID_оценки> <Новая_оценка>\n\n"
        f"Пример:\n1 5\n\n"
        f"Оценка: от 1 до 5"
    )

# УДАЛЕНИЕ ДАННЫХ
@bot.message_handler(func=lambda message: message.text == "🗑️ Удалить студента")
def delete_student_start(message):
    user_states[message.chat.id] = "awaiting_student_delete"
    
    students = db.get_all_students()[:10]
    students_info = "\n".join([f"#{s['id']} - {s['first_name']} {s['last_name']}" for s in students])
    
    bot.send_message(
        message.chat.id,
        f"🗑️ УДАЛЕНИЕ СТУДЕНТА\n\n"
        f"Студенты:\n{students_info}\n\n"
        f"Введите ID студента для удаления:\n\n"
        f"Пример:\n1"
    )

@bot.message_handler(func=lambda message: message.text == "🗑️ Удалить преподавателя")
def delete_teacher_start(message):
    user_states[message.chat.id] = "awaiting_teacher_delete"
    
    teachers = db.get_all_teachers()[:10]
    teachers_info = "\n".join([f"#{t['id']} - {t['first_name']} {t['last_name']}" for t in teachers])
    
    bot.send_message(
        message.chat.id,
        f"🗑️ УДАЛЕНИЕ ПРЕПОДАВАТЕЛЯ\n\n"
        f"Преподаватели:\n{teachers_info}\n\n"
        f"Введите ID преподавателя для удаления:\n\n"
        f"Пример:\n1"
    )

@bot.message_handler(func=lambda message: message.text == "🗑️ Удалить оценку")
def delete_grade_start(message):
    user_states[message.chat.id] = "awaiting_grade_delete"
    
    grades = db.get_all_grades()[:10]
    grades_info = "\n".join([f"#{g['id']} - {g['student_first_name']} {g['student_last_name']}: {g['grade']} по {g['subject_name']}" for g in grades])
    
    bot.send_message(
        message.chat.id,
        f"🗑️ УДАЛЕНИЕ ОЦЕНКИ\n\n"
        f"Оценки:\n{grades_info}\n\n"
        f"Введите ID оценки для удаления:\n\n"
        f"Пример:\n1"
    )

# ОБРАБОТКА ВВЕДЕННЫХ ДАННЫХ
@bot.message_handler(func=lambda message: user_states.get(message.chat.id))
def handle_user_input(message):
    state = user_states[message.chat.id]
    data = message.text.split()
    
    try:
        # ДОБАВЛЕНИЕ
        if state == "awaiting_student_data" and len(data) >= 5:
            first_name, last_name, email, phone, group_id = data[0], data[1], data[2], data[3], int(data[4])
            if db.add_student(first_name, last_name, email, phone, group_id):
                bot.send_message(message.chat.id, "✅ Студент успешно добавлен!")
            else:
                bot.send_message(message.chat.id, "❌ Ошибка при добавлении студента")
                
        elif state == "awaiting_teacher_data" and len(data) >= 5:
            first_name, last_name, email, phone, dept_id = data[0], data[1], data[2], data[3], int(data[4])
            if db.add_teacher(first_name, last_name, email, phone, dept_id):
                bot.send_message(message.chat.id, "✅ Преподаватель успешно добавлен!")
            else:
                bot.send_message(message.chat.id, "❌ Ошибка при добавлении преподавателя")
                
        elif state == "awaiting_grade_data" and len(data) >= 4:
            student_id, subject_id, grade, teacher_id = int(data[0]), int(data[1]), int(data[2]), int(data[3])
            student = db.get_student_by_id(student_id)
            teacher = db.get_teacher_by_id(teacher_id)
            if not student:
                bot.send_message(message.chat.id, "❌ Студент с таким ID не найден")
            elif not teacher:
                bot.send_message(message.chat.id, "❌ Преподаватель с таким ID не найден")
            elif 1 <= grade <= 5:
                if db.add_grade(student_id, subject_id, grade, teacher_id):
                    bot.send_message(message.chat.id, "✅ Оценка успешно добавлена!")
                else:
                    bot.send_message(message.chat.id, "❌ Ошибка при добавлении оценки")
            else:
                bot.send_message(message.chat.id, "❌ Оценка должна быть от 1 до 5")
        
        # РЕДАКТИРОВАНИЕ
        elif state == "awaiting_student_edit" and len(data) >= 6:
            student_id, first_name, last_name, email, phone, group_id = int(data[0]), data[1], data[2], data[3], data[4], int(data[5])
            if db.update_student(student_id, first_name, last_name, email, phone, group_id):
                bot.send_message(message.chat.id, "✅ Студент успешно обновлен!")
            else:
                bot.send_message(message.chat.id, "❌ Ошибка при обновлении студента")
                
        elif state == "awaiting_teacher_edit" and len(data) >= 6:
            teacher_id, first_name, last_name, email, phone, dept_id = int(data[0]), data[1], data[2], data[3], data[4], int(data[5])
            if db.update_teacher(teacher_id, first_name, last_name, email, phone, dept_id):
                bot.send_message(message.chat.id, "✅ Преподаватель успешно обновлен!")
            else:
                bot.send_message(message.chat.id, "❌ Ошибка при обновлении преподавателя")
                
        elif state == "awaiting_grade_edit" and len(data) >= 2:
            grade_id, new_grade = int(data[0]), int(data[1])
            if 1 <= new_grade <= 5:
                if db.update_grade(grade_id, new_grade):
                    bot.send_message(message.chat.id, "✅ Оценка успешно обновлена!")
                else:
                    bot.send_message(message.chat.id, "❌ Ошибка при обновлении оценки")
            else:
                bot.send_message(message.chat.id, "❌ Оценка должна быть от 1 до 5")
        
        # УДАЛЕНИЕ
        elif state == "awaiting_student_delete" and len(data) >= 1:
            student_id = int(data[0])
            if db.delete_student(student_id):
                bot.send_message(message.chat.id, "✅ Студент успешно удален!")
            else:
                bot.send_message(message.chat.id, "❌ Ошибка при удалении студента")
                
        elif state == "awaiting_teacher_delete" and len(data) >= 1:
            teacher_id = int(data[0])
            if db.delete_teacher(teacher_id):
                bot.send_message(message.chat.id, "✅ Преподаватель успешно удален!")
            else:
                bot.send_message(message.chat.id, "❌ Ошибка при удалении преподавателя")
                
        elif state == "awaiting_grade_delete" and len(data) >= 1:
            grade_id = int(data[0])
            if db.delete_grade(grade_id):
                bot.send_message(message.chat.id, "✅ Оценка успешно удалена!")
            else:
                bot.send_message(message.chat.id, "❌ Ошибка при удалении оценки")
                
        else:
            bot.send_message(message.chat.id, "❌ Неверный формат данных")
            
    except (ValueError, IndexError):
        bot.send_message(message.chat.id, "❌ Неверный формат данных. Проверьте ввод.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")
    
    # Сбрасываем состояние
    user_states[message.chat.id] = None

# Статистика
@bot.message_handler(func=lambda message: message.text == "📊 Статистика")
def show_stats(message):
    try:
        students = db.get_all_students()
        teachers = db.get_all_teachers()
        groups = db.get_all_groups()
        departments = db.get_all_departments()
        grades = db.get_all_grades()
        
        response = "📊 СТАТИСТИКА КОЛЛЕДЖА\n\n"
        response += f"🎓 Студентов: {len(students)}\n"
        response += f"👨‍🏫 Преподавателей: {len(teachers)}\n"
        response += f"🏫 Групп: {len(groups)}\n"
        response += f"📚 Отделов: {len(departments)}\n"
        response += f"📝 Оценок: {len(grades)}\n"
        response += f"📈 Всего записей: {len(students) + len(teachers) + len(grades)}"
        
        bot.send_message(message.chat.id, response)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

# Обработка неизвестных команд
@bot.message_handler(func=lambda message: True)
def unknown_message(message):
    bot.send_message(
        message.chat.id,
        "🤔 Используйте кнопки меню для навигации",
        reply_markup=create_main_keyboard()
    )

if __name__ == "__main__":
    print("🚀 Starting Telegram bot with FULL CRUD functionality...")
    
    # Проверяем интернет-соединение
    def check_internet():
        try:
            requests.get('https://api.telegram.org', timeout=10)
            return True
        except:
            return False
    
    if not check_internet():
        print("❌ Нет интернет-соединения! Проверьте сеть.")
        exit(1)
    
    print("✅ Интернет-соединение есть")
    
    # Сброс вебхука перед запуском
    try:
        requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset=-1", timeout=10)
        print("🔄 Вебхук сброшен")
    except Exception as e:
        print(f"⚠️ Не удалось сбросить вебхук: {e}")
    
    # Добавляем обработку сетевых ошибок
    max_retries = 5
    retry_delay = 10
    
    for attempt in range(max_retries):
        try:
            print(f"🔄 Попытка запуска {attempt + 1} из {max_retries}...")
            
            bot.polling(
                none_stop=True, 
                skip_pending=True, 
                interval=3,
                timeout=30,
                long_polling_timeout=20
            )
            
        except requests.exceptions.ConnectTimeout as e:
            print(f"❌ Таймаут подключения: {e}")
            print(f"⏳ Ждем {retry_delay} секунд перед повторной попыткой...")
            time.sleep(retry_delay)
            
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Ошибка подключения: {e}")
            print(f"⏳ Ждем {retry_delay} секунд перед повторной попыткой...")
            time.sleep(retry_delay)
            
        except telebot.apihelper.ApiTelegramException as e:
            if "Conflict" in str(e):
                print(f"❌ Конфликт ботов. Ждем {retry_delay} секунд...")
                time.sleep(retry_delay)
            else:
                print(f"❌ Ошибка Telegram API: {e}")
                break
                
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            break
            
        else:
            print("✅ Бот успешно завершил работу")
            break
    else:
        print("❌ Не удалось запустить бота после нескольких попыток")
        print("💡 Проверьте интернет-соединение и VPN/прокси")
    
    # Закрываем соединение с БД
    if hasattr(db, 'connection') and db.connection:
        db.connection.close()
        print("✅ Соединение с БД закрыто")