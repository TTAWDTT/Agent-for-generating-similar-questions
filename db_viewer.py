"""
数据库查询工具
用于查看和分析存储的问题和解答数据
"""

import json
import sqlite3
from datetime import datetime
from src.database.db_manager import DatabaseManager


class DatabaseViewer:
    """数据库查看器"""
    
    def __init__(self, db_path: str = "questions.db"):
        self.db_manager = DatabaseManager(db_path)
    
    def show_all_solutions_with_questions(self):
        """显示所有解答及其对应的问题"""
        print("📚 所有问题解答（包含问题内容）")
        print("=" * 80)
        
        solutions = self.db_manager.get_all_solutions_with_questions()
        
        if not solutions:
            print("暂无数据")
            return
        
        for i, solution in enumerate(solutions, 1):
            print(f"\n{i}. 解答ID: {solution.id}")
            print(f"📝 问题: {solution.question}")
            print(f"💭 思维链: {solution.thinking_chain[:100]}...")
            print(f"✅ 答案: {solution.answer}")
            print(f"⏰ 创建时间: {solution.created_at}")
            print("-" * 60)
    
    def show_solution_with_full_context(self, solution_id: int):
        """显示解答的完整上下文"""
        print(f"🔍 解答 {solution_id} 的完整上下文")
        print("=" * 80)
        
        context = self.db_manager.get_solution_with_full_context(solution_id)
        
        if not context:
            print(f"未找到解答 ID {solution_id}")
            return
        
        print("📋 原始问题:")
        print(f"  问题: {context['original_question']['question']}")
        print(f"  标签: {', '.join(context['original_question']['domain_tags'])}")
        print(f"  答案: {context['original_question']['answer']}")
        
        print("\n🔄 生成的问题:")
        print(f"  问题: {context['generated_question']['question']}")
        print(f"  标签: {', '.join(context['generated_question']['domain_tags'])}")
        
        print("\n🧠 AI解答:")
        print(f"  思维链: {context['solution']['thinking_chain']}")
        print(f"  答案: {context['solution']['answer']}")
        
        print(f"\n⏰ 时间线:")
        print(f"  原问题创建: {context['original_question']['created_at']}")
        print(f"  新问题生成: {context['generated_question']['created_at']}")
        print(f"  解答生成: {context['solution']['created_at']}")
    
    def show_statistics(self):
        """显示数据库统计信息"""
        print("📊 数据库统计")
        print("=" * 50)
        
        with sqlite3.connect(self.db_manager.db_path) as conn:
            cursor = conn.cursor()
            
            # 统计原始问题数量
            cursor.execute("SELECT COUNT(*) FROM original_questions")
            original_count = cursor.fetchone()[0]
            
            # 统计生成问题数量
            cursor.execute("SELECT COUNT(*) FROM generated_questions")
            generated_count = cursor.fetchone()[0]
            
            # 统计解答数量
            cursor.execute("SELECT COUNT(*) FROM question_solutions")
            solution_count = cursor.fetchone()[0]
            
            # 统计领域分布
            cursor.execute("SELECT domain_tags FROM original_questions")
            tags_data = cursor.fetchall()
            
            all_tags = []
            for tags_str in tags_data:
                tags = json.loads(tags_str[0])
                all_tags.extend(tags)
            
            tag_counts = {}
            for tag in all_tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        print(f"📝 原始问题: {original_count}")
        print(f"🔄 生成问题: {generated_count}")
        print(f"🧠 解答数量: {solution_count}")
        
        if tag_counts:
            print(f"\n🏷️ 领域分布:")
            for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  {tag}: {count}")
    
    def export_to_json(self, filename: str = "database_export.json"):
        """导出数据到JSON文件"""
        print(f"💾 导出数据到 {filename}")
        
        solutions = self.db_manager.get_all_solutions_with_questions()
        
        export_data = {
            "export_time": datetime.now().isoformat(),
            "total_solutions": len(solutions),
            "solutions": []
        }
        
        for solution in solutions:
            export_data["solutions"].append({
                "solution_id": solution.id,
                "question_id": solution.question_id,
                "question": solution.question,
                "thinking_chain": solution.thinking_chain,
                "answer": solution.answer,
                "created_at": solution.created_at.isoformat() if solution.created_at else None
            })
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 成功导出 {len(solutions)} 条解答数据")

    def show_qa_overview(self, limit: int | None = None):
        """显示 QA 总览（问题/思维链/答案）"""
        data = self.db_manager.get_qa_overview(limit=limit)
        if not data:
            print("暂无数据")
            return
        print("🧾 QA 总览（问题/思维链/答案）")
        print("=" * 100)
        for i, row in enumerate(data, 1):
            print(f"{i}. 解答ID: {row['solution_id']} | 问题ID: {row['question_id']} | 时间: {row['created_at']}")
            print(f"📝 问题: {row['question']}")
            print(f"💭 思维链: {row['thinking_chain']}")
            print(f"✅ 答案: {row['answer']}")
            print("-" * 100)


def main():
    """主函数"""
    import sys
    
    viewer = DatabaseViewer()
    
    if len(sys.argv) < 2:
        print("📚 数据库查看工具")
        print("使用方法:")
        print("  python db_viewer.py stats              - 显示统计信息")
        print("  python db_viewer.py solutions          - 显示所有解答")
        print("  python db_viewer.py context <id>       - 显示解答的完整上下文")
        print("  python db_viewer.py export [filename]  - 导出数据到JSON")
        print("  python db_viewer.py qa [limit]         - 显示问题/思维链/答案总览")
        return
    
    command = sys.argv[1]
    
    if command == "stats":
        viewer.show_statistics()
    elif command == "solutions":
        viewer.show_all_solutions_with_questions()
    elif command == "context":
        if len(sys.argv) < 3:
            print("请提供解答ID")
            return
        try:
            solution_id = int(sys.argv[2])
            viewer.show_solution_with_full_context(solution_id)
        except ValueError:
            print("解答ID必须是数字")
    elif command == "export":
        filename = sys.argv[2] if len(sys.argv) > 2 else "database_export.json"
        viewer.export_to_json(filename)
    elif command == "qa":
        limit = None
        if len(sys.argv) > 2:
            try:
                limit = int(sys.argv[2])
            except ValueError:
                limit = None
        viewer.show_qa_overview(limit)
    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    main()
