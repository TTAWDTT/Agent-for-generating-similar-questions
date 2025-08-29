import openai
import json
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
import re

load_dotenv()


class LLMClient:
    """LLM客户端封装"""
    
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY", os.getenv("OPENAI_API_KEY")),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1")
        )
        self.model = "deepseek-reasoner"
    
    def chat_completion(self, messages: List[Dict[str, str]], 
                       temperature: float = 0.7) -> str:
        """调用聊天完成API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=4000
            )
            return response.choices[0].message.content
        except Exception as e:
            # 规范化各种可能的错误格式（OpenAI SDK 异常、字典形式的错误等）
            try:
                if hasattr(e, 'args') and e.args and isinstance(e.args[0], dict):
                    err_info = e.args[0]
                    err_payload = err_info.get('error', err_info)
                    message = json.dumps(err_payload, ensure_ascii=False)
                else:
                    message = str(e)
            except Exception:
                message = str(e)

            print(f"LLM调用错误: {message}")
            # 抛出一个明确的 RuntimeError，便于上层捕获并将信息写入 state.error
            raise RuntimeError(message)
    
    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """解析JSON响应"""
        try:
            # 如果已经是 dict，直接返回（防止重复解析）
            if isinstance(response, dict):
                return response
            # 尝试找到JSON部分
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]

                # 将字符串内部的裸换行替换为 \n，并移除尾随逗号
                def _sanitize_for_json(s: str) -> str:
                    out = []
                    in_string = False
                    escape = False
                    for ch in s:
                        if in_string:
                            if escape:
                                out.append(ch)
                                escape = False
                            else:
                                if ch == '\\':
                                    out.append(ch)
                                    escape = True
                                elif ch == '"':
                                    out.append(ch)
                                    in_string = False
                                elif ch == '\n':
                                    out.append('\\n')
                                elif ch == '\r':
                                    # 忽略 CR 或在需要时可转换
                                    continue
                                else:
                                    out.append(ch)
                        else:
                            if ch == '"':
                                out.append(ch)
                                in_string = True
                            else:
                                out.append(ch)
                    res = ''.join(out)
                    # 去掉对象/数组末尾的尾随逗号
                    res = re.sub(r',\s*([}\]])', r'\1', res)
                    return res

                json_str = _sanitize_for_json(json_str)
                # 修复常见的非法反斜杠转义（如 \()）：为未知转义符前再补一个反斜杠
                try:
                    json_str = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', json_str)
                except Exception:
                    pass
                return json.loads(json_str)
            else:
                # 如果没找到JSON，尝试直接解析整个响应
                return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            print(f"原始响应: {response}")
            # 容错：若包含 questions 列表但整体 JSON 不完整，尽力提取可用的问题文本
            try:
                if isinstance(response, str) and '"questions"' in response:
                    # 提取所有完整的一行形式的 question 字段，忽略被截断的最后一项
                    matches = re.findall(r'\"question\"\s*:\s*\"([^\"\n\r]*)\"', response)
                    if matches:
                        return {"questions": matches}
            except Exception:
                pass
            raise e
