import pandas as pd
import googlemaps
import time

# 初始化 Google Maps API
API_KEY = "AIzaSyCsTUruu9At5J17jPznlPC817-j72vWnSw"  # 替換為您的 Google Maps API 金鑰
gmaps = googlemaps.Client(key=API_KEY)

# 讀取資料
file_path = "C:\\Users\\User\\Documents\\GitHub\\clinic11312\\健保特約醫事機構診所.csv"

data = pd.read_csv(file_path, encoding='utf-8')  # 確保使用正確的編碼

# 確認欄位是否包含 "地址"
if "地址" not in data.columns:
    raise ValueError("CSV 資料中缺少 '地址' 欄位")

# 新增經緯度欄位
data["緯度"] = None
data["經度"] = None

# 定義地理編碼函數
def geocode_address(address):
    try:
        geocode_result = gmaps.geocode(address)
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            return location['lat'], location['lng']
    except Exception as e:
        print(f"地理編碼失敗: {e}")
    return None, None

# 開始地理編碼
for index, row in data.iterrows():
    address = row["地址"]
    if pd.notnull(address):  # 確保地址不為空
        lat, lon = geocode_address(address)
        data.at[index, "緯度"] = lat
        data.at[index, "經度"] = lon
        print(f"地址: {address} => 緯度: {lat}, 經度: {lon}")
        time.sleep(0.1)  # 控制請求速率，避免超過 API 限制

# 保存處理後的資料
output_file_path = "C:\\Users\\User\\Documents\\GitHub\\clinic11312\\健保特約醫事機構診所.csv"  # 使用原始字符串
data.to_csv(output_file_path, index=False, encoding='utf-8-sig')  # 使用 UTF-8 編碼保存文件，適合中文
print(f"地理編碼完成，結果已保存至: {output_file_path}")
