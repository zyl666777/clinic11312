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
st.write("透過此系統，您可以查詢台灣各地的健保特約醫事機構分佈，並自動顯示最近診所的位置。")

# 添加獲取用戶位置的 JavaScript 腳本
location_script = """
<script>
navigator.geolocation.getCurrentPosition(
    (position) => {
        const latitude = position.coords.latitude;
        const longitude = position.coords.longitude;
        const inputLat = document.getElementById("latitude");
        const inputLon = document.getElementById("longitude");
        inputLat.value = latitude;
        inputLon.value = longitude;
        document.getElementById("location-form").submit();
    },
    (error) => {
        console.error(error);
        alert("無法獲取您的位置，請確保已啟用位置權限。");
    }
);
</script>
"""

# 自動執行地理位置腳本
st.components.v1.html(
    f"""
    <div>
        <form id="location-form">
            <input type="hidden" id="latitude" name="latitude" />
            <input type="hidden" id="longitude" name="longitude" />
        </form>
        {location_script}
    </div>
    """,
    height=0,
)

# 用戶經緯度輸入處理
latitude = st.experimental_get_query_params().get('latitude', [None])[0]
longitude = st.experimental_get_query_params().get('longitude', [None])[0]

if latitude and longitude:
    user_location = (float(latitude), float(longitude))
    
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
else:
    st.write("正在嘗試獲取您的位置...")

# 顯示醫事機構清單
st.subheader("醫事機構清單")
st.dataframe(data)
