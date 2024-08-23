import streamlit as st
import os
from paddleocr import PaddleOCR
from PIL import Image
import openai
import io
import requests
import json
import numpy as np
# 設置頁面配置
st.set_page_config(page_title="證件文字提取", layout="wide")

# 設置 OpenAI API key（請替換為你的 API key）
with st.sidebar:
    OPENAI_API_KEY = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
os.environ['CUDA_VISIBLE_DEVICES'] = ''


import paddle
paddle.device.set_device('cpu')


# 初始化 PaddleOCR
@st.cache_resource
def load_ocr():
    return PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=False)

ocr = load_ocr()

def extract_text(image):
    result = ocr.ocr(image)
    extracted_text = '\n'.join([line[1][0] for line in result[0]])
    return extracted_text

def get_completion(messages, model="gpt-4", temperature=0, max_tokens=300, seed=None):
        payload = { "model": model, "temperature": temperature, "messages": messages, "max_tokens": max_tokens }
        if seed:
            payload["seed"] = seed
        headers = { "Authorization": f'Bearer {OPENAI_API_KEY}', "Content-Type": "application/json" }
        response = requests.post('https://api.openai.com/v1/chat/completions', headers = headers, data = json.dumps(payload) )
        obj = json.loads(response.text)
        if response.status_code == 200 :
            return obj["choices"][0]["message"]["content"]
        else :
            return obj["error"]



st.title("證件文字提取")

uploaded_file = st.file_uploader("上傳證件圖片", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    # 使用 PIL 打開圖片
    uploaded_file = Image.open(io.BytesIO(bytes_data))
    image=uploaded_file
    st.image(image, caption='上傳的圖片', use_column_width=True)
    
    if st.button('提取並格式化文字'):
        with st.spinner('正在處理圖片...'):
            # 提取文字
            img_array = np.array(image)
            extracted_text = extract_text(img_array)
            #st.subheader("提取的原始文字：")
            #st.text(extracted_text)

            if "姓名" in extracted_text:
                st.write("身份證正面")
                system_message = "你是一個專門處理證件資訊的助手。現在你讀取的是身份證正面，請將提供的文字整理成一個結構化的格式，格式包括姓名、出生年月日、性別、身份證件號、發證日期這些關鍵信息，請以繁體中文回覆。" 
            elif "通知" in extracted_text:
                st.write("帳單")
                system_message = "你是一個專門處理帳單資訊的助手。請按照你讀取到的文字，整理成可以理解的帳單資訊，並以結構化的方式輸出，請以繁體中文回覆。"
            else :
                st.write("身份證反面")
                system_message = "你是一個專門處理證件資訊的助手。現在你讀取的是身份證反面，請將提供的文字整理成一個結構化的格式，格式包括父親姓名、母親姓名、配偶姓名、兵役別、出生地、住址這些關鍵信息，請以繁體中文回覆。"
            
            
            #使用 GPT 生成格式化文字
            
            messages = [
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": f"請將以下文字整理成結構化格式：\n\n{extracted_text}"
                }]

            response = get_completion(messages, temperature=0)
            st.subheader("格式化後的文字：")
            st.text(response)
            
            # # 提供下載選項
            st.download_button(
                label="下載格式化文字",
                data=response,
                file_name="formatted_text.txt",
                mime="text/plain"
            )

st.sidebar.title("導航")
st.sidebar.info("選擇上方的頁面來切換不同功能。")
