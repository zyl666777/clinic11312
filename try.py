import folium

m = folium.Map(location=[23.6978, 120.9605], zoom_start=8)
m.save('test_map.html')

print("地圖已成功保存為 test_map.html")
