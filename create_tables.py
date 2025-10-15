import psycopg2
from psycopg2 import sql

DB_CONFIG = {
    "host": "localhost",
    "database": "college_db",
    "user": "postgres", 
    "password": "2008",  
    "port": "5432"
}

def create_tables():
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("🔧 Создание таблиц...")
        
        # Таблица отделов
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            head_teacher_id INTEGER
        )
        """)
        
        # Таблица учителей
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(100) UNIQUE,
            phone VARCHAR(20),
            department_id INTEGER REFERENCES departments(id),
            hire_date DATE
        )
        """)
        
        # Таблица групп
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id SERIAL PRIMARY KEY,
            name VARCHAR(20) NOT NULL,
            department_id INTEGER REFERENCES departments(id),
            start_date DATE,
            end_date DATE,
            curator_id INTEGER REFERENCES teachers(id)
        )
        """)
        
        # Таблица студентов
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(100) UNIQUE,
            phone VARCHAR(20),
            group_id INTEGER REFERENCES groups(id),
            enrollment_date DATE
        )
        """)
        
        # Таблица предметов
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            department_id INTEGER REFERENCES departments(id)
        )
        """)
        
        # Таблица преподавания
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS teaching (
            id SERIAL PRIMARY KEY,
            teacher_id INTEGER REFERENCES teachers(id),
            subject_id INTEGER REFERENCES subjects(id),
            group_id INTEGER REFERENCES groups(id)
        )
        """)
        
        # Таблица оценок
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS grades (
            id SERIAL PRIMARY KEY,
            student_id INTEGER REFERENCES students(id),
            subject_id INTEGER REFERENCES subjects(id),
            grade INTEGER CHECK (grade BETWEEN 1 AND 5),
            exam_date DATE,
            teacher_id INTEGER REFERENCES teachers(id)
        )
        """)
        
        conn.commit()
        print("✅ Все таблицы успешно созданы!")
        
        # Добавляем тестовые данные
        print("📝 Добавление тестовых данных...")
        add_test_data(cursor, conn)
        
    except Exception as e:
        print(f"❌ Ошибка при создании таблиц: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

def add_test_data(cursor, conn):
    try:
        # Добавляем отделы
        cursor.execute("INSERT INTO departments (name) VALUES ('Программирование') ON CONFLICT DO NOTHING")
        cursor.execute("INSERT INTO departments (name) VALUES ('Дизайн') ON CONFLICT DO NOTHING")
        
        # Добавляем преподавателей
        cursor.execute("""
        INSERT INTO teachers (first_name, last_name, email, phone, department_id, hire_date) 
        VALUES 
        ('Иван', 'Петров', 'ivan@college.ru', '+79991112233', 1, '2020-01-15'),
        ('Мария', 'Сидорова', 'maria@college.ru', '+79994445566', 2, '2019-03-20')
        ON CONFLICT DO NOTHING
        """)
        
        # Добавляем группы
        cursor.execute("""
        INSERT INTO groups (name, department_id, start_date, end_date, curator_id) 
        VALUES 
        ('П-21', 1, '2023-09-01', '2025-06-30', 1),
        ('Д-22', 2, '2023-09-01', '2025-06-30', 2)
        ON CONFLICT DO NOTHING
        """)
        
        # Добавляем студентов
        cursor.execute("""
        INSERT INTO students (first_name, last_name, email, phone, group_id, enrollment_date) 
        VALUES 
        ('Алексей', 'Иванов', 'alex@mail.ru', '+79991234567', 1, '2023-09-01'),
        ('Елена', 'Смирнова', 'elena@mail.ru', '+79992345678', 1, '2023-09-01'),
        ('Дмитрий', 'Козлов', 'dmitry@mail.ru', '+79993456789', 2, '2023-09-01')
        ON CONFLICT DO NOTHING
        """)
        
        # Добавляем предметы
        cursor.execute("""
        INSERT INTO subjects (name, department_id) 
        VALUES 
        ('Python программирование', 1),
        ('Веб-дизайн', 2),
        ('Базы данных', 1)
        ON CONFLICT DO NOTHING
        """)
        
        # Добавляем оценки
        cursor.execute("""
        INSERT INTO grades (student_id, subject_id, grade, teacher_id, exam_date) 
        VALUES 
        (1, 1, 5, 1, '2024-01-20'),
        (1, 3, 4, 1, '2024-01-25'),
        (2, 1, 5, 1, '2024-01-20'),
        (3, 2, 5, 2, '2024-01-22')
        ON CONFLICT DO NOTHING
        """)
        
        conn.commit()
        print("✅ Тестовые данные добавлены!")
        
    except Exception as e:
        print(f"❌ Ошибка при добавлении тестовых данных: {e}")

if __name__ == "__main__":
    create_tables()