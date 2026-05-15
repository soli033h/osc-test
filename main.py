import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(
    page_title="DIAF_TEST - JS Network Transfer",
    layout="centered"
)

# CSS 설정 (기존과 동일)
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stAppDeployButton { display: none !important; }
.centered-image { display: flex; justify-content: center; margin-bottom: 20px; }
.stButton > button { width: 100%; border-radius: 5px; height: 3em; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 비밀번호 확인 로직 (기존과 동일)
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.title("Access Restricted")
        pwd_input = st.text_input("비밀번호를 입력하세요", type="password")
        if st.button("입장하기"):
            if pwd_input == st.secrets.get("password", "1234"): # secrets 설정 확인
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("비밀번호가 올바르지 않습니다.")
        return False
    return True

if check_password():
    # 로고 영역
    st.markdown('<div class="centered-image"><h4>DIAF TEST PANEL</h4></div>', unsafe_allow_html=True)

    # 세션 상태 초기화
    if "history" not in st.session_state:
        st.session_state.history = pd.DataFrame(columns=["Value"])

    # 1. 접속 설정
    with st.expander("접속 설정 (Target B's IP/Port)", expanded=True):
        col_ip, col_port = st.columns(2)
        ip = col_ip.text_input("상대방 IP 주소", "127.0.0.1")
        port = col_port.number_input("포트 번호", 1, 65535, 8000)

    st.markdown("---")

    # 2. 제어 슬라이더
    osc_value = st.slider("전송 값 조절 (0.0 ~ 1.0)", 0.0, 1.0, 0.5, step=0.01)

    # 3. 전송 버튼
    if st.button("데이터 전송하기", type="primary"):
        # 히스토리 업데이트
        new_entry = pd.DataFrame({"Value": [osc_value]})
        st.session_state.history = pd.concat([st.session_state.history, new_entry], ignore_index=True).tail(30)
        
        # JavaScript를 통한 직접 통신 (핵심 부분)
        # 브라우저(A)가 직접 B의 IP로 fetch 요청을 보냅니다.
        js_send = f"""
        <script>
        (function() {{
            const url = "http://{ip}:{port}/data";
            const data = {{ value: {osc_value} }};
            
            fetch(url, {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify(data)
            }})
            .then(response => console.log('Success:', response))
            .catch(error => {{
                console.error('Error:', error);
                alert('전송 실패! B의 서버가 켜져 있는지, CORS 설정이 되어 있는지 확인하세요.');
            }});
        }})();
        </script>
        """
        components.html(js_send, height=0)
        st.success(f"전송 명령 보냄: {ip}:{port} -> {osc_value}")

    st.markdown("---")

    # 4. 시각화 영역
    if not st.session_state.history.empty:
        st.line_chart(st.session_state.history)
        st.dataframe(st.session_state.history.sort_index(ascending=False), use_container_width=True)
