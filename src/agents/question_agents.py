import json
from typing import List
from ..models.schemas import WorkflowState, TaggedQuestion, GeneratedQuestion, QuestionSolution, VerificationResult
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
            domain_tags = result.get("domain_tags", [])
            question_type = result.get("question_type", "简答题")
            
            # 创建带标签的问题
            tagged_question = TaggedQuestion(
                question=input_question.question,
                thinking_chain=input_question.thinking_chain,
                answer=input_question.answer,
                domain_tags=domain_tags,
                question_type=question_type
            )
            
            state.tagged_question = tagged_question
            state.current_step = "tagged"
            
            print(f"问题标签识别完成: 领域标签={domain_tags}, 题型={question_type}")
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
                tagged_question.domain_tags,
                tagged_question.question_type
            )
            
            # 生成问题生成提示词
            prompt = self.prompt_manager.get_question_generation_prompt(
                tagged_question.domain_tags,
                tagged_question.question_type,
                tagged_question.question,
                tagged_question.thinking_chain,
                tagged_question.answer
            )
            
            # 调用LLM生成问题
            messages = [{"role": "user", "content": prompt}]
            response = self.llm_client.chat_completion(messages)
            
            # 解析响应
            result = self.llm_client.parse_json_response(response)
            questions_data = result.get("questions", [])
            
            # 创建生成的问题对象并保存到数据库
            generated_questions = []
            for question_data in questions_data:
                if isinstance(question_data, dict):
                    question_text = question_data.get("question", "")
                    domain_tags = question_data.get("domain_tags", tagged_question.domain_tags)
                    question_type = question_data.get("question_type", tagged_question.question_type)
                else:
                    # 兼容旧格式（纯字符串）
                    question_text = str(question_data)
                    domain_tags = tagged_question.domain_tags
                    question_type = tagged_question.question_type
                
                question_id = self.db_manager.insert_generated_question(
                    original_id, question_text, domain_tags, question_type
                )
                
                generated_question = GeneratedQuestion(
                    id=question_id,
                    original_question_id=original_id,
                    question=question_text,
                    domain_tags=domain_tags,
                    question_type=question_type
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
                    question.question_type,
                    question.question
                )
                
                # 调用LLM解题
                messages = [{"role": "user", "content": prompt}]
                response = self.llm_client.chat_completion(messages)
                
                # 解析响应
                result = self.llm_client.parse_json_response(response)
                thinking_chain = result.get("thinking_chain", "")
                answer = result.get("answer", "")
                
                # 保存解答到数据库（暂不设置验证信息）
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


class QuestionVerificationAgent:
    """思维链检查代理"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.prompt_manager = PromptManager()
        self.db_manager = DatabaseManager()
    
    def verify_solutions(self, state: WorkflowState) -> WorkflowState:
        """检查解答的思维链质量"""
        try:
            solutions = state.solutions
            generated_questions = state.generated_questions
            
            if not solutions or not generated_questions:
                raise ValueError("解答或问题为空")
            
            verification_results = []
            verified_solutions = []
            
            for i, solution in enumerate(solutions):
                if i >= len(generated_questions):
                    break
                    
                question = generated_questions[i]
                max_attempts = 2  # 最多重试2次
                attempt = 0
                
                while attempt < max_attempts:
                    attempt += 1
                    print(f"检查第{i+1}题解答 (第{attempt}次尝试)...")
                    
                    # 生成检查提示词
                    prompt = self.prompt_manager.get_verification_prompt(
                        question.domain_tags,
                        question.question_type,
                        question.question,
                        solution.thinking_chain,
                        solution.answer
                    )
                    
                    # 调用LLM进行检查
                    messages = [{"role": "user", "content": prompt}]
                    response = self.llm_client.chat_completion(messages)
                    
                    # 解析检查结果
                    result = self.llm_client.parse_json_response(response)
                    score = result.get("score", 0)
                    passed = result.get("passed", False)
                    feedback = result.get("feedback", "")
                    suggestions = result.get("suggestions", [])
                    
                    verification_result = VerificationResult(
                        score=score,
                        passed=passed,
                        feedback=feedback,
                        suggestions=suggestions
                    )
                    
                    # 更新数据库中的验证信息
                    self.db_manager.update_solution_verification(
                        solution.id, score, passed, feedback
                    )
                    
                    if passed:
                        # 检查通过，更新解答对象
                        solution.verification_score = score
                        solution.verification_passed = passed
                        solution.verification_feedback = feedback
                        verified_solutions.append(solution)
                        verification_results.append(verification_result)
                        print(f"✅ 第{i+1}题检查通过 (得分: {score})")
                        break
                    else:
                        print(f"❌ 第{i+1}题检查未通过 (得分: {score}), 重新生成解答...")
                        
                        # 重新生成解答
                        prompt = self.prompt_manager.get_solution_prompt(
                            question.domain_tags,
                            question.question_type,
                            question.question
                        )
                        
                        messages = [{"role": "user", "content": prompt}]
                        response = self.llm_client.chat_completion(messages)
                        
                        result = self.llm_client.parse_json_response(response)
                        solution.thinking_chain = result.get("thinking_chain", "")
                        solution.answer = result.get("answer", "")
                        
                        # 更新数据库
                        self.db_manager.insert_question_solution(
                            question.id,
                            solution.thinking_chain,
                            solution.answer
                        )
                        
                        if attempt == max_attempts:
                            # 达到最大重试次数，仍然记录结果
                            solution.verification_score = score
                            solution.verification_passed = passed
                            solution.verification_feedback = feedback
                            verified_solutions.append(solution)
                            verification_results.append(verification_result)
                            print(f"⚠️ 第{i+1}题达到最大重试次数，保留最后结果 (得分: {score})")
            
            state.solutions = verified_solutions
            state.verification_results = verification_results
            state.current_step = "verified"
            
            passed_count = sum(1 for r in verification_results if r.passed)
            print(f"✅ 思维链检查完成: {passed_count}/{len(verification_results)} 题通过检查")
            return state
            
        except Exception as e:
            state.error = f"思维链检查失败: {str(e)}"
            print(f"思维链检查错误: {e}")
            return state
