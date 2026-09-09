"""
故障诊断工具（FR-9）
- 基于 JSON 知识库的关键词匹配
- 返回分步骤排查清单 + 多轮追问建议
"""
import os
import json
from typing import Optional

from langchain_core.tools import tool
from dotenv import load_dotenv

from tool_registry import registry

load_dotenv()

KB_PATH = os.getenv(
    "FAULT_KB_PATH",
    os.path.join(os.path.dirname(__file__), "fault_kb.json"),
)


def _load_kb() -> dict:
    with open(KB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _match_fault(symptom: str) -> Optional[dict]:
    """关键词匹配故障条目，返回匹配度最高的条目"""
    kb = _load_kb()
    symptom_lower = symptom.lower()
    best_match = None
    best_score = 0
    for fault in kb["faults"]:
        score = sum(1 for kw in fault["keywords"] if kw.lower() in symptom_lower)
        if score > best_score:
            best_score = score
            best_match = fault
    return best_match if best_score > 0 else None


@tool
def diagnose_fault(symptom: str) -> str:
    """
    运维故障诊断。当用户描述服务器故障、性能问题、报错等需要排查的问题时调用此工具。
    返回分步骤排查清单和建议追问的问题。

    Args:
        symptom: 故障现象描述，如"CPU飙高"、"服务宕机了"、"磁盘满了"
    """
    fault = _match_fault(symptom)
    if not fault:
        return (
            "未匹配到具体故障类型。请提供更详细的故障现象，例如：\n"
            "- 是哪台服务器？\n"
            "- 具体现象是什么（CPU高/内存不足/服务宕机/网络不通/数据库慢）？\n"
            "- 问题持续多久了？\n"
            "你也可以直接描述现象，我会给出排查步骤。"
        )

    steps_text = "\n".join(fault["steps"])
    follow_up = "、".join(fault["follow_up"])
    return (
        f"【{fault['title']}】排查步骤：\n{steps_text}\n\n"
        f"为进一步定位，建议确认：{follow_up}"
    )


# 注册到工具中心
registry.register(diagnose_fault)
