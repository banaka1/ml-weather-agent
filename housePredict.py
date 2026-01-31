import pandas as pd
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import streamlit as st

# 初始化Ollama
ollama = ChatOllama(base_url='http://localhost:11434', model="deepseek-r1:1.5b")

def abc():
    st.markdown("我是小白快来和我聊天吧")
    prompt = st.chat_input("Enter your question here")

    # 初始化会话状态（存消息对象）
    if 'message_history' not in st.session_state:
        # 初始消息包含SystemMessage（只需要加一次）
        st.session_state.message_history = [
            SystemMessage(
                content="你的身份是情感小助手，名字叫小白。你需要以小白的身份与用户交流，提供情感支持或者聊天，不要提及自己是DeepSeek-R1或任何开发相关信息，只说自己是情感助手小白。")
        ]

    if prompt:
        # 1. 把用户的prompt加入消息历史（HumanMessage）
        st.session_state.message_history.append(HumanMessage(content=prompt))

        # 2. 调用模型（传入完整的消息历史）
        # 新版本中invoke返回的是BaseMessage对象，直接取content即可
        response = ollama.invoke(st.session_state.message_history)

        # 3. 把模型回复加入消息历史（AIMessage）
        st.session_state.message_history.append(AIMessage(content=response.content))

        # 4. 渲染聊天记录（遍历message_history，跳过初始的SystemMessage）
        for msg in st.session_state.message_history[1:]:  # 从第1个开始，跳过SystemMessage
            if isinstance(msg, HumanMessage):
                with st.chat_message("user"):
                    st.write(f"我 ：{msg.content}")
            elif isinstance(msg, AIMessage):
                with st.chat_message("assistant"):
                    # 移除了多余的字符串分割（新版本返回的content是纯文本）
                    st.write(f"小白 ：{msg.content}")

abc()