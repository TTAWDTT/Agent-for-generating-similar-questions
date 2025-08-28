import json
import os
from dotenv import load_dotenv
from src.workflow import QuestionGenerationWorkflow

# 加载环境变量
load_dotenv()


def main():
    """主程序"""
    print("🤖 问题生成工作流系统")
    print("=" * 50)
    
    # 检查环境变量
    if not os.getenv("DEEPSEEK_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("❌ 错误: 请设置 DEEPSEEK_API_KEY 或 OPENAI_API_KEY 环境变量")
        return
    
    # 创建工作流
    workflow = QuestionGenerationWorkflow()
    
    # 示例输入
    sample_question = """
有一个水池，进水管每小时可以注入池容量的1/10，出水管每小时可以排出池容量的1/15。
现在水池是空的，如果同时打开进水管和出水管，多少小时可以把水池注满？
"""
    
    sample_thinking = """
这是一个关于工程问题的题目，需要考虑进水和出水的净效率。

设水池总容量为1（单位容量）

进水管每小时注入：1/10
出水管每小时排出：1/15

净进水速度 = 进水速度 - 出水速度
= 1/10 - 1/15
= 3/30 - 2/30
= 1/30

所以每小时净进水量为池容量的1/30

要注满整个水池（容量为1），需要的时间为：
时间 = 总容量 ÷ 净进水速度 = 1 ÷ (1/30) = 30小时
"""
    
    sample_answer = "30小时"
    
    print("📝 输入问题示例:")
    print(f"问题: {sample_question.strip()}")
    print(f"答案: {sample_answer}")
    print("\n" + "=" * 50)
    
    # 运行工作流
    result_state = workflow.run(
        question=sample_question.strip(),
        thinking_chain=sample_thinking.strip(),
        answer=sample_answer
    )
    
    # 获取并显示结果
    results = workflow.get_results(result_state)
    
    if "error" in results:
        print(f"❌ 执行失败: {results['error']}")
        return
    
    print("\n📋 执行结果:")
    print("=" * 50)
    
    # 显示原问题标签
    print(f"🏷️ 原问题标签: {', '.join(results['original_question']['tags'])}")
    
    # 显示生成的问题和解答
    print(f"\n📚 生成的问题和解答 ({len(results['generated_questions'])} 道):")
    print("-" * 50)
    
    for i, item in enumerate(results['generated_questions'], 1):
        print(f"\n问题 {i} (ID: {item['id']}):")
        print(f"📝 {item['question']}")
        
        if 'solution' in item:
            print(f"\n💭 思维链:")
            print(f"{item['solution']['thinking_chain']}")
            print(f"\n✅ 答案: {item['solution']['answer']}")
        
        print("-" * 30)
    
    # 保存结果到文件
    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 结果已保存到 results.json")
    print("🗄️ 数据已存储到 questions.db 数据库")
    print("\n📊 查看数据库内容:")
    print("  python db_viewer.py stats      - 查看统计信息")
    print("  python db_viewer.py solutions  - 查看所有解答")
    print("🎉 工作流执行完成!")


if __name__ == "__main__":
    main()
