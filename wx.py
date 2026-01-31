from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import streamlit as st

ollama = ChatOllama(base_url='http://localhost:11434', model="deepseek-r1:1.5b")