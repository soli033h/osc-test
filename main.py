import streamlit as st
import pandas as pd
import time
import asyncio
import websockets
import json

# 1. 페이지 설정
st.set_page_config(
    page_title="DIAF_TEST - WebSocket TEST", 
    layout="centered",
    page_icon="seoul_arts_logo_favicon.png"
)

# CSS 설정 (상단 바 제거 및 스타일링)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton { display: none !important; }
    [data-testid="stToolbar"] { visibility: hidden; display: none; }
    .centered-image { display: flex; justify-content: center; margin-bottom: 20px; }
    .stButton > button { width: 100%; border-radius: 5px; height: 3em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. 비밀번호 확인 로직
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.title("Access Restricted")
        pwd_input = st.text_input("비밀번호를 입력하세요", type="password")
        if st.button("입장하기"):
            # st.secrets["password"] 설정이 되어 있어야 합니다.
            if pwd_input == st.secrets.get("password", "1234"): 
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("비밀번호가 올바르지 않습니다.")
        return False
    return True

# 3. 비동기 웹소켓 전송 함수
async def send_websocket_data(uri, value):
    async with websockets.connect(uri) as websocket:
        # JSON 형식으로 데이터를 보낼 수도 있고, 일반 텍스트로 보낼 수도 있습니다.
        payload = json.dumps({"address": "/param", "value": value})
        await websocket.send(payload)

if check_password():
    # 상단 이미지
    st.markdown('<div class="centered-image">', unsafe_allow_html=True)
    try:
        st.image("seoul_arts_logo.png", width=300) # 너비는 적절히 조절하세요
    except:
        st.info("이미지 파일을 찾을 수 없습니다.")
    st.markdown('</div>', unsafe_allow_html=True)

    # 4. 상태 관리 변수 초기화
    if "running" not in st.session_state:
        st.session_state.running = False
    if "history" not in st.session_state:
        st.session_state.history = pd.DataFrame(columns=["Value"])

    # 5. 접속 설정 (WebSocket URI)
    with st.expander("웹소켓 접속 설정 (WS URL)", expanded=True):
        col_url, col_int = st.columns([3, 1])
        ws_url = col_url.text_input("WebSocket 주소", "ws://localhost:8000")
        interval = col_int.number_input("전송 간격(초)", value=0.5, step=0.1)

    st.markdown("---")

    # 6. 메인 컨트롤러 (슬라이더)
    osc_value = st.slider("WebSocket 전송 값 조절 (0.0 ~ 1.0)", 0.0, 1.0, 0.5, step=0.01)

    # 7. 보내기/멈추기 버튼
    btn_col1, btn_col2 = st.columns(2)
    if btn_col1.button("보내기", type="primary"):
        st.session_state.running = True
    if btn_col2.button("멈추기"):
        st.session_state.running = False

    st.markdown("---")

    # 8. 출력용 컨테이너
    status_holder = st.empty()
    chart_holder = st.empty()
    table_holder = st.empty()

    # 9. 실시간 실행 루프
    if st.session_state.running:
        status_holder.success(f"연결 중: {ws_url} (JSON 데이터 전송)")
        
        # 무한 루프 시작
        while st.session_state.running:
            try:
                # 비동기 함수 실행
                asyncio.run(send_websocket_data(ws_url, osc_value))
                
                # 기록 업데이트 (최근 30개)
                new_entry = pd.DataFrame({"Value": [osc_value]})
                st.session_state.history = pd.concat([st.session_state.history, new_entry], ignore_index=True).tail(30)
                
                # 차트 및 표 업데이트
                chart_holder.line_chart(st.session_state.history)
                table_holder.dataframe(st.session_state.history.sort_index(ascending=False), use_container_width=True)
                
                time.sleep(interval)
                
            except Exception as e:
                st.error(f"서버 연결 실패: {e}")
                st.session_state.running = False
                break
    else:
        status_holder.info("현재 정지 상태입니다. '보내기' 버튼을 눌러주세요.")
        if not st.session_state.history.empty:
            chart_holder.line_chart(st.session_state.history)
            table_holder.dataframe(st.session_state.history.sort_index(ascending=False), use_container_width=True)
