import os
import logging
import requests
import streamlit as st
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory

# ------------------------------
# 基础配置
# ------------------------------
load_dotenv()
AMAP_API_KEY = os.getenv("AMAP_API_KEY")

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "deepseek-r1:1.5b"
AMAP_WEATHER_URL = "https://restapi.amap.com/v3/weather/weatherInfo"

st.set_page_config(
    page_title="智能天气助手",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------------------
# 高德天气工具（不变）
# ------------------------------
class WeatherTool:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or AMAP_API_KEY

    def _get_city_adcode(self, city: str) -> Optional[str]:
        if not self.api_key:
            return None
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
                return data["geocodes"][0]["adcode"]
        except Exception as e:
            st.error(f"获取城市编码失败：{str(e)}")
        return None

    def _validate_input(self, city: str) -> bool:
        if not isinstance(city, str) or len(city.strip()) == 0:
            st.error("城市名不能为空或格式错误")
            return False
        return True

    def run(self, city: str) -> Dict[str, Any]:
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

        adcode = self._get_city_adcode(city)
        if not adcode:
            return {
                "success": False,
                "observation": f"查询失败：未找到[{city}]的行政编码，请确认城市名正确"
            }

        try:
            params = {
                "key": self.api_key,
                "city": adcode,
                "extensions": "base",
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

            live_weather = data["lives"][0]
            return {
                "success": True,
                "observation": {
                    "city": live_weather["city"],
                    "temperature": live_weather["temperature"],
                    "weather": live_weather["weather"],
                    "humidity": live_weather["humidity"],
                    "winddirection": live_weather["winddirection"],
                    "windpower": live_weather["windpower"],
                    "reporttime": live_weather["reporttime"]
                }
            }

        except requests.exceptions.Timeout:
            return {"success": False, "observation": f"查询失败：连接高德API超时（{city}）"}
        except requests.exceptions.HTTPError as e:
            return {"success": False, "observation": f"查询失败：HTTP错误 {e.response.status_code}（{city}）"}
        except Exception as e:
            return {"success": False, "observation": f"查询失败：{str(e)}（{city}）"}

# ------------------------------
# ✅ 新版 LangChain 记忆 + 对话（全部重写为最新版）
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
        self.city_list = [
            "北京", "上海", "广州", "深圳", "成都", "重庆", "杭州",
            "南京", "武汉", "西安", "平顶山", "郑州", "长沙", "青岛",
            "苏州", "天津", "合肥", "厦门", "宁波", "昆明", "贵阳"
        ]

        # ------------------------------
        # 最新版 LangChain 对话记忆（官方推荐）
        # ------------------------------
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个智能聊天助手，规则如下：
                1. 必须结合聊天历史理解用户的上下文需求；
                2. 天气相关问题，优先调用天气工具获取精准数据后回答；
                3. 非天气问题直接用简洁、自然的中文回答，保持对话连贯；
                4. 回答时不提“工具”“API”“编码”等技术词汇，只说用户能懂的内容。"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])

        # 新版 Chain
        self.chain = self.prompt | self.llm | StrOutputParser()

        # 新版记忆管理
        self.chat_history = []

    def _extract_city(self, text: str) -> Optional[str]:
        for city in self.city_list:
            if city in text:
                return city
        return None

    def chat(self, user_input: str) -> str:
        try:
            # 提取城市
            city = self._extract_city(user_input)
            weather_words = ["天气","气温","温度","下雨","晴天","湿度","风速","风力","多少度"]
            need_weather = any(w in user_input for w in weather_words)

            if need_weather and city:
                res = self.weather_tool.run(city)
                if res["success"]:
                    data = res["observation"]
                    answer = (
                        f"{data['city']} 当前天气（{data['reporttime']}）\n\n"
                        f"🌡 温度：{data['temperature']}℃\n"
                        f"☁ 天气：{data['weather']}\n"
                        f"💧 湿度：{data['humidity']}%\n"
                        f"💨 风向：{data['winddirection']} {data['windpower']}级"
                    )
                else:
                    answer = f"😥 {res['observation']}"

                self.chat_history.append(HumanMessage(content=user_input))
                self.chat_history.append(SystemMessage(content=answer))
                return answer

            # 正常对话
            response = self.chain.invoke({
                "chat_history": self.chat_history,
                "input": user_input
            })

            self.chat_history.append(HumanMessage(content=user_input))
            self.chat_history.append(SystemMessage(content=response))
            return response

        except Exception as e:
            st.error(f"错误：{str(e)}")
            return f"⚠️ 出错了：{str(e)}"

# ------------------------------
# 主界面（不变）
# ------------------------------
def main():
    st.title("🌤️ 智能天气助手")
    st.markdown("""
    ### 基于 Ollama + 高德天气API + 最新 LangChain
    - 支持国内城市实时天气
    - 支持上下文记忆对话
    - 输入 `exit`/`退出` 清空对话
    """)
    st.divider()

    if "agent" not in st.session_state:
        try:
            st.session_state.agent = LangChainOllamaAgent()
        except RuntimeError:
            st.session_state.agent = None

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "你好！我是智能天气助手，请问你想查询哪个城市的天气？"}
        ]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("请输入你的问题（如：重庆今天天气怎么样？）")

    if prompt:
        if prompt.lower() in ["exit", "quit", "退出"]:
            st.session_state.messages = [{"role": "assistant", "content": "你好！我是智能天气助手，请问你想查询哪个城市的天气？"}]
            if st.session_state.agent:
                st.session_state.agent.chat_history = []
            st.rerun()

        if not prompt.strip():
            st.warning("请输入有效内容！")
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
            st.error("Agent 初始化失败，请检查 Ollama 是否启动！")

if __name__ == "__main__":
    main()