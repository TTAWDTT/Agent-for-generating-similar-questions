"""
问题生成提示词模板
基于原题生成相似问题
"""

QUESTION_GENERATION_PROMPT = """
你是一位{expert_description}，擅长根据给定的题目生成同类型的相似问题。

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
4. 难度水平保持一致
5. 确保问题有明确的答案

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
