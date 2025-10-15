import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from typing import List, Dict, Any

class CollegeDatabase:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        try:
            self.connection = psycopg2.connect(
                host="localhost",
                database="college_db",
                user="your_username",
                password="your_password",
                port="5432"
            )
            logging.info("Connected to PostgreSQL database")
        except Exception as e:
            logging.error(f"Database connection failed: {e}")
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params or ())
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                self.connection.commit()
                return []
        except Exception as e:
            logging.error(f"Query execution error: {e}")
            return []
    
    def get_all_students(self) -> List[Dict]:
        query = """
        SELECT s.*, g.name as group_name 
        FROM students s 
        LEFT JOIN groups g ON s.group_id = g.id
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
    
    def get_student_by_name(self, name: str) -> List[Dict]:
        query = """
        SELECT s.*, g.name as group_name 
        FROM students s 
        LEFT JOIN groups g ON s.group_id = g.id 
        WHERE s.first_name ILIKE %s OR s.last_name ILIKE %s
        """
        return self.execute_query(query, (f"%{name}%", f"%{name}%"))
    
    def get_all_teachers(self) -> List[Dict]:
        query = """
        SELECT t.*, d.name as department_name 
        FROM teachers t 
        LEFT JOIN departments d ON t.department_id = d.id
        """
        return self.execute_query(query)
    
    def get_teacher_by_id(self, teacher_id: int) -> Dict:
        query = """
        SELECT t.*, d.name as department_name 
        FROM teachers t 
        LEFT JOIN departments d ON t.department_id = d.id 
        WHERE t.id = %s
        """
        result = self.execute_query(query, (teacher_id,))
        return result[0] if result else {}
    
    def get_student_grades(self, student_id: int) -> List[Dict]:
        query = """
        SELECT g.grade, g.exam_date, s.name as subject_name, 
               t.first_name || ' ' || t.last_name as teacher_name
        FROM grades g
        JOIN subjects s ON g.subject_id = s.id
        JOIN teachers t ON g.teacher_id = t.id
        WHERE g.student_id = %s
        ORDER BY g.exam_date DESC
        """
        return self.execute_query(query, (student_id,))
    
    def get_group_students(self, group_id: int) -> List[Dict]:
        query = """
        SELECT s.* 
        FROM students s 
        WHERE s.group_id = %s
        """
        return self.execute_query(query, (group_id,))
    
    def get_teacher_subjects(self, teacher_id: int) -> List[Dict]:
        query = """
        SELECT DISTINCT s.name as subject_name, g.name as group_name
        FROM teaching t
        JOIN subjects s ON t.subject_id = s.id
        JOIN groups g ON t.group_id = g.id
        WHERE t.teacher_id = %s
        """
        return self.execute_query(query, (teacher_id,))

    def close(self):
        if self.connection:
            self.connection.close()