"""
反幻觉输出校验（FR-6）
- 数值来源回溯：回答中的数值必须能在工具结果中找到
- 工具失败时不编造数据
- 校验不通过则由调用方重试 1 次
"""
import re
from typing import List, Tuple

# 工具失败关键词
FAILURE_KEYWORDS = ["失败", "不可用", "错误", "查询失败", "无法", "异常", "error", "fail"]


def extract_numbers(text: str) -> List[str]:
    """提取文本中的数字（整数、小数、百分比）"""
    # 匹配数字（含小数），排除纯年份如 2024 过于宽泛，这里提取所有数字
    return re.findall(r"\d+\.?\d*", text)


def _is_tool_failure(result: str) -> bool:
    """判断工具结果是否为失败"""
    lower = result.lower()
    return any(kw in lower for kw in FAILURE_KEYWORDS)


class OutputValidator:
    def validate(self, answer: str, tool_results: List[str]) -> Tuple[bool, str]:
        """
        校验最终回答是否存在幻觉。
        返回 (是否通过, 原因)
        """
        # 无工具调用：纯闲聊，直接通过
        if not tool_results:
            return True, ""

        all_tool_text = "\n".join(tool_results)

        # 检查是否有工具失败
        has_failure = any(_is_tool_failure(r) for r in tool_results)

        # 提取回答中的数值
        numbers_in_answer = extract_numbers(answer)

        # 过滤掉无意义的数字（如单个 0、1，可能是序号）
        meaningful_numbers = [n for n in numbers_in_answer if float(n) > 1 or "." in n]

        # 数值来源回溯：回答中的数值必须出现在工具结果中
        for num in meaningful_numbers:
            if num not in all_tool_text:
                # 容错：如果数值在工具结果中以不同形式出现（如 25 和 25.0），视为通过
                found = False
                try:
                    num_f = float(num)
                    for tool_text in tool_results:
                        tool_nums = extract_numbers(tool_text)
                        for tn in tool_nums:
                            if abs(float(tn) - num_f) < 0.01:
                                found = True
                                break
                        if found:
                            break
                except ValueError:
                    pass
                if not found:
                    return False, f"数值 {num} 在工具结果中找不到来源，疑似编造"

        # 工具失败时，回答不应包含具体数值（除非来自工具结果）
        if has_failure and meaningful_numbers:
            for num in meaningful_numbers:
                if num not in all_tool_text:
                    return False, "工具调用失败，但回答中包含未来源的数值"

        return True, ""


# 全局实例
output_validator = OutputValidator()
