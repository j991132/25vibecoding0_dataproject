import streamlit as st
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components
import json

st.title("🗺️ 나만의 위치 북마크 지도")
st.write("현재 위치를 지도에 표시하고, 원하는 장소를 북마크하세요!")

# JavaScript로 사용자 위치 가져오기
geolocation_html = """
<script>
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                // Streamlit으로 좌표 전송
                window.parent.postMessage({
                    type: "streamlit:setComponentValue",
                    value: {
                        lat: position.coords.latitude,
                        lon: position.coords.longitude
                    }
                }, "*");
            },
            function(error) {
                // 에러 처리
                window.parent.postMessage({
                    type: "streamlit:setComponentValue",
                    value: { error: error.message }
                }, "*");
            }
        );
    } else {
        window.parent.postMessage({
            type: "streamlit:setComponentValue",
            value: { error: "이 브라우저는 위치 정보를 지원하지 않습니다." }
        }, "*");
    }
}
getLocation();
</script>
"""

# JavaScript 실행
location_data = components.html(geolocation_html, height=0)

# 세션 상태 초기화
if "places" not in st.session_state:
    st.session_state.places = []
if "current_location" not in st.session_state:
    st.session_state.current_location = None

# 위치 데이터 처리
if location_data:
    try:
        data = json.loads(location_data)
        if "error" in data:
            st.warning(f"위치 정보를 가져오지 못했습니다: {data['error']}")
            st.session_state.current_location = None
        else:
            st.session_state.current_location = (data["lat"], data["lon"])
            st.success("현재 위치를 성공적으로 가져왔습니다!")
    except:
        pass  # JSON 파싱 실패 또는 데이터 미준비 시 처리

# 북마크 입력 필드
st.subheader("장소 추가")
place = st.text_input("장소 이름", value="")
lat = st.number_input("위도 (Latitude)", value=37.5665, format="%.6f")
lon = st.number_input("경도 (Longitude)", value=126.9780, format="%.6f")

# 북마크 추가
if st.button("지도에 추가하기"):
    if place.strip() and -90 <= lat <= 90 and -180 <= lon <= 180:
        st.session_state.places.append((place, lat, lon))
    else:
        st.error("장소 이름과 유효한 위도(-90~90)/경도(-180~180)를 입력하세요.")

# 모든 북마크 지우기
if st.button("모든 장소 지우기"):
    st.session_state.places = []
    st.experimental_rerun()

# Folium 지도 생성
if st.session_state.current_location:
    # 현재 위치를 중심으로 지도 설정
    m = folium.Map(location=st.session_state.current_location, zoom_start=12)
    # 현재 위치 마커 추가
    folium.Marker(
        st.session_state.current_location,
        tooltip="현재 위치",
        icon=folium.Icon(color="red", icon="user")
    ).add_to(m)
else:
    # 기본 위치: 서울 시청
    m = folium.Map(location=[37.5665, 126.9780], zoom_start=6)

# 북마크 마커 추가
for name, lat, lon in st.session_state.places:
    folium.Marker([lat, lon], tooltip=name).add_to(m)

# 모든 마커를 포함하도록 지도 범위 조정
all_locations = [(lat, lon) for _, lat, lon in st.session_state.places]
if st.session_state.current_location:
    all_locations.append(st.session_state.current_location)
if all_locations:
    lats, lons = zip(*all_locations)
    m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])

# 지도 렌더링
st_folium(m, width=700, height=500)
