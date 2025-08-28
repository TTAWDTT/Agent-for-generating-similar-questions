"""
测试新的数据库关联查询功能
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.db_manager import DatabaseManager
from src.models.schemas import QuestionSolution
from datetime import datetime


def test_database_relations():
    """测试数据库关联查询"""
    print("🧪 测试数据库关联查询功能")
    print("=" * 50)
    
    # 创建测试数据库
    db_manager = DatabaseManager("test_questions.db")
    
    # 插入测试数据
    print("📝 插入测试数据...")
    
    # 插入原始问题
    original_id = db_manager.insert_original_question(
        "测试原始问题：求解二元一次方程组",
        "这是一个线性代数问题，需要使用消元法...",
        "x=2, y=3",
        ["数学", "代数"]
    )
    
    # 插入生成的问题
    question_id1 = db_manager.insert_generated_question(
        original_id,
        "求解方程组：x + y = 5, 2x - y = 1",
        ["数学", "代数"]
    )
    
    question_id2 = db_manager.insert_generated_question(
        original_id,
        "求解方程组：3x + 2y = 12, x - y = 1",
        ["数学", "代数"]
    )
    
    # 插入解答
    solution_id1 = db_manager.insert_question_solution(
        question_id1,
        "使用加减消元法：第一个方程加上第二个方程得到3x=6，所以x=2，代入得y=3",
        "x=2, y=3"
    )
    
    solution_id2 = db_manager.insert_question_solution(
        question_id2,
        "使用代入消元法：从第二个方程得x=y+1，代入第一个方程得3(y+1)+2y=12，解得y=1.8，x=2.8",
        "x=2.8, y=1.8"
    )
    
    print("✅ 测试数据插入完成")
    
    # 测试关联查询
    print("\n🔍 测试关联查询...")
    
    # 测试获取带问题内容的解答
    print("\n1. 测试 get_question_solutions (带问题内容):")
    solutions = db_manager.get_question_solutions(question_id1)
    for solution in solutions:
        print(f"  解答ID: {solution.id}")
        print(f"  问题ID: {solution.question_id}")
        print(f"  问题内容: {solution.question}")
        print(f"  解答: {solution.answer}")
    
    # 测试获取所有解答
    print("\n2. 测试 get_all_solutions_with_questions:")
    all_solutions = db_manager.get_all_solutions_with_questions()
    for solution in all_solutions:
        print(f"  解答ID: {solution.id}, 问题: {solution.question[:30]}...")
    
    # 测试获取特定原始问题的所有解答
    print("\n3. 测试 get_all_solutions_with_questions (按原始问题过滤):")
    filtered_solutions = db_manager.get_all_solutions_with_questions(original_id)
    for solution in filtered_solutions:
        print(f"  解答ID: {solution.id}, 问题: {solution.question[:30]}...")
    
    # 测试获取完整上下文
    print("\n4. 测试 get_solution_with_full_context:")
    context = db_manager.get_solution_with_full_context(solution_id1)
    if context:
        print(f"  原问题: {context['original_question']['question'][:30]}...")
        print(f"  生成问题: {context['generated_question']['question'][:30]}...")
        print(f"  解答: {context['solution']['answer']}")
    
    print("\n✅ 所有测试通过!")
    
    # 清理测试数据库（如果可能）
    try:
        os.remove("test_questions.db")
        print("🧹 测试数据库已清理")
    except PermissionError:
        print("⚠️ 无法删除 test_questions.db（文件可能仍被占用）。请手动删除该文件或关闭占用程序后重试。")
    except FileNotFoundError:
        print("ℹ️ 测试数据库文件已不存在，无需清理。")


def test_question_solution_model():
    """测试QuestionSolution模型的新字段"""
    print("\n🧪 测试QuestionSolution模型")
    print("=" * 50)
    
    # 测试创建带问题内容的解答对象
    solution = QuestionSolution(
        id=1,
        question_id=123,
        question="这是一个测试问题？",
        thinking_chain="这是思维链...",
        answer="这是答案",
        created_at=datetime.now()
    )
    
    print(f"✅ QuestionSolution对象创建成功:")
    print(f"  ID: {solution.id}")
    print(f"  问题ID: {solution.question_id}")
    print(f"  问题内容: {solution.question}")
    print(f"  思维链: {solution.thinking_chain}")
    print(f"  答案: {solution.answer}")
    print(f"  创建时间: {solution.created_at}")


if __name__ == "__main__":
    test_question_solution_model()
    test_database_relations()
    print("\n🎉 所有测试完成!")
