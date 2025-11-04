import streamlit as st
import requests

# 1. API 기본 정보
SEARCH_API_URL = "https://collectionapi.metmuseum.org/public/collection/v1/search"
OBJECT_API_URL = "https://collectionapi.metmuseum.org/public/collection/v1/objects/"

# --- Streamlit 앱 UI ---
st.title("🎨 메트로폴리탄 미술관 작품 검색")
st.write("키워드를 입력해 The Met의 소장품을 검색해 보세요.")

# 2. 사용자로부터 키워드 입력받기
search_query = st.text_input("검색어 (예: 'Van Gogh' 또는 'Cat'):")

# 3. 검색 버튼
if st.button("검색하기"):
    if not search_query:
        st.warning("검색어를 입력해주세요.")
    else:
        st.write(f"'{search_query}' 검색 중...")

        # 4. API로 검색 요청 보내기
        search_params = {
            'q': search_query,
            'hasImages': 'true'  # 이미지가 있는 작품만 검색
        }
        
        try:
            # 검색 API 호출 (Object ID 목록 가져오기)
            search_response = requests.get(SEARCH_API_URL, params=search_params)
            search_response.raise_for_status()  # 오류가 있으면 예외 발생
            search_data = search_response.json()

            object_ids = search_data.get('objectIDs')

            if not object_ids:
                st.error("검색 결과가 없습니다. 다른 키워드를 시도해 보세요.")
            else:
                st.success(f"총 {search_data.get('total', 0)}개의 결과를 찾았습니다. (최대 5개 표시)")
                
                # 5. 검색된 작품 중 최대 5개만 가져오기
                for object_id in object_ids[:5]:
                    with st.spinner(f"작품 ID {object_id} 정보 로딩 중..."):
                        try:
                            # 개별 작품 API 호출 (상세 정보 가져오기)
                            obj_response = requests.get(f"{OBJECT_API_URL}{object_id}")
                            obj_response.raise_for_status()
                            obj_data = obj_response.json()

                            # 6. Streamlit에 결과 표시
                            st.divider() # 구분선
                            
                            # primaryImageSmall이 비어있지 않은지 확인
                            if obj_data.get('primaryImageSmall'):
                                st.subheader(obj_data.get('title', '제목 없음'))
                                st.image(
                                    obj_data['primaryImageSmall'], 
                                    caption=f"{obj_data.get('artistDisplayName', '작자 미상')}, {obj_data.get('objectDate', '연도 미상')}"
                                )
                                st.write(f"**작가:** {obj_data.get('artistDisplayName', '작자 미상')}")
                                st.write(f"**제작연도:** {obj_data.get('objectDate', '연도 미상')}")
                                st.write(f"**매체:** {obj_data.get('medium', '정보 없음')}")
                                st.link_button("자세히 보기", obj_data.get('objectURL', '#'))
                            
                        except requests.exceptions.RequestException as e:
                            st.error(f"작품 ID {object_id} 로딩 실패: {e}")

        except requests.exceptions.RequestException as e:
            st.error(f"API 요청 중 오류 발생: {e}")