from typing import List


class PromptManager:
    """提示词管理器"""
    
    # 领域标签映射
    DOMAIN_EXPERTS = {
        "数学": "数学教育专家",
        "物理": "物理学专家", 
        "化学": "化学专家",
        "生物": "生物学专家",
        "历史": "历史学专家",
        "地理": "地理学专家",
        "语文": "语文教学专家",
        "英语": "英语教学专家",
        "编程": "计算机编程专家",
        "算法": "算法与数据结构专家",
        "机器学习": "机器学习专家",
        "深度学习": "深度学习专家",
        "经济学": "经济学专家",
        "心理学": "心理学专家",
        "哲学": "哲学专家",
        "逻辑": "逻辑学专家"
    }
    
    @staticmethod
    def get_tagging_prompt(question: str, thinking_chain: str, answer: str) -> str:
        """获取问题标签识别提示词"""
        return f"""
请分析以下问题，并为其打上合适的领域标签。标签应该准确反映问题所涉及的学科领域和知识点。

问题：{question}

思维链：{thinking_chain}

答案：{answer}

请从以下领域中选择最相关的标签（可以选择多个）：
数学、物理、化学、生物、历史、地理、语文、英语、编程、算法、机器学习、深度学习、经济学、心理学、哲学、逻辑

请以JSON格式返回标签列表，例如：
{{"tags": ["数学", "逻辑"]}}

只返回JSON，不要其他解释。
"""
    
    @staticmethod
    def get_question_generation_prompt(tags: List[str], original_question: str, 
                                     thinking_chain: str, answer: str) -> str:
        """获取问题生成提示词"""
        expert_roles = []
        for tag in tags:
            if tag in PromptManager.DOMAIN_EXPERTS:
                expert_roles.append(PromptManager.DOMAIN_EXPERTS[tag])
        
        expert_description = "、".join(expert_roles) if expert_roles else "教育专家"
        
        return f"""
你是一位{expert_description}，擅长根据给定的题目生成同类型的相似问题。

原题目：{original_question}

原题思维链：{thinking_chain}

原题答案：{answer}

请基于以上原题，生成5道同样知识点但不同情境的问题。要求：
1. 保持相同的知识点和解题思路
2. 改变问题的具体情境、数值或背景
3. 难度水平保持一致
4. 确保问题有明确的答案

请以JSON格式返回，例如：
{{
    "questions": [
        "问题1内容",
        "问题2内容",
        "问题3内容",
        "问题4内容",
        "问题5内容"
    ]
}}

只返回JSON，不要其他解释。
"""
    
    @staticmethod
    def get_solution_prompt(tags: List[str], question: str) -> str:
        """获取问题解答提示词"""
        expert_roles = []
        for tag in tags:
            if tag in PromptManager.DOMAIN_EXPERTS:
                expert_roles.append(PromptManager.DOMAIN_EXPERTS[tag])
        
        expert_description = "、".join(expert_roles) if expert_roles else "教育专家"
        
        return f"""
你是一位{expert_description}，请详细解答以下问题。

问题：{question}

请提供：
1. 详细的思维链（逐步分析解题过程）
2. 最终答案

请以JSON格式返回，例如：
{{
    "thinking_chain": "详细的思维链，包括每一步的分析过程...",
    "answer": "最终答案"
}}

思维链要求：
- 思路清晰，步骤完整
- 每一步都有明确的推理依据
- 适当解释关键概念和方法
- 逻辑连贯，易于理解

只返回JSON，不要其他解释。
"""
