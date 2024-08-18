import streamlit as st
import os
from PIL import Image
import io
import numpy as np
import matplotlib.pyplot as plt
import pickle
os.environ['CUDA_VISIBLE_DEVICES'] = ''

import paddle
paddle.device.set_device('cpu')

from paddleocr import PaddleOCR

st.title("訓練文字標註")
# 初始化 PaddleOCR
@st.cache_resource
def load_ocr():
    return PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=False)

ocr = load_ocr()

def extract_text_regions(image):
    result = ocr.ocr(image)
    text_regions = [line[0] for line in result[0]]
    return text_regions


def crop_text_regions(bytes_data, regions):
    image = Image.open(io.BytesIO(bytes_data))
    cropped_images = []
    for box in regions:
        points = np.array(box).astype(np.int32).reshape((-1, 2))
        left = min(points[:, 0])
        top = min(points[:, 1])
        right = max(points[:, 0])
        bottom = max(points[:, 1])
        cropped = image.crop((left, top, right, bottom))
        cropped_images.append(cropped)
    return cropped_images


uploaded_file = st.file_uploader("上傳證件圖片", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    # 使用 PIL 打開圖片
    uploaded_file = Image.open(io.BytesIO(bytes_data))
    image=uploaded_file
    st.image(image, caption='上傳的圖片', use_column_width=True)
    img_array = np.array(image)
    text_regions=extract_text_regions(img_array)
    result=ocr.ocr(img_array)
    cropped_texts = crop_text_regions(bytes_data, text_regions)

    text_info = [(region, text) for region, (text, confidence) in result[0]]

    st.subheader("標註文件提取")

    # 打開完整圖片
    full_image = Image.open(io.BytesIO(bytes_data))
    # st.image(full_image, caption="完整圖片", use_column_width=True)

    # 初始化 session state
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
        st.session_state.corrected_data = []


    # 顯示當前區域的圖片和文字輸入
    if st.session_state.current_index < len(text_info):
        region, ocr_text = text_info[st.session_state.current_index]
        points = np.array(region).astype(np.int32).reshape((-1, 2))
        left, top = np.min(points, axis=0)
        right, bottom = np.max(points, axis=0)
        cropped = full_image.crop((left, top, right, bottom))

        # 使用 matplotlib 繪製圖片
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.imshow(cropped)
        ax.axis('off')
        
        # 將 matplotlib 圖形轉換為 Streamlit 可顯示的格式
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        st.image(buf, caption=f"區域 {st.session_state.current_index + 1}")

        # 文字輸入
        correct_text = st.text_input(f"請輸入正確的文字 (或按 Enter 保留 '{ocr_text}')", value=ocr_text)

        if st.button("下一個"):
            st.session_state.corrected_data.append((region, correct_text))
            st.session_state.current_index += 1
            st.rerun()

    else:
        st.write("所有區域已處理完畢")
        #st.write("校正後的數據：", st.session_state.corrected_data)

    # 顯示進度
    st.progress(st.session_state.current_index / len(text_info))

    ## training_set_cnn
    if st.session_state.current_index >= len(text_info):
        st.write("所有區域已處理完畢")
        
        # 創建訓練數據
        training_data = []
        for i, (region, correct_text) in enumerate(st.session_state.corrected_data):
            # 從原始圖片中裁剪出對應區域
            points = np.array(region).astype(np.int32).reshape((-1, 2))
            left, top = np.min(points, axis=0)
            right, bottom = np.max(points, axis=0)
            cropped = full_image.crop((left, top, right, bottom))
            
            # 將裁剪後的圖片和校正後的文字添加到訓練數據中
            training_data.append((cropped, correct_text))
        
        st.write(f"已生成 {len(training_data)} 條訓練數據")
        
        # 可以選擇將訓練數據保存到文件中
        if st.button("保存訓練數據"):
            save_dir = "training_data"
            os.makedirs(save_dir, exist_ok=True)
            for i, (image, label) in enumerate(training_data):
                image_path = os.path.join(save_dir, f"image_{i}.png")
                label_path = os.path.join(save_dir, f"label_{i}.txt")
                
                image.save(image_path)
                with open(label_path, 'w', encoding='utf-8') as f:
                    f.write(label)
            
            st.write(f"訓練數據已保存到 {save_dir} 目錄")