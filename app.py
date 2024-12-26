import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# 設定頁面配置
st.set_page_config(page_title="台灣健保醫事機構互動地圖", layout="wide")

# 加載資料
@st.cache_data
def load_data():
    data = pd.read_csv('C:\\Users\\User\\Documents\\GitHub\\clinic11312\\健保特約醫事機構診所.csv')
    data.columns = data.columns.str.strip()  # 去除多餘空格
    data["縣市"] = data["地址"].str.extract(r'([\u4e00-\u9fa5]{2,3}[市縣])')[0].fillna("未知")
    data["緯度"] = pd.to_numeric(data["緯度"], errors="coerce")
    data["經度"] = pd.to_numeric(data["經度"], errors="coerce")
    return data

data = load_data()

# 設定標題與介紹
st.title("台灣健保醫事機構互動地圖")
st.write("透過此系統，您可以查詢台灣各地的健保特約醫事機構分佈，並根據需求篩選或查看詳細資訊。")

# 篩選功能
city_options = ["全部"] + list(data["縣市"].unique())
selected_city = st.selectbox("選擇縣市", city_options)

type_options = ["全部"] + data["醫事機構種類"].dropna().unique().tolist()
selected_type = st.selectbox("選擇醫事機構種類", type_options)

# 根據篩選條件過濾資料
filtered_data = data.copy()
if selected_city != "全部":
    filtered_data = filtered_data[filtered_data["縣市"] == selected_city]

if selected_type != "全部":
    filtered_data = filtered_data[filtered_data["醫事機構種類"] == selected_type]

# 地圖顯示
st.subheader("互動地圖")
m = folium.Map(location=[23.6978, 120.9605], zoom_start=8)

# 將醫事機構數據添加到地圖
for _, row in filtered_data.iterrows():
    if pd.notna(row["緯度"]) and pd.notna(row["經度"]):  # 確保經緯度非空
        folium.Marker(
            location=[row["緯度"], row["經度"]],
            popup=f"""
            <strong>醫事機構名稱:</strong> {row['醫事機構名稱']}<br>
            <strong>種類:</strong> {row['醫事機構種類']}<br>
            <strong>電話:</strong> {row['電話']}<br>
            <strong>地址:</strong> {row['地址']}<br>
            <strong>診療科別:</strong> {row['診療科別']}<br>
            <strong>服務項目:</strong> {row['服務項目']}
            """,
            icon=folium.Icon(color="blue" if row["醫事機構種類"] == "診所" else "green")
        ).add_to(m)

# 顯示地圖
folium_static(m)

# 顯示醫事機構清單
st.subheader("醫事機構清單")
st.dataframe(filtered_data)
