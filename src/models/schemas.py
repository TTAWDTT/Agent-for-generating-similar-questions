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
    question_type: str  # 计算题、证明题、简答题


class GeneratedQuestion(BaseModel):
    """生成的问题"""
    id: Optional[int] = None
    original_question_id: Optional[int] = None
    question: str
    domain_tags: List[str]
    question_type: str  # 计算题、证明题、简答题
    created_at: Optional[datetime] = None


class QuestionSolution(BaseModel):
    """问题解答"""
    id: Optional[int] = None
    question_id: int
    question: Optional[str] = None  # 通过关联查询获取的问题内容
    thinking_chain: str
    answer: str
    verification_score: Optional[int] = None  # 思维链检查得分
    verification_passed: Optional[bool] = None  # 是否通过检查
    verification_feedback: Optional[str] = None  # 检查反馈
    created_at: Optional[datetime] = None


class VerificationResult(BaseModel):
    """思维链检查结果"""
    score: int
    passed: bool
    feedback: str
    suggestions: List[str] = []


class WorkflowState(BaseModel):
    """工作流状态"""
    input_question: Optional[QuestionInput] = None
    tagged_question: Optional[TaggedQuestion] = None
    generated_questions: List[GeneratedQuestion] = []
    solutions: List[QuestionSolution] = []
    verification_results: List[VerificationResult] = []  # 思维链检查结果
    current_step: str = "start"
    error: Optional[str] = None
