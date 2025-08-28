#!/usr/bin/env python3
"""
问题生成工作流命令行工具
"""

import argparse
import json
import os
from dotenv import load_dotenv
from src.workflow import QuestionGenerationWorkflow

# 加载环境变量
load_dotenv()


def run_interactive():
    """交互式运行模式"""
    print("🤖 问题生成工作流 - 交互模式")
    print("=" * 50)
    
    # 检查API密钥
    if not os.getenv("DEEPSEEK_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("❌ 错误: 请设置API密钥环境变量")
        return
    
    workflow = QuestionGenerationWorkflow()
    
    print("请输入问题信息（输入空行结束）:")
    
    # 获取问题
    print("\n📝 问题:")
    question_lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        question_lines.append(line)
    question = "\n".join(question_lines).strip()
    
    if not question:
        print("❌ 问题不能为空")
        return
    
    # 获取思维链
    print("\n💭 思维链:")
    thinking_lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        thinking_lines.append(line)
    thinking_chain = "\n".join(thinking_lines).strip()
    
    # 获取答案
    print("\n✅ 答案:")
    answer = input().strip()
    
    if not answer:
        print("❌ 答案不能为空")
        return
    
    print("\n" + "=" * 50)
    print("🚀 开始处理...")
    
    # 运行工作流
    result_state = workflow.run(question, thinking_chain, answer)
    results = workflow.get_results(result_state)
    
    # 显示结果
    display_results(results)


def run_from_file(file_path):
    """从文件运行"""
    print(f"📁 从文件运行: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        question = data.get('question', '')
        thinking_chain = data.get('thinking_chain', '')
        answer = data.get('answer', '')
        
        if not all([question, thinking_chain, answer]):
            print("❌ 错误: 文件必须包含question, thinking_chain, answer字段")
            return
        
        workflow = QuestionGenerationWorkflow()
        result_state = workflow.run(question, thinking_chain, answer)
        results = workflow.get_results(result_state)
        
        display_results(results)
        
        # 保存结果
        output_file = file_path.replace('.json', '_results.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 结果已保存到: {output_file}")
        
    except FileNotFoundError:
        print(f"❌ 错误: 找不到文件 {file_path}")
    except json.JSONDecodeError:
        print(f"❌ 错误: 文件 {file_path} 不是有效的JSON格式")
    except Exception as e:
        print(f"❌ 错误: {e}")


def display_results(results):
    """显示结果"""
    if "error" in results:
        print(f"❌ 执行失败: {results['error']}")
        return
    
    print("\n📋 执行结果:")
    print("=" * 50)
    
    # 显示原问题标签
    tags = results['original_question']['tags']
    print(f"🏷️ 原问题标签: {', '.join(tags)}")
    
    # 显示生成的问题和解答
    questions = results['generated_questions']
    print(f"\n📚 生成的问题和解答 ({len(questions)} 道):")
    print("-" * 50)
    
    for i, item in enumerate(questions, 1):
        print(f"\n🔢 问题 {i}:")
        print(f"📝 {item['question']}")
        
        if 'solution' in item:
            print(f"\n💭 思维链:")
            # 限制显示长度
            thinking = item['solution']['thinking_chain']
            if len(thinking) > 200:
                thinking = thinking[:200] + "..."
            print(f"{thinking}")
            print(f"\n✅ 答案: {item['solution']['answer']}")
        
        print("-" * 30)


def create_sample_file():
    """创建示例输入文件"""
    sample_data = {
        "question": "一个水池，进水管每小时可以注入池容量的1/10，出水管每小时可以排出池容量的1/15。现在水池是空的，如果同时打开进水管和出水管，多少小时可以把水池注满？",
        "thinking_chain": "这是一个关于工程问题的题目，需要考虑进水和出水的净效率。\n\n设水池总容量为1（单位容量）\n\n进水管每小时注入：1/10\n出水管每小时排出：1/15\n\n净进水速度 = 进水速度 - 出水速度\n= 1/10 - 1/15\n= 3/30 - 2/30\n= 1/30\n\n所以每小时净进水量为池容量的1/30\n\n要注满整个水池（容量为1），需要的时间为：\n时间 = 总容量 ÷ 净进水速度 = 1 ÷ (1/30) = 30小时",
        "answer": "30小时"
    }
    
    with open("sample_input.json", "w", encoding="utf-8") as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    print("📝 示例输入文件已创建: sample_input.json")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="问题生成工作流CLI工具")
    parser.add_argument("-i", "--interactive", action="store_true", 
                       help="交互模式运行")
    parser.add_argument("-f", "--file", type=str, 
                       help="从JSON文件读取输入")
    parser.add_argument("--create-sample", action="store_true",
                       help="创建示例输入文件")
    
    args = parser.parse_args()
    
    if args.create_sample:
        create_sample_file()
    elif args.interactive:
        run_interactive()
    elif args.file:
        run_from_file(args.file)
    else:
        print("🤖 问题生成工作流CLI工具")
        print("\n使用方法:")
        print("  python cli.py -i                    # 交互模式")
        print("  python cli.py -f input.json         # 从文件运行")
        print("  python cli.py --create-sample       # 创建示例文件")
        print("\n更多信息请使用: python cli.py --help")


if __name__ == "__main__":
    main()
