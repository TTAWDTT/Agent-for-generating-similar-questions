#!/usr/bin/env python3
"""
数据库迁移脚本
为现有数据库添加新的字段以支持扩展的标签系统和思维链检查
"""

import sqlite3
import os


def migrate_database(db_path: str = "questions.db"):
    """迁移数据库结构"""
    if not os.path.exists(db_path):
        print(f"数据库文件 {db_path} 不存在，无需迁移")
        return
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # 检查并添加新字段
        print("🔄 开始数据库迁移...")
        
        # 为 original_questions 表添加 question_type 字段
        try:
            cursor.execute("ALTER TABLE original_questions ADD COLUMN question_type TEXT DEFAULT '简答题'")
            print("✅ 为 original_questions 表添加 question_type 字段")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("ℹ️ original_questions.question_type 字段已存在")
            else:
                print(f"❌ 添加 original_questions.question_type 字段失败: {e}")
        
        # 为 generated_questions 表添加 question_type 字段
        try:
            cursor.execute("ALTER TABLE generated_questions ADD COLUMN question_type TEXT DEFAULT '简答题'")
            print("✅ 为 generated_questions 表添加 question_type 字段")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("ℹ️ generated_questions.question_type 字段已存在")
            else:
                print(f"❌ 添加 generated_questions.question_type 字段失败: {e}")
        
        # 为 question_solutions 表添加验证相关字段
        verification_fields = [
            ("verification_score", "INTEGER"),
            ("verification_passed", "BOOLEAN"), 
            ("verification_feedback", "TEXT")
        ]
        
        for field_name, field_type in verification_fields:
            try:
                cursor.execute(f"ALTER TABLE question_solutions ADD COLUMN {field_name} {field_type}")
                print(f"✅ 为 question_solutions 表添加 {field_name} 字段")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"ℹ️ question_solutions.{field_name} 字段已存在")
                else:
                    print(f"❌ 添加 question_solutions.{field_name} 字段失败: {e}")
        
        conn.commit()
        print("🎉 数据库迁移完成！")


if __name__ == "__main__":
    migrate_database()
