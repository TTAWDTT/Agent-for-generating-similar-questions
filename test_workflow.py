"""
问题生成工作流示例和测试
"""

import json
import os
from dotenv import load_dotenv
from src.workflow import QuestionGenerationWorkflow

# 加载环境变量
load_dotenv()


class WorkflowTester:
    """工作流测试器"""
    
    def __init__(self):
        self.workflow = QuestionGenerationWorkflow()
    
    def test_math_problem(self):
        """测试数学问题"""
        print("🧮 测试数学问题...")
        
        question = "一个圆的半径是5cm，求这个圆的面积。"
        thinking_chain = """
这是一个基础的几何问题，需要用到圆的面积公式。

已知：圆的半径 r = 5cm
求：圆的面积 S

圆的面积公式：S = πr²

代入数据：
S = π × 5²
S = π × 25
S = 25π cm²

如果需要数值结果：
S ≈ 25 × 3.14159 ≈ 78.54 cm²
"""
        answer = "25π cm² (约78.54 cm²)"
        
        return self.workflow.run(question, thinking_chain, answer)
    
    def test_physics_problem(self):
        """测试物理问题"""
        print("⚛️ 测试物理问题...")
        
        question = "一个质量为2kg的物体从高度10m处自由落下，求它落地时的速度。(g=10m/s²)"
        thinking_chain = """
这是一个自由落体运动问题。

已知：
- 质量 m = 2kg
- 初始高度 h = 10m  
- 重力加速度 g = 10m/s²
- 初始速度 v₀ = 0

求：落地时的速度 v

使用运动学公式：v² = v₀² + 2gh

由于是自由落下，v₀ = 0，所以：
v² = 2gh
v² = 2 × 10 × 10
v² = 200
v = √200 = 10√2 ≈ 14.14 m/s

注意：在自由落体运动中，速度与质量无关。
"""
        answer = "10√2 m/s (约14.14 m/s)"
        
        return self.workflow.run(question, thinking_chain, answer)
    
    def test_programming_problem(self):
        """测试编程问题"""
        print("💻 测试编程问题...")
        
        question = "写一个Python函数，计算斐波那契数列的第n项。"
        thinking_chain = """
斐波那契数列的定义：
F(0) = 0
F(1) = 1  
F(n) = F(n-1) + F(n-2) for n > 1

可以使用递归或迭代方法实现。考虑到效率，使用迭代方法：

def fibonacci(n):
    if n <= 1:
        return n
    
    a, b = 0, 1
    for i in range(2, n + 1):
        a, b = b, a + b
    
    return b

时间复杂度：O(n)
空间复杂度：O(1)
"""
        answer = """
def fibonacci(n):
    if n <= 1:
        return n
    
    a, b = 0, 1
    for i in range(2, n + 1):
        a, b = b, a + b
    
    return b
"""
        
        return self.workflow.run(question, thinking_chain, answer)
    
    def run_all_tests(self):
        """运行所有测试"""
        tests = [
            ("数学问题", self.test_math_problem),
            ("物理问题", self.test_physics_problem), 
            ("编程问题", self.test_programming_problem)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            print(f"\n{'='*60}")
            print(f"🧪 开始测试: {test_name}")
            print('='*60)
            
            try:
                state = test_func()
                results[test_name] = self.workflow.get_results(state)
                
                if state.error:
                    print(f"❌ 测试失败: {state.error}")
                else:
                    print(f"✅ 测试成功: 生成了{len(state.generated_questions)}道问题")
                    
            except Exception as e:
                print(f"❌ 测试异常: {e}")
                results[test_name] = {"error": str(e)}
        
        # 保存所有测试结果
        with open("test_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📊 所有测试结果已保存到 test_results.json")
        return results


def main():
    """主函数"""
    print("🚀 问题生成工作流测试系统")
    
    # 检查环境变量
    if not os.getenv("DEEPSEEK_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("❌ 错误: 请先在.env文件中设置API密钥")
        print("💡 请复制.env.example到.env并填入你的API密钥")
        return
    
    # 创建测试器
    tester = WorkflowTester()
    
    # 运行测试
    results = tester.run_all_tests()
    
    # 显示测试摘要
    print(f"\n{'='*60}")
    print("📋 测试摘要")
    print('='*60)
    
    for test_name, result in results.items():
        if "error" in result:
            print(f"❌ {test_name}: 失败 - {result['error']}")
        else:
            question_count = len(result.get('generated_questions', []))
            print(f"✅ {test_name}: 成功 - 生成{question_count}道问题")
    
    print("\n🎉 测试完成!")


if __name__ == "__main__":
    main()
