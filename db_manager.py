import sqlite3
import random
import os
import sys

LAST_NAME = [
    "김", "이", "박", "최", "정", "강", "조", "윤", "장", "임",
    "한", "오", "서", "신", "권", "황", "안", "송", "전", "홍", 
    "유", "고", "문", "양", "손"
]
FIRST_NAME = [
    "민준", "서준", "도윤", "주원", "예준", "현우", "준서", "지훈", "하준", "우진",
    "서연", "서윤", "지우", "서현", "민서", "하은", "지민", "윤서", "지안", "은서",
    "시우", "건우", "연우", "유준", "선우", "준우", "이준", "은우", "정우", "도현",
    "하윤", "아린", "수아", "지아", "수연", "다은", "예린", "채원", "시은", "소율"
]


class DBManager:
    def __init__(self, db_path=None):
        if db_path is None:
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, "student.db")
        self.db_path = db_path

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    # ── 초기화 ──────────────────────────────────────────────
    def init_db(self):
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    grade     INTEGER NOT NULL,
                    class_num INTEGER NOT NULL,
                    num       INTEGER NOT NULL,
                    name      TEXT    NOT NULL,
                    korean    INTEGER DEFAULT 0,
                    english   INTEGER DEFAULT 0,
                    math      INTEGER DEFAULT 0,
                    average   REAL    DEFAULT 0.0,
                    note      TEXT    DEFAULT '',
                    PRIMARY KEY (grade, class_num, num)
                )
            """)
            count = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
            if count == 0:
                self._seed_data(conn)

    def _seed_data(self, conn):
        rows = []
        for grade in range(1, 4):
            for class_num in range(1, 9):
                for num in range(1, random.randint(25, 30) + 1):
                    name    = random.choice(LAST_NAME) + random.choice(FIRST_NAME)
                    korean  = random.randint(40, 100)
                    english = random.randint(40, 100)
                    math    = random.randint(40, 100)
                    avg     = (korean + english + math) / 3
                    rows.append((grade, class_num, num, name, korean, english, math, avg))
        conn.executemany(
            "INSERT OR IGNORE INTO students "
            "(grade, class_num, num, name, korean, english, math, average) "
            "VALUES (?,?,?,?,?,?,?,?)",
            rows
        )

    # ── 조회 ────────────────────────────────────────────────
    def get_all_students(self):
        with self.get_connection() as conn:
            return conn.execute(
                "SELECT grade,class_num,num,name,korean,english,math,average,note "
                "FROM students ORDER BY grade,class_num,num"
            ).fetchall()

    def get_students_by_class(self, grade, class_num):
        with self.get_connection() as conn:
            return conn.execute(
                "SELECT grade,class_num,num,name,korean,english,math,average,note "
                "FROM students WHERE grade=? AND class_num=? ORDER BY num",
                (grade, class_num)
            ).fetchall()

    def search_students(self, name):
        with self.get_connection() as conn:
            return conn.execute(
                "SELECT grade,class_num,num,name,korean,english,math,average,note "
                "FROM students WHERE name LIKE ? ORDER BY grade,class_num,num",
                (f"%{name}%",)
            ).fetchall()

    def search_students_by_info(self, grade, class_num, num):
        with self.get_connection() as conn:
            sql = ("SELECT grade,class_num,num,name,korean,english,math,average,note "
                   "FROM students WHERE grade=? AND class_num=?")
            params = [grade, class_num]
            if num:
                sql += " AND num=?"
                params.append(num)
            sql += " ORDER BY num"
            return conn.execute(sql, params).fetchall()

    # ── 추가 / 삭제 ─────────────────────────────────────────
    def add_student(self, grade, class_num, num, name):
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT INTO students (grade,class_num,num,name) VALUES (?,?,?,?)",
                    (grade, class_num, num, name)
                )
            return True, "추가 성공"
        except sqlite3.IntegrityError:
            return False, "이미 존재하는 학번입니다."

    def delete_student(self, grade, class_num, num):
        with self.get_connection() as conn:
            cur = conn.execute(
                "DELETE FROM students WHERE grade=? AND class_num=? AND num=?",
                (grade, class_num, num)
            )
            return cur.rowcount > 0

    # ── 성적 수정 ────────────────────────────────────────────
    def update_scores(self, grade, class_num, num, korean, english, math):
        avg = (korean + english + math) / 3
        with self.get_connection() as conn:
            cur = conn.execute(
                "UPDATE students SET korean=?,english=?,math=?,average=? "
                "WHERE grade=? AND class_num=? AND num=?",
                (korean, english, math, avg, grade, class_num, num)
            )
            return cur.rowcount > 0

    def update_note(self, grade, class_num, num, note):
        with self.get_connection() as conn:
            cur = conn.execute(
                "UPDATE students SET note=? WHERE grade=? AND class_num=? AND num=?",
                (note, grade, class_num, num)
            )
            return cur.rowcount > 0

    # ── 번호 조회 ────────────────────────────────────────────
    def get_last_num(self, grade, class_num):
        """해당 학년/반의 마지막 번호 반환 (학생 없으면 0)"""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT MAX(num) FROM students WHERE grade=? AND class_num=?",
                (grade, class_num)
            ).fetchone()
            return row[0] if row[0] is not None else 0

    # ── 통계 ────────────────────────────────────────────────
    def get_subject_averages(self, grade=None):
        sql = "SELECT AVG(korean),AVG(english),AVG(math) FROM students"
        params = ()
        if grade:
            sql += " WHERE grade=?"
            params = (grade,)
        with self.get_connection() as conn:
            row = conn.execute(sql, params).fetchone()
            return [v or 0 for v in row]

    def get_class_averages(self, grade):
        with self.get_connection() as conn:
            return conn.execute(
                "SELECT class_num,AVG(korean),AVG(english),AVG(math),AVG(average) "
                "FROM students WHERE grade=? GROUP BY class_num ORDER BY class_num",
                (grade,)
            ).fetchall()

    def get_ranking(self, grade=None):
        sql = (
            "SELECT name,grade,class_num,num,korean,english,math,average,"
            "RANK() OVER (ORDER BY average DESC) "
            "FROM students"
        )
        params = ()
        if grade:
            sql += " WHERE grade=?"
            params = (grade,)
        sql += " ORDER BY average DESC"
        with self.get_connection() as conn:
            return conn.execute(sql, params).fetchall()

    def get_score_distribution(self, subject="average", grade=None):
        col = {"국어": "korean", "영어": "english", "수학": "math"}.get(subject, "average")
        sql = f"SELECT {col} FROM students"
        params = ()
        if grade:
            sql += " WHERE grade=?"
            params = (grade,)
        with self.get_connection() as conn:
            return [r[0] for r in conn.execute(sql, params).fetchall()]

    def get_total_count(self):
        with self.get_connection() as conn:
            return conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        
    def get_existing_nums(self, grade, class_num):
        """해당 학년/반에 존재하는 번호 목록"""
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT num FROM students WHERE grade=? AND class_num=? ORDER BY num",
                (grade, class_num)
            ).fetchall()
            return [r[0] for r in rows]

    def get_available_nums(self, grade, class_num):
        """해당 학년/반에 추가 가능한 번호 목록 (1~40 중 없는 번호)"""
        existing = set(self.get_existing_nums(grade, class_num))
        return [n for n in range(1, 41) if n not in existing]
    
    def get_students_by_grade(self, grade):
        """학년 전체 학생 조회"""
        with self.get_connection() as conn:
            return conn.execute(
                "SELECT grade,class_num,num,name,korean,english,math,average,note "
                "FROM students WHERE grade=? ORDER BY class_num,num",
                (grade,)
            ).fetchall()

    def get_student(self, grade, class_num, num):
        """특정 학생 1명 조회"""
        with self.get_connection() as conn:
            return conn.execute(
                "SELECT grade,class_num,num,name,korean,english,math,average,note "
                "FROM students WHERE grade=? AND class_num=? AND num=?",
                (grade, class_num, num)
            ).fetchall()