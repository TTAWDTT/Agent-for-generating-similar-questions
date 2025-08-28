import sqlite3
import json
from datetime import datetime
from typing import List, Optional
from ..models.schemas import GeneratedQuestion, QuestionSolution


class DatabaseManager:
    """SQLite数据库管理器"""
    
    def __init__(self, db_path: str = "questions.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建原始问题表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS original_questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    thinking_chain TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    domain_tags TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建生成问题表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS generated_questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_question_id INTEGER,
                    question TEXT NOT NULL,
                    domain_tags TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (original_question_id) REFERENCES original_questions (id)
                )
            """)
            
            # 创建问题解答表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS question_solutions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_id INTEGER NOT NULL,
                    thinking_chain TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (question_id) REFERENCES generated_questions (id)
                )
            """)
            
            conn.commit()
    
    def insert_original_question(self, question: str, thinking_chain: str, 
                               answer: str, domain_tags: List[str]) -> int:
        """插入原始问题"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO original_questions 
                (question, thinking_chain, answer, domain_tags)
                VALUES (?, ?, ?, ?)
            """, (question, thinking_chain, answer, json.dumps(domain_tags)))
            return cursor.lastrowid
    
    def insert_generated_question(self, original_question_id: int, 
                                question: str, domain_tags: List[str]) -> int:
        """插入生成的问题"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO generated_questions 
                (original_question_id, question, domain_tags)
                VALUES (?, ?, ?)
            """, (original_question_id, question, json.dumps(domain_tags)))
            return cursor.lastrowid
    
    def insert_question_solution(self, question_id: int, thinking_chain: str, 
                               answer: str) -> int:
        """插入问题解答"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO question_solutions 
                (question_id, thinking_chain, answer)
                VALUES (?, ?, ?)
            """, (question_id, thinking_chain, answer))
            return cursor.lastrowid
    
    def get_generated_questions(self, original_question_id: int) -> List[GeneratedQuestion]:
        """获取生成的问题"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, original_question_id, question, domain_tags, created_at
                FROM generated_questions
                WHERE original_question_id = ?
            """, (original_question_id,))
            
            questions = []
            for row in cursor.fetchall():
                questions.append(GeneratedQuestion(
                    id=row[0],
                    original_question_id=row[1],
                    question=row[2],
                    domain_tags=json.loads(row[3]),
                    created_at=datetime.fromisoformat(row[4])
                ))
            return questions
    
    def get_question_solutions(self, question_id: int) -> List[QuestionSolution]:
        """获取问题解答"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT qs.id, qs.question_id, gq.question, qs.thinking_chain, qs.answer, qs.created_at
                FROM question_solutions qs
                JOIN generated_questions gq ON qs.question_id = gq.id
                WHERE qs.question_id = ?
            """, (question_id,))
            
            solutions = []
            for row in cursor.fetchall():
                solutions.append(QuestionSolution(
                    id=row[0],
                    question_id=row[1],
                    question=row[2],  # 通过关联查询获取的问题内容
                    thinking_chain=row[3],
                    answer=row[4],
                    created_at=datetime.fromisoformat(row[5])
                ))
            return solutions
    
    def get_all_solutions_with_questions(self, original_question_id: Optional[int] = None) -> List[QuestionSolution]:
        """获取所有解答，包含问题内容和标签信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if original_question_id:
                # 获取特定原始问题生成的所有解答
                cursor.execute("""
                    SELECT qs.id, qs.question_id, gq.question, qs.thinking_chain, qs.answer, qs.created_at
                    FROM question_solutions qs
                    JOIN generated_questions gq ON qs.question_id = gq.id
                    WHERE gq.original_question_id = ?
                    ORDER BY qs.created_at DESC
                """, (original_question_id,))
            else:
                # 获取所有解答
                cursor.execute("""
                    SELECT qs.id, qs.question_id, gq.question, qs.thinking_chain, qs.answer, qs.created_at
                    FROM question_solutions qs
                    JOIN generated_questions gq ON qs.question_id = gq.id
                    ORDER BY qs.created_at DESC
                """)
            
            solutions = []
            for row in cursor.fetchall():
                solutions.append(QuestionSolution(
                    id=row[0],
                    question_id=row[1],
                    question=row[2],
                    thinking_chain=row[3],
                    answer=row[4],
                    created_at=datetime.fromisoformat(row[5])
                ))
            return solutions
    
    def get_solution_with_full_context(self, solution_id: int) -> Optional[dict]:
        """获取解答的完整上下文信息，包括原始问题、生成问题、解答等"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    qs.id as solution_id,
                    qs.thinking_chain,
                    qs.answer as solution_answer,
                    qs.created_at as solution_created_at,
                    gq.id as generated_question_id,
                    gq.question as generated_question,
                    gq.domain_tags as generated_tags,
                    gq.created_at as question_created_at,
                    oq.id as original_question_id,
                    oq.question as original_question,
                    oq.thinking_chain as original_thinking,
                    oq.answer as original_answer,
                    oq.domain_tags as original_tags,
                    oq.created_at as original_created_at
                FROM question_solutions qs
                JOIN generated_questions gq ON qs.question_id = gq.id
                JOIN original_questions oq ON gq.original_question_id = oq.id
                WHERE qs.id = ?
            """, (solution_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return {
                "solution": {
                    "id": row[0],
                    "thinking_chain": row[1],
                    "answer": row[2],
                    "created_at": row[3]
                },
                "generated_question": {
                    "id": row[4],
                    "question": row[5],
                    "domain_tags": json.loads(row[6]),
                    "created_at": row[7]
                },
                "original_question": {
                    "id": row[8],
                    "question": row[9],
                    "thinking_chain": row[10],
                    "answer": row[11],
                    "domain_tags": json.loads(row[12]),
                    "created_at": row[13]
                }
            }
