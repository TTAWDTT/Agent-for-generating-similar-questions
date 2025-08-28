from typing import List
from .templates.tagging_prompt import TAGGING_PROMPT
from .templates.generation_prompt import QUESTION_GENERATION_PROMPT  
from .templates.solution_prompt import SOLUTION_PROMPT
from .templates.verification_prompt import VERIFICATION_PROMPT


class PromptManager:
    """提示词管理器"""
    
    @staticmethod
    def get_tagging_prompt(question: str, thinking_chain: str, answer: str) -> str:
        """获取问题标签识别提示词"""
        return TAGGING_PROMPT.format(
            question=question,
            thinking_chain=thinking_chain,
            answer=answer
        )
    
    @staticmethod
    def get_question_generation_prompt(domain_tags: List[str], question_type: str,
                                     original_question: str, thinking_chain: str, answer: str) -> str:
        """获取问题生成提示词"""
        # 构建专家描述
        expert_roles = [f"{tag}领域的专家" for tag in domain_tags if tag and tag.strip()]
        expert_description = "、".join(expert_roles) if expert_roles else "教育专家"
        
        return QUESTION_GENERATION_PROMPT.format(
            expert_description=expert_description,
            original_question=original_question,
            thinking_chain=thinking_chain,
            answer=answer,
            domain_tags="、".join(domain_tags),
            question_type=question_type
        )
    
    @staticmethod
    def get_solution_prompt(domain_tags: List[str], question_type: str, question: str) -> str:
        """获取问题解答提示词"""
        # 构建专家描述
        expert_roles = [f"{tag}领域的专家" for tag in domain_tags if tag and tag.strip()]
        expert_description = "、".join(expert_roles) if expert_roles else "教育专家"
        
        return SOLUTION_PROMPT.format(
            expert_description=expert_description,
            question=question,
            domain_tags="、".join(domain_tags),
            question_type=question_type
        )
    
    @staticmethod
    def get_verification_prompt(domain_tags: List[str], question_type: str, 
                              question: str, thinking_chain: str, answer: str) -> str:
        """获取思维链检查提示词"""
        # 构建专家描述
        expert_roles = [f"{tag}领域的专家" for tag in domain_tags if tag and tag.strip()]
        expert_description = "、".join(expert_roles) if expert_roles else "教育专家"
        
        return VERIFICATION_PROMPT.format(
            expert_description=expert_description,
            question=question,
            domain_tags="、".join(domain_tags),
            question_type=question_type,
            thinking_chain=thinking_chain,
            answer=answer
        )
