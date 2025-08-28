import json
from typing import List
from ..models.schemas import WorkflowState, TaggedQuestion, GeneratedQuestion, QuestionSolution
from ..prompts.prompt_manager import PromptManager
from ..utils.llm_client import LLMClient
from ..database.db_manager import DatabaseManager


class QuestionTaggingAgent:
    """问题标签识别代理"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.prompt_manager = PromptManager()
    
    def tag_question(self, state: WorkflowState) -> WorkflowState:
        """为问题打标签"""
        try:
            input_question = state.input_question
            if not input_question:
                raise ValueError("输入问题为空")
            
            # 生成标签识别提示词
            prompt = self.prompt_manager.get_tagging_prompt(
                input_question.question,
                input_question.thinking_chain,
                input_question.answer
            )
            
            # 调用LLM进行标签识别
            messages = [{"role": "user", "content": prompt}]
            response = self.llm_client.chat_completion(messages)
            
            # 解析响应
            result = self.llm_client.parse_json_response(response)
            tags = result.get("tags", [])
            
            # 创建带标签的问题
            tagged_question = TaggedQuestion(
                question=input_question.question,
                thinking_chain=input_question.thinking_chain,
                answer=input_question.answer,
                domain_tags=tags
            )
            
            state.tagged_question = tagged_question
            state.current_step = "tagged"
            
            print(f"问题标签识别完成: {tags}")
            return state
            
        except Exception as e:
            state.error = f"标签识别失败: {str(e)}"
            print(f"标签识别错误: {e}")
            return state


class QuestionGenerationAgent:
    """问题生成代理"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.prompt_manager = PromptManager()
        self.db_manager = DatabaseManager()
    
    def generate_questions(self, state: WorkflowState) -> WorkflowState:
        """生成相似问题"""
        try:
            tagged_question = state.tagged_question
            if not tagged_question:
                raise ValueError("标签问题为空")
            
            # 首先保存原始问题到数据库
            original_id = self.db_manager.insert_original_question(
                tagged_question.question,
                tagged_question.thinking_chain,
                tagged_question.answer,
                tagged_question.domain_tags
            )
            
            # 生成问题生成提示词
            prompt = self.prompt_manager.get_question_generation_prompt(
                tagged_question.domain_tags,
                tagged_question.question,
                tagged_question.thinking_chain,
                tagged_question.answer
            )
            
            # 调用LLM生成问题
            messages = [{"role": "user", "content": prompt}]
            response = self.llm_client.chat_completion(messages)
            
            # 解析响应
            result = self.llm_client.parse_json_response(response)
            questions = result.get("questions", [])
            
            # 创建生成的问题对象并保存到数据库
            generated_questions = []
            for question_text in questions:
                question_id = self.db_manager.insert_generated_question(
                    original_id, question_text, tagged_question.domain_tags
                )
                
                generated_question = GeneratedQuestion(
                    id=question_id,
                    original_question_id=original_id,
                    question=question_text,
                    domain_tags=tagged_question.domain_tags
                )
                generated_questions.append(generated_question)
            
            state.generated_questions = generated_questions
            state.current_step = "questions_generated"
            
            print(f"生成了 {len(generated_questions)} 道相似问题")
            return state
            
        except Exception as e:
            state.error = f"问题生成失败: {str(e)}"
            print(f"问题生成错误: {e}")
            return state


class QuestionSolvingAgent:
    """问题解答代理"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.prompt_manager = PromptManager()
        self.db_manager = DatabaseManager()
    
    def solve_questions(self, state: WorkflowState) -> WorkflowState:
        """解答生成的问题"""
        try:
            generated_questions = state.generated_questions
            if not generated_questions:
                raise ValueError("生成的问题为空")
            
            solutions = []
            for question in generated_questions:
                # 生成解题提示词
                prompt = self.prompt_manager.get_solution_prompt(
                    question.domain_tags,
                    question.question
                )
                
                # 调用LLM解题
                messages = [{"role": "user", "content": prompt}]
                response = self.llm_client.chat_completion(messages)
                
                # 解析响应
                result = self.llm_client.parse_json_response(response)
                thinking_chain = result.get("thinking_chain", "")
                answer = result.get("answer", "")
                
                # 保存解答到数据库
                solution_id = self.db_manager.insert_question_solution(
                    question.id,
                    thinking_chain,
                    answer
                )
                
                solution = QuestionSolution(
                    id=solution_id,
                    question_id=question.id,
                    question=question.question,  # 添加问题内容
                    thinking_chain=thinking_chain,
                    answer=answer
                )
                solutions.append(solution)
                
                print(f"完成问题解答: {question.question[:50]}...")
            
            state.solutions = solutions
            state.current_step = "completed"
            
            print(f"完成了 {len(solutions)} 道问题的解答")
            return state
            
        except Exception as e:
            state.error = f"问题解答失败: {str(e)}"
            print(f"问题解答错误: {e}")
            return state
