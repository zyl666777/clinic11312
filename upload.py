import os
import streamlit as st
import pandas as pd

# 設定檔案保存的資料夾
UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # 如果資料夾不存在，則創建

st.title("後台檔案更新系統")

# 上傳檔案區域
uploaded_file = st.file_uploader("請上傳檔案", type=["csv", "xlsx", "txt"])

if uploaded_file is not None:
    # 檢視檔案內容
    st.write("**上傳的檔案名稱：**", uploaded_file.name)

    # 讀取檔案內容
    try:
        if uploaded_file.name.endswith(".csv"):
            data = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            data = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith(".txt"):
            data = uploaded_file.read().decode("utf-8").splitlines()
            st.write("**檔案內容：**")
            st.write("\n".join(data))
        else:
            st.warning("不支援的檔案格式")
            data = None

        # 顯示數據
        if isinstance(data, pd.DataFrame):
            st.dataframe(data)

        # 儲存檔案
        with open(os.path.join(UPLOAD_FOLDER, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"檔案已成功上傳並保存到 {UPLOAD_FOLDER} 資料夾！")

    except Exception as e:
        st.error(f"檔案處理失敗：{e}")
else:
    st.info("請上傳檔案以檢視和更新。")
