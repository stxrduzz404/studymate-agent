import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="StudyMate Agent", page_icon="📘", layout="centered")

st.title("📘 StudyMate Agent")
st.write("AI 學習摘要與測驗生成系統")

st.sidebar.title("專案說明")
st.sidebar.write("本系統可以協助學生將課程內容整理成摘要，並自動產生測驗題，方便複習與自我檢測。")
st.sidebar.write("功能包含：")
st.sidebar.write("1. 課程摘要生成")
st.sidebar.write("2. 測驗題生成")
st.sidebar.write("3. 題目難度選擇")
st.sidebar.write("4. 答案與解析")

if "course_text" not in st.session_state:
    st.session_state.course_text = ""

if "summary_result" not in st.session_state:
    st.session_state.summary_result = ""

if "quiz_result" not in st.session_state:
    st.session_state.quiz_result = ""

def clear_all():
    st.session_state.course_text = ""
    st.session_state.summary_result = ""
    st.session_state.quiz_result = ""

if not api_key:
    st.error("找不到 GEMINI_API_KEY，請檢查 .env 檔案")
    st.stop()

client = genai.Client(api_key=api_key)

user_input = st.text_area(
    "請貼上課程內容：",
    height=250,
    key="course_text"
)

setting_col1, setting_col2 = st.columns(2)

with setting_col1:
    question_count = st.selectbox(
        "測驗題數量",
        [3, 5, 10],
        index=1
    )

with setting_col2:
    difficulty = st.selectbox(
        "測驗難度",
        ["簡單", "中等", "困難"],
        index=1
    )

col1, col2, col3, col4 = st.columns(4)

with col1:
    summary_button = st.button("產生摘要")

with col2:
    quiz_button = st.button("產生測驗題")

with col3:
    all_button = st.button("全部產生")

with col4:
    clear_button = st.button("清除內容", on_click=clear_all)

def generate_summary(text):
    prompt = f"""
    你是一位學習助教。
    請根據以下課程內容，整理成適合學生複習的摘要。
    請使用繁體中文，語氣清楚簡潔。

    請輸出以下格式：

    ## 一、重點整理
    - 
    - 
    - 

    ## 二、關鍵名詞
    - 名詞：解釋
    - 名詞：解釋

    ## 三、學習建議
    - 
    - 
    - 

    ## 四、考試可能重點
    - 
    - 
    - 

    課程內容：
    {text}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text

def generate_quiz(text, count, level):
    prompt = f"""
    你是一位學習測驗出題助教。
    請根據以下課程內容，產生 {count} 題選擇題。
    題目難度請設定為：{level}。
    請使用繁體中文。

    每一題請包含：
    1. 題目
    2. A、B、C、D 四個選項
    3. 正確答案
    4. 簡短解析

    如果難度是簡單，請偏向基本概念。
    如果難度是中等，請加入理解與比較。
    如果難度是困難，請加入應用、推論或觀念整合。

    請輸出以下格式：

    ## 第 1 題
    題目：
    A.
    B.
    C.
    D.
    正確答案：
    解析：

    課程內容：
    {text}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text

if summary_button:
    if user_input.strip() == "":
        st.warning("請先貼上課程內容")
    else:
        with st.spinner("AI 正在生成摘要..."):
            st.session_state.summary_result = generate_summary(user_input)

if quiz_button:
    if user_input.strip() == "":
        st.warning("請先貼上課程內容")
    else:
        with st.spinner("AI 正在生成測驗題..."):
            st.session_state.quiz_result = generate_quiz(user_input, question_count, difficulty)

if all_button:
    if user_input.strip() == "":
        st.warning("請先貼上課程內容")
    else:
        with st.spinner("AI 正在生成摘要與測驗題..."):
            st.session_state.summary_result = generate_summary(user_input)
            st.session_state.quiz_result = generate_quiz(user_input, question_count, difficulty)

if st.session_state.summary_result:
    st.divider()
    st.subheader("AI 摘要結果")
    st.markdown(st.session_state.summary_result)

if st.session_state.quiz_result:
    st.divider()
    st.subheader("AI 測驗題結果")
    st.markdown(st.session_state.quiz_result)