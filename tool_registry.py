"""
工具注册中心（单例）
- register(tool) 注册 LangChain @tool 装饰的工具
- all_tools() 返回全部工具，供 bind_tools 一次性绑定
- get(name) 按名称获取工具实例
"""
from typing import List, Dict, Optional
from langchain_core.tools import BaseTool


class ToolRegistry:
    _instance: Optional["ToolRegistry"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools: Dict[str, BaseTool] = {}
        return cls._instance

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def all_tools(self) -> List[BaseTool]:
        return list(self._tools.values())

    def get(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def names(self) -> List[str]:
        return list(self._tools.keys())


# 全局单例
registry = ToolRegistry()
