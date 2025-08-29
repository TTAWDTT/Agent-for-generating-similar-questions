"""
问题生成提示词模板
基于原题生成相似问题
"""

QUESTION_GENERATION_PROMPT = """
你是一位{domain_tags}领域的出题专家，擅长根据给定的题目生成同类型的相似问题。

原题目：{original_question}

原题思维链：{thinking_chain}

原题答案：{answer}

原题标签：
- 领域标签：{domain_tags}
- 题型标签：{question_type}

请基于以上原题，生成5道同样知识点和题型的相似问题。要求：
1. 保持相同的知识点和解题思路
2. 保持相同的题型（{question_type}）
3. 改变问题的具体情境、数值或背景
4. 确保问题有明确的答案
5. 如若没有情境，可为其补充一个合理的情境
6. 问题应该均衡分布在以下难度级别(每个级别至少占20%):
   - 基础级：适合入门者，关注基本概念、定义和简单应用
   - 中级：需要一定领域知识，涉及原理解释、案例分析和应用场景
   - 高级：需要深度思考，包括前沿发展、跨领域联系、复杂问题解决方案等
7. 问题表述要清晰、准确、专业，避免以下问题：
   - 避免模糊或过于宽泛的表述
   - 避免可以简单用"是/否"回答的封闭性问题
   - 避免包含误导性假设的问题
   - 避免重复或高度相似的问题   

请以JSON格式返回，例如：
{{
    "questions": [
        {{
            "question": "问题1内容",
            "domain_tags": ["数学", "统计学"],
            "question_type": "{question_type}"
        }},
        {{
            "question": "问题2内容", 
            "domain_tags": ["数学", "统计学"],
            "question_type": "{question_type}"
        }},
        {{
            "question": "问题3内容",
            "domain_tags": ["数学", "统计学"], 
            "question_type": "{question_type}"
        }},
        {{
            "question": "问题4内容",
            "domain_tags": ["数学", "统计学"],
            "question_type": "{question_type}"
        }},
        {{
            "question": "问题5内容",
            "domain_tags": ["数学", "统计学"],
            "question_type": "{question_type}"
        }}
    ]
}}

只返回JSON，不要其他解释。
"""
