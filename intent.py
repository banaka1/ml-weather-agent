"""
意图识别器
- 用 LLM 对用户输入做意图分类
- 输出 {chat, weather, nl2sql, diagnose, unknown} + 置信度
- 置信度 < 0.6 回退为 chat
"""
import os
import json
from typing import Tuple
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

INTENTS = ["chat", "weather", "nl2sql", "diagnose", "unknown"]

_CLASSIFY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一个意图分类器。根据用户输入判断其意图，只能从以下类别中选择一个：
- chat: 普通闲聊、问候、无明确工具需求的问题
- weather: 查询天气、气温、是否下雨、穿衣建议等
- nl2sql: 查询服务器/主机/CPU/内存/磁盘/数据库等运维数据，需要查数据库
- diagnose: 服务器故障、报错、性能问题排查，需要诊断步骤
- unknown: 无法判断

请严格以 JSON 格式返回，不要输出其他内容：
{{"intent": "类别", "confidence": 0.0~1.0}}"""),
    ("human", "{input}")
])


class IntentClassifier:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name=os.getenv("SILICONFLOW_MODEL_NAME"),
            temperature=0.0,
            api_key=os.getenv("SILICONFLOW_API_KEY"),
            base_url=os.getenv("SILICONFLOW_BASE_URL"),
        )

    def classify(self, message: str) -> Tuple[str, float]:
        """返回 (intent, confidence)，置信度 < 0.6 回退 chat"""
        try:
            resp = self.llm.invoke(_CLASSIFY_PROMPT.format_messages(input=message))
            text = resp.content.strip()
            # 兼容模型可能输出 ```json ... ``` 包裹
            if text.startswith("```"):
                text = text.strip("`")
                if text.lower().startswith("json"):
                    text = text[4:]
            data = json.loads(text.strip())
            intent = data.get("intent", "unknown")
            confidence = float(data.get("confidence", 0.0))
        except (json.JSONDecodeError, ValueError, KeyError, Exception):
            intent, confidence = "unknown", 0.0

        if intent not in INTENTS:
            intent = "unknown"
        if confidence < 0.6:
            intent = "chat"
        return intent, confidence


# 全局实例
intent_classifier = IntentClassifier()
