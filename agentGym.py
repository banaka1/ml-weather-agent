import os
import logging
import requests
import streamlit as st
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
# 新增：导入记忆相关组件（核心修改1）
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate

# ------------------------------
# 基础配置（替换为高德API Key）
# ------------------------------
load_dotenv()
AMAP_API_KEY = os.getenv("AMAP_API_KEY")  # 高德API Key

# 常量定义
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "deepseek-r1:1.5b"
# 高德天气API地址（实时天气）
AMAP_WEATHER_URL = "https://restapi.amap.com/v3/weather/weatherInfo"

# Streamlit页面配置
st.set_page_config(
    page_title="智能天气助手",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------------------
# 高德天气工具（国内数据源，精准实时）
# ------------------------------
class WeatherTool:
    """高德天气查询工具（国内城市精准）"""
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or AMAP_API_KEY

    def _get_city_adcode(self, city: str) -> Optional[str]:
        """获取城市的高德行政编码（关键：精准定位城市）"""
        if not self.api_key:
            return None
        # 高德地理编码API（根据城市名查adcode）
        geo_url = "https://restapi.amap.com/v3/geocode/geo"
        params = {
            "key": self.api_key,
            "address": city.strip(),
            "output": "json"
        }
        try:
            response = requests.get(geo_url, params=params, timeout=10)
            data = response.json()
            if data["status"] == "1" and len(data["geocodes"]) > 0:
                return data["geocodes"][0]["adcode"]  # 返回行政编码
        except Exception as e:
            st.error(f"获取城市编码失败：{str(e)}")
        return None

    def _validate_input(self, city: str) -> bool:
        """校验输入城市是否合法"""
        if not isinstance(city, str) or len(city.strip()) == 0:
            st.error("城市名不能为空或格式错误")
            return False
        return True

    def run(self, city: str) -> Dict[str, Any]:
        """执行天气查询（高德API）"""
        if not self._validate_input(city):
            return {
                "success": False,
                "observation": "查询失败：城市名不能为空或格式错误"
            }

        if not self.api_key:
            st.warning("未配置AMAP_API_KEY环境变量，天气查询功能不可用！")
            return {
                "success": False,
                "observation": "查询失败：未配置AMAP_API_KEY环境变量"
            }

        # 第一步：获取城市行政编码（精准定位）
        adcode = self._get_city_adcode(city)
        if not adcode:
            return {
                "success": False,
                "observation": f"查询失败：未找到[{city}]的行政编码，请确认城市名正确"
            }

        # 第二步：调用高德实时天气API
        try:
            params = {
                "key": self.api_key,
                "city": adcode,
                "extensions": "base",  # base=实时天气，all=实时+预报
                "output": "json"
            }

            response = requests.get(
                AMAP_WEATHER_URL,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            if data["status"] != "1" or len(data["lives"]) == 0:
                return {
                    "success": False,
                    "observation": f"查询失败：未获取到[{city}]的有效天气数据"
                }

            # 解析高德返回的实时天气（国内精准数据）
            live_weather = data["lives"][0]
            return {
                "success": True,
                "observation": {
                    "city": live_weather["city"],
                    "temperature": live_weather["temperature"],  # 实时温度（国内站点数据）
                    "weather": live_weather["weather"],          # 天气状况（晴/阴/小雨等）
                    "humidity": live_weather["humidity"],        # 湿度
                    "winddirection": live_weather["winddirection"],  # 风向
                    "windpower": live_weather["windpower"],      # 风力
                    "reporttime": live_weather["reporttime"]     # 数据更新时间（精准到分钟）
                }
            }

        except requests.exceptions.Timeout:
            return {"success": False, "observation": f"查询失败：连接高德API超时（{city}）"}
        except requests.exceptions.HTTPError as e:
            return {"success": False, "observation": f"查询失败：HTTP错误 {e.response.status_code}（{city}）"}
        except Exception as e:
            return {"success": False, "observation": f"查询失败：{str(e)}（{city}）"}

# ------------------------------
# Agent核心类（新增记忆系统，核心修改2）
# ------------------------------
class LangChainOllamaAgent:
    def __init__(self, model_name: str = DEFAULT_MODEL):
        try:
            self.llm = ChatOllama(
                base_url=OLLAMA_BASE_URL,
                model=model_name,
                timeout=30
            )
            st.success(f"✅ 成功连接Ollama模型：{model_name}")
        except Exception as e:
            st.error(f"❌ 连接Ollama模型失败：{str(e)}")
            raise RuntimeError(f"Ollama模型初始化失败：{str(e)}")

        self.weather_tool = WeatherTool()
        self.tools = {
            "weather": {
                "name": "weather",
                "description": "查询指定城市的实时天气信息，需要传入中文城市名（如北京、上海、广州）",
                "function": self.weather_tool.run
            }
        }

        # ------------------------------
        # 新增：初始化对话记忆（核心）
        # ------------------------------
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",  # 记忆在Prompt中对应的变量名
            return_messages=True        # 返回Message对象，兼容ChatPromptTemplate
        )

        # 新增：构造带“上下文历史”的Prompt模板
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个智能天气助手，规则如下：
                1. 必须结合聊天历史理解用户的上下文需求；
                2. 天气相关问题（含天气/气温/温度等关键词），优先调用天气工具获取精准数据后回答；
                3. 非天气问题直接用简洁、自然的中文回答，保持对话连贯；
                4. 回答时不提“工具”“API”“编码”等技术词汇，只说用户能懂的内容。"""),
            ("human", "聊天历史：{chat_history}\n当前问题：{input}")
        ])

        # 新增：初始化“带记忆的对话Chain”
        self.conversation_chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            memory=self.memory,  # 绑定记忆组件，自动管理上下文
            verbose=False        # 调试时可改为True，查看上下文传递过程
        )

    def _extract_city_name(self, text: str) -> Optional[str]:
        """优化：从完整上下文（历史+当前输入）中提取城市名，扩展城市列表"""
        text = text.replace("工具调用", "").replace("：", "").replace(":", "").strip()
        # 扩展城市列表（可根据需求继续添加）
        city_keywords = [
            "北京", "上海", "广州", "深圳", "成都", "重庆", "杭州",
            "南京", "武汉", "西安", "平顶山", "郑州", "长沙", "青岛",
            "苏州", "天津", "合肥", "厦门", "宁波", "昆明", "贵阳"
        ]
        for city in city_keywords:
            if city in text:
                return city
        return None

    def chat(self, user_input: str) -> str:
        """核心对话逻辑（新增上下文记忆，核心修改3）"""
        try:
            # 步骤1：从“历史+当前输入”的完整上下文提取城市名（支持上下文联想）
            chat_history = self.memory.load_memory_variables({})["chat_history"]
            full_context = f"{chat_history}\n{user_input}"  # 整合历史+当前输入
            city = self._extract_city_name(full_context)

            # 步骤2：智能判断是否需要调用天气工具（支持上下文，比如先问“平顶山天气”，再问“多少度”）
            weather_keywords = ["天气", "气温", "温度", "下雨", "晴天", "湿度", "风速", "风力", "多少度"]
            is_weather_question = any(keyword in user_input for keyword in weather_keywords)

            # 天气问题+能提取到城市 → 调用工具
            if is_weather_question and city:
                tool_result = self.tools["weather"]["function"](city=city)
                if tool_result["success"]:
                    # 构造带天气数据的提示，让模型生成自然回答
                    weather_data = tool_result["observation"]
                    tool_prompt = f"""
                    {weather_data['city']}实时天气（{weather_data['reporttime']}更新）：
                    温度：{weather_data['temperature']}℃
                    天气：{weather_data['weather']}
                    湿度：{weather_data['humidity']}%
                    风向：{weather_data['winddirection']}
                    风力：{weather_data['windpower']}级

                    结合之前的聊天历史，用自然、友好的语言回答用户当前问题：{user_input}
                    要求：1. 突出核心信息（温度+天气）；2. 不提及工具/API/编码等技术词汇；3. 保持语气连贯。
                    """
                    # 调用模型生成回答，并手动更新记忆
                    response = self.llm.invoke([HumanMessage(content=tool_prompt)])
                    answer = response.content.strip() if response.content else f"抱歉，未获取到{city}的天气回答"
                    # 保存当前对话到记忆（让后续对话能关联）
                    self.memory.save_context({"input": user_input}, {"output": answer})
                    return answer
                else:
                    # 工具调用失败的友好提示，同时保存记忆
                    error_msg = f"😥 抱歉，查询{city}天气失败：{tool_result['observation']}"
                    self.memory.save_context({"input": user_input}, {"output": error_msg})
                    return error_msg
            else:
                # 非天气问题：用带记忆的Chain自动结合历史上下文生成回答
                answer = self.conversation_chain.run(input=user_input)
                return answer if answer else "抱歉，我没理解你的问题，请换个说法试试～"
        except Exception as e:
            st.error(f"对话处理出错：{str(e)}")
            error_msg = f"⚠️ 对话出错：{str(e)}"
            # 出错时也保存记忆，避免上下文断裂
            self.memory.save_context({"input": user_input}, {"output": error_msg})
            return error_msg

# ------------------------------
# Streamlit界面交互逻辑
# ------------------------------
def main():
    # 页面标题和说明（更新记忆功能说明）
    st.title("🌤️ 智能天气助手")
    st.markdown("""
    ### 基于Ollama + 高德天气API构建
    - 支持**国内城市实时天气查询**（数据精准，分钟级更新）
    - 支持**上下文连贯对话**（比如先问“重庆天气”，再问“多少度”可识别）
    - 支持**通用对话**（如：什么是大语言模型？）
    - 输入 `exit`/`退出` 可清空对话记录
    """)
    st.divider()

    # 初始化会话状态
    if "agent" not in st.session_state:
        try:
            st.session_state.agent = LangChainOllamaAgent()
        except RuntimeError:
            st.session_state.agent = None

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "你好！我是智能天气助手（带记忆版），请问你想查询哪个城市的天气，或者有其他问题想要问我？"}
        ]

    # 渲染聊天记录
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 聊天输入框
    prompt = st.chat_input("请输入你的问题（如：重庆今天天气怎么样？）")

    if prompt:
        if prompt.lower() in ["exit", "quit", "退出"]:
            st.session_state.messages = [
                {"role": "assistant", "content": "你好！我是智能天气助手（带记忆版），请问你想查询哪个城市的天气，或者有其他问题想要问我？"}
            ]
            # 清空Agent的记忆（关键：退出时重置记忆）
            if st.session_state.agent:
                st.session_state.agent.memory.clear()
            st.rerun()

        if not prompt.strip():
            st.warning("请输入有效的问题！")
            return

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        if st.session_state.agent:
            with st.chat_message("assistant"):
                with st.spinner("思考中..."):
                    response = st.session_state.agent.chat(prompt)
                    st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            st.error("Agent初始化失败，请检查Ollama服务是否运行！")

if __name__ == "__main__":
    main()