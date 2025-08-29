from langgraph.graph import StateGraph, END
from typing import Dict, Any
from .models.schemas import WorkflowState, QuestionInput
from .agents.question_agents import (
    QuestionTaggingAgent, 
    QuestionGenerationAgent, 
    QuestionSolvingAgent,
    QuestionVerificationAgent
)


class QuestionGenerationWorkflow:
    """问题生成工作流"""
    
    def __init__(self):
        self.tagging_agent = QuestionTaggingAgent()
        self.generation_agent = QuestionGenerationAgent()
        self.solving_agent = QuestionSolvingAgent()
        self.verification_agent = QuestionVerificationAgent()
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """构建工作流图"""
        # 创建状态图
        workflow = StateGraph(WorkflowState)
        
        # 添加节点
        workflow.add_node("tag_question", self._tag_question_node)
        workflow.add_node("generate_questions", self._generate_questions_node)
        workflow.add_node("solve_questions", self._solve_questions_node)
        workflow.add_node("verify_solutions", self._verify_solutions_node)
        
        # 添加边
        workflow.add_edge("tag_question", "generate_questions")
        workflow.add_edge("generate_questions", "solve_questions")
        workflow.add_edge("solve_questions", "verify_solutions")
        workflow.add_edge("verify_solutions", END)
        
        # 设置入口点
        workflow.set_entry_point("tag_question")
        
        return workflow.compile()
    
    def _tag_question_node(self, state: WorkflowState) -> WorkflowState:
        """问题标签识别节点"""
        print("🏷️ 开始问题标签识别...")
        return self.tagging_agent.tag_question(state)
    
    def _generate_questions_node(self, state: WorkflowState) -> WorkflowState:
        """问题生成节点"""
        if state.error:
            return state
        
        print("🔄 开始生成相似问题...")
        return self.generation_agent.generate_questions(state)
    
    def _solve_questions_node(self, state: WorkflowState) -> WorkflowState:
        """问题解答节点"""
        if state.error:
            return state
        
        print("🧠 开始解答生成的问题...")
        return self.solving_agent.solve_questions(state)
    
    def _verify_solutions_node(self, state: WorkflowState) -> WorkflowState:
        """思维链检查节点"""
        if state.error:
            return state
        
        print("🔍 开始检查思维链质量...")
        return self.verification_agent.verify_solutions(state)
    
    def run(self, question: str, thinking_chain: str, answer: str) -> WorkflowState:
        """运行工作流"""
        print("🚀 启动问题生成工作流...")
        
        # 创建初始状态
        initial_state = WorkflowState(
            input_question=QuestionInput(
                question=question,
                thinking_chain=thinking_chain,
                answer=answer
            ),
            current_step="start"
        )
        
        # 运行工作流
        try:
            final_state = self.workflow.invoke(initial_state)

            # LangGraph 常常返回字典形式的状态，这里将其转换为 WorkflowState，而不是当成错误
            if isinstance(final_state, dict):
                try:
                    final_state = WorkflowState(**final_state)
                except Exception:
                    # 若转换失败，再尝试读取其中的 error 字段
                    err_msg = final_state.get('error') if isinstance(final_state, dict) else str(final_state)
                    print(f"❌ 工作流执行失败: {err_msg or final_state}")
                    return WorkflowState(input_question=initial_state.input_question, error=str(err_msg or final_state))

            if final_state.error:
                print(f"❌ 工作流执行失败: {final_state.error}")
            else:
                print("✅ 工作流执行成功!")
                print(f"📊 生成了 {len(final_state.generated_questions)} 道问题")
                print(f"📝 完成了 {len(final_state.solutions)} 个解答")

            return final_state
            
        except Exception as e:
            print(f"❌ 工作流执行出错: {e}")
            error_state = WorkflowState(
                input_question=initial_state.input_question,
                error=str(e)
            )
            return error_state
    
    def get_results(self, state: WorkflowState) -> Dict[str, Any]:
        """获取结果摘要"""
        if state.error:
            return {"error": state.error}
        
        results = {
            "original_question": {
                "question": state.input_question.question,
                "domain_tags": state.tagged_question.domain_tags if state.tagged_question else [],
                "question_type": state.tagged_question.question_type if state.tagged_question else ""
            },
            "generated_questions": [],
            "solutions": [],
            "verification_summary": {
                "total": len(state.verification_results),
                "passed": sum(1 for r in state.verification_results if r.passed),
                "average_score": sum(r.score for r in state.verification_results) / len(state.verification_results) if state.verification_results else 0
            }
        }
        
        # 组合问题和解答
        for i, question in enumerate(state.generated_questions):
            question_data = {
                "id": question.id,
                "question": question.question,
                "domain_tags": question.domain_tags,
                "question_type": question.question_type
            }
            
            # 找到对应的解答
            if i < len(state.solutions):
                solution = state.solutions[i]
                question_data["solution"] = {
                    "thinking_chain": solution.thinking_chain,
                    "answer": solution.answer,
                    "verification_score": solution.verification_score,
                    "verification_passed": solution.verification_passed,
                    "verification_feedback": solution.verification_feedback
                }
            
            results["generated_questions"].append(question_data)
        
        return results
