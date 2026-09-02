# ------------------------------
# 基础配置
# ------------------------------
#调用模型链接
from langchain_openai import ChatOpenAI
#模型输入历史队列模板
from langchain_core.prompts import MessagesPlaceholder
#提示词
from langchain_core.prompts import ChatPromptTemplate
#工具调用
from langchain_core.tools import tool
#环境变量加载
import os
#环境变量加载
from dotenv import load_dotenv
#高德天气工具
import requests
#skill工具
from langchain_core.tools import tool
#消息类型
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage



# 加载环境变量
load_dotenv()

prompt = ChatPromptTemplate.from_messages([
            ("system", """
            你是一个智能助手。规则：
            1. 用户询问天气/气温/是否下雨等问题时，必须调用 get_weather 工具查询真实数据；
            2. 非天气问题直接回答，不要调用工具；
            3. 必须基于工具返回的真实数据回答，不要编造；
            4. 回答自然简洁，不提"工具""API"等技术词汇。
            """),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
chat_history = []

@tool
def get_weather(city: str) -> str:
    """
    查询指定城市的实时天气。
    当用户询问某地天气、气温、是否下雨、穿什么衣服等问题时调用此工具。

    Args:
        city: 中文城市名，如"北京"、"上海"、"平顶山"
    """
    api_key = os.getenv("AMAP_API_KEY")
    if not api_key:
        return "未配置AMAP_API_KEY环境变量，天气查询功能不可用！"
    # 获取天气信息
    weather_resp = requests.get(
        os.getenv("AMAP_WEATHER_URL"),
        params={"key": api_key, "city": city, "output": "json"},
        timeout=10
    ).json()
    if weather_resp.get("status") != "1" or not weather_resp.get("lives"):
        return f"查询失败：获取天气信息失败"
    live = weather_resp["lives"][0]
    return (
        f"{live['city']} {live['reporttime']} - "
        f"温度{live['temperature']}℃，{live['weather']}，"
        f"湿度{live['humidity']}%，{live['winddirection']}风{live['windpower']}级"
    )
       


def test_chat_openai(test_prompt: str):
    # 初始化 ChatOpenAI 模型
    model = ChatOpenAI(
        model_name=os.getenv("SILICONFLOW_MODEL_NAME"),
        temperature=0.7,
        api_key=os.getenv("SILICONFLOW_API_KEY"),
        base_url = os.getenv("SILICONFLOW_BASE_URL")
    )
    #让模型知道有get_weather工具可用
    model_with_tools = model.bind_tools([get_weather])
    # 构造完整消息列表（含历史）
    messages = prompt.format_messages(chat_history=chat_history, input=test_prompt)
    #第一次调用模型是否决定调用工具
    response = model_with_tools.invoke(messages)

    if response.tool_calls:
        # 模型决定调用工具
        print(f"🔧 模型自动判断需要调用工具：{response.tool_calls}")
        messages.append(response)  # 把模型的工具调用决策加入消息

        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]

            # 执行工具
            if tool_name == "get_weather":
                tool_result = get_weather.invoke(tool_args)
            else:
                tool_result = f"未知工具：{tool_name}"
            print(f"🔍 工具执行结果：{tool_result}")

            # 把工具结果作为 ToolMessage 返回给模型
            messages.append(ToolMessage(content=tool_result, tool_call_id=tool_id))

        # 第二次调用：模型基于工具结果生成最终回答
        final_response = model_with_tools.invoke(messages)
        answer = final_response.content
    else:
        # 模型直接回答，无需工具
        answer = response.content

    # 更新对话历史（用 LangChain 标准消息类型）
    chat_history.append(HumanMessage(content=test_prompt))
    chat_history.append(AIMessage(content=answer))

    print(f"\n📝 最终回答：{answer}")
    # print(f"\n📚 对话历史：{chat_history}")
    return answer

