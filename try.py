import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from geopy.distance import geodesic

# 設定頁面配置
st.set_page_config(page_title="台灣健保醫事機構互動地圖", layout="wide")

# 加載資料
@st.cache_data
def load_data():
    data = pd.read_csv('健保特約醫事機構診所.csv')
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

# 用戶位置和最近診所
st.subheader("查找最近的健保特約診所")
st.write("請允許瀏覽器訪問您的位置信息以顯示最近診所。")

# HTML 元件獲取用戶位置
location_script = """
<script>
navigator.geolocation.getCurrentPosition(
    (position) => {
        const coords = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
        };
        document.getElementById("latitude").value = coords.latitude;
        document.getElementById("longitude").value = coords.longitude;
    },
    (error) => {
        console.error(error);
        alert("無法獲取您的位置，請確保已啟用位置權限。");
    }
);
</script>
"""

st.components.v1.html(f"""
    <div>
        <button onclick="navigator.geolocation.getCurrentPosition(position => {{
            document.getElementById('latitude').value = position.coords.latitude;
            document.getElementById('longitude').value = position.coords.longitude;
        }})">獲取位置</button>
        <form>
            <input type="text" id="latitude" name="latitude" placeholder="緯度" />
            <input type="text" id="longitude" name="longitude" placeholder="經度" />
        </form>
    </div>
    {location_script}
""", height=200)

# 用戶輸入經緯度
user_lat = st.text_input("緯度", "")
user_lon = st.text_input("經度", "")

if user_lat and user_lon:
    user_location = (float(user_lat), float(user_lon))
    
    # 計算每個診所到用戶的距離
    def calculate_distance(row):
        clinic_location = (row['緯度'], row['經度'])
        return geodesic(user_location, clinic_location).kilometers

    data['距離'] = data.apply(calculate_distance, axis=1)

    # 找出最近的診所
    nearest_clinic = data.loc[data['距離'].idxmin()]
    st.write(f"最近的診所是：{nearest_clinic['醫事機構名稱']}，距離：{nearest_clinic['距離']:.2f} 公里")

    # 顯示用戶位置和最近診所的地圖
    m_nearest = folium.Map(location=user_location, zoom_start=14)
    folium.Marker(location=user_location, popup="您的位置", icon=folium.Icon(color="red")).add_to(m_nearest)
    folium.Marker(location=[nearest_clinic['緯度'], nearest_clinic['經度']],
                  popup=nearest_clinic['醫事機構名稱'], icon=folium.Icon(color="blue")).add_to(m_nearest)

    folium_static(m_nearest)
