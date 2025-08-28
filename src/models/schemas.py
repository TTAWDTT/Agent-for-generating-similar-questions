from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class QuestionInput(BaseModel):
    """输入问题的数据模型"""
    question: str
    thinking_chain: str
    answer: str


class TaggedQuestion(BaseModel):
    """带标签的问题"""
    question: str
    thinking_chain: str
    answer: str
    domain_tags: List[str]


class GeneratedQuestion(BaseModel):
    """生成的问题"""
    id: Optional[int] = None
    original_question_id: Optional[int] = None
    question: str
    domain_tags: List[str]
    created_at: Optional[datetime] = None


class QuestionSolution(BaseModel):
    """问题解答"""
    id: Optional[int] = None
    question_id: int
    question: Optional[str] = None  # 通过关联查询获取的问题内容
    thinking_chain: str
    answer: str
    created_at: Optional[datetime] = None


class WorkflowState(BaseModel):
    """工作流状态"""
    input_question: Optional[QuestionInput] = None
    tagged_question: Optional[TaggedQuestion] = None
    generated_questions: List[GeneratedQuestion] = []
    solutions: List[QuestionSolution] = []
    current_step: str = "start"
    error: Optional[str] = None
