import streamlit as st
import pandas as pd
from plotly import express as px
import json
from collections import defaultdict
import numpy as np

# 設置頁面配置
st.set_page_config(
    page_title="健保診所分佈儀表板",
    page_icon="🏥",
    layout="wide"
)

# 定義台灣縣市和區域的映射
DISTRICTS = {
    "臺北市": ["中正區", "大同區", "中山區", "松山區", "大安區", "萬華區", "信義區", "士林區", "北投區", "內湖區", "南港區", "文山區"],
    "新北市": ["板橋區", "三重區", "中和區", "永和區", "新莊區", "新店區", "土城區", "樹林區", "鶯歌區", "三峽區", "淡水區", "汐止區", "瑞芳區", "五股區", "蘆洲區", "泰山區", "林口區", "八里區", "三芝區", "石門區", "坪林區", "平溪區", "雙溪區"],
    # ... (其他縣市區域映射，為了簡潔省略，實際使用時需要完整列出)
}

# 固定縣市顯示順序
CITY_ORDER = [
    "臺北市", "新北市", "基隆市", "桃園市", "新竹市", "新竹縣", "苗栗縣",
    "臺中市", "彰化縣", "南投縣", "雲林縣", "嘉義市", "嘉義縣",
    "臺南市", "高雄市", "屏東縣", "臺東縣", "花蓮縣", "宜蘭縣",
    "澎湖縣", "金門縣", "連江縣"
]

# 初始化 session state
if 'favorite_clinics' not in st.session_state:
    st.session_state.favorite_clinics = set()

def load_data():
    """載入診所資料"""
    try:
        df = pd.read_csv('健保特約醫事機構診所.csv')
        return process_data(df)
    except Exception as e:
        st.error(f"無法載入資料：{str(e)}")
        return pd.DataFrame()

def process_data(df):
    """處理診所資料"""
    # 判斷診所類型
    conditions = [
        df['醫事機構名稱'].str.contains('醫院', na=False),
        df['醫事機構名稱'].str.contains('診所', na=False),
        df['醫事機構名稱'].str.contains('衛生所', na=False)
    ]
    choices = ['醫院', '診所', '衛生所']
    df['診所類型'] = np.select(conditions, choices, default='其他')
    
    # 從地址提取縣市和區域
    df['縣市'] = df['地址'].str.extract(r'^([\u4e00-\u9fa5]{2,3}(?:市|縣))')
    df['區域'] = df['地址'].str.extract(r'(?:市|縣)([\u4e00-\u9fa5]+?[區鎮鄉市])')
    
    return df

def create_city_chart(df):
    """建立縣市分布圖表"""
    city_counts = df['縣市'].value_counts().reindex(CITY_ORDER).fillna(0)
    fig = px.bar(
        x=city_counts.index,
        y=city_counts.values,
        title='各縣市診所數量分布',
        labels={'x': '縣市', 'y': '診所數量'},
        color=city_counts.values,
        color_continuous_scale='Blues'
    )
    fig.update_layout(
        showlegend=False,
        height=500,
        xaxis_tickangle=45
    )
    return fig

def main():
    # 標題和說明
    st.title('健保診所分佈儀表板')
    st.markdown('透過本系統，您可以查詢健保特約診所在各縣市及區域的分佈情況。')
    
    # 載入資料
    df = load_data()
    
    if df.empty:
        st.warning('無法載入資料，請確認資料檔案是否存在。')
        return
    
    # 建立側邊欄篩選器
    st.sidebar.header('搜尋條件')
    
    # 縣市選擇
    selected_city = st.sidebar.selectbox(
        '選擇縣市',
        ['全部'] + CITY_ORDER
    )
    
    # 區域選擇
    districts = DISTRICTS.get(selected_city, []) if selected_city != '全部' else []
    selected_district = st.sidebar.selectbox(
        '選擇區域',
        ['全部'] + districts
    )
    
    # 診所類型選擇
    selected_type = st.sidebar.selectbox(
        '選擇診所類型',
        ['全部', '醫院', '診所', '衛生所']
    )
    
    # 關鍵字搜尋
    search_keyword = st.sidebar.text_input('搜尋診所名稱/地址/電話')
    
    # 資料篩選
    filtered_df = df.copy()
    if selected_city != '全部':
        filtered_df = filtered_df[filtered_df['縣市'] == selected_city]
    if selected_district != '全部':
        filtered_df = filtered_df[filtered_df['區域'].str.contains(selected_district, na=False)]
    if selected_type != '全部':
        filtered_df = filtered_df[filtered_df['診所類型'] == selected_type]
    if search_keyword:
        search_condition = filtered_df.apply(
            lambda x: any(str(search_keyword).lower() in str(v).lower() for v in x),
            axis=1
        )
        filtered_df = filtered_df[search_condition]
    
    # 顯示圖表
    st.plotly_chart(create_city_chart(df), use_container_width=True)
    
    # 顯示總診所數量
    st.metric('總診所數量', len(filtered_df))
    
    # 顯示診所列表
    st.header('診所列表')
    
    # 新增收藏功能
    for idx, row in filtered_df.iterrows():
        col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
        
        with col1:
            clinic_id = f"{row['醫事機構名稱']}_{row['地址']}"
            is_favorite = clinic_id in st.session_state.favorite_clinics
            if st.checkbox('⭐', key=f'fav_{idx}', value=is_favorite):
                st.session_state.favorite_clinics.add(clinic_id)
            else:
                st.session_state.favorite_clinics.discard(clinic_id)
        
        with col2:
            st.write(f"""
            **{row['醫事機構名稱']}**  
            地址：{row['地址']}  
            電話：{row['電話']}  
            類型：{row['診所類型']}
            """)
        
        st.divider()
    
    # 顯示收藏的診所
    if st.sidebar.checkbox('顯示收藏的診所'):
        st.header('收藏的診所')
        favorite_df = df[df.apply(lambda x: f"{x['醫事機構名稱']}_{x['地址']}" in st.session_state.favorite_clinics, axis=1)]
        if len(favorite_df) > 0:
            st.dataframe(favorite_df[['醫事機構名稱', '地址', '電話', '診所類型']])
        else:
            st.info('尚未收藏任何診所')

if __name__ == '__main__':
    main()