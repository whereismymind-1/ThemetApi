# app.py
import streamlit as st
import requests

# -------------------------------------------------
# 1. API 키 불러오기
# Streamlit 클라우드에서는 'Settings > Secrets'에 설정된 값을 가져옵니다.
# -------------------------------------------------
try:
    API_KEY = st.secrets["OWM_API_KEY"]
except KeyError:
    st.error("⚠️ Streamlit 설정(Secrets)에 'OWM_API_KEY'가 없습니다!")
    st.info("앱 관리자라면, 앱의 'Settings > Secrets'에서 API 키를 추가해주세요.")
    st.stop()
except FileNotFoundError:
    # (로컬 테스트용) .streamlit/secrets.toml 파일이 없는 경우를 대비
    st.error("⚠️ API 키를 찾을 수 없습니다. 로컬 테스트 시 .streamlit/secrets.toml 파일이 필요합니다.")
    st.stop()


# -------------------------------------------------
# 2. Streamlit UI 구성
# -------------------------------------------------
st.title("🌦️ 실시간 날씨 검색 (Streamlit Cloud)")
st.write("도시 이름을 **영어**로 입력하세요. (예: Seoul, London, Paris)")

city_name = st.text_input("도시 이름:", "Seoul")

if st.button("날씨 검색"):
    if not city_name:
        st.warning("도시 이름을 입력해주세요.")
    else:
        # -------------------------------------------------
        # 3. OpenWeatherMap API에 데이터 요청
        # -------------------------------------------------
        base_url = "https://api.openweathermap.org/data/2.5/weather"
        
        params = {
            "q": city_name,
            "appid": API_KEY,   # st.secrets에서 불러온 키 사용
            "units": "metric",  # 섭씨
            "lang": "kr"        # 한국어
        }
        
        try:
            response = requests.get(base_url, params=params)
            
            # -------------------------------------------------
            # 4. 응답(Response) 처리 및 결과 표시
            # -------------------------------------------------
            if response.status_code == 200:
                data = response.json()
                
                # 정보 추출
                city = data['name']
                country = data['sys']['country']
                weather_desc = data['weather'][0]['description']
                icon_code = data['weather'][0]['icon']
                icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
                temp = data['main']['temp']
                feels_like = data['main']['feels_like']
                humidity = data['main']['humidity']

                # 결과 표시
                st.subheader(f"{city}, {country}의 현재 날씨")
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.image(icon_url, width=100)
                with col2:
                    st.metric(label="현재 날씨", value=f"{temp}°C", delta=f"체감: {feels_like}°C")
                    st.write(f"**상세:** {weather_desc}")
                
                st.metric("습도", f"{humidity}%")

            elif response.status_code == 404:
                st.error(f"'{city_name}' 도시를 찾을 수 없습니다. 영문 이름을 확인해주세요.")
            
            elif response.status_code == 401:
                # 401 오류는 대부분 API 키 문제
                st.error("API 키가 유효하지 않습니다. Streamlit Secrets 설정을 확인하세요.")
            
            else:
                st.error(f"오류가 발생했습니다. (상태 코드: {response.status_code})")

        except requests.exceptions.RequestException as e:
            st.error(f"API 요청 중 네트워크 오류가 발생했습니다: {e}")