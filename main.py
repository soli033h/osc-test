import streamlit as st
from pythonosc import udp_client
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 페이지 설정
st.set_page_config(
    page_title="DIAF_TEST - Simple OSC TEST",
    layout="centered",
    page_icon="seoul_arts_logo_favicon.png"
)

# CSS
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stAppDeployButton {
    display: none !important;
}
[data-testid="stToolbar"] {
    visibility: hidden;
    display: none;
}
.centered-image {
    display: flex;
    justify-content: center;
    margin-bottom: 20px;
}
.stButton > button {
    width: 100%;
    border-radius: 5px;
    height: 3em;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# 비밀번호 확인
def check_password():

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:

        st.title("Access Restricted")

        pwd_input = st.text_input(
            "비밀번호를 입력하세요",
            type="password"
        )

        if st.button("입장하기"):

            if pwd_input == st.secrets["password"]:
                st.session_state.authenticated = True
                st.rerun()

            else:
                st.error("비밀번호가 올바르지 않습니다.")

        return False

    return True


if check_password():

    # 로고
    st.markdown(
        '<div class="centered-image">',
        unsafe_allow_html=True
    )

    st.image("seoul_arts_logo.png", width=1000)

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    # 세션 상태 초기화
    if "running" not in st.session_state:
        st.session_state.running = False

    if "history" not in st.session_state:
        st.session_state.history = pd.DataFrame(
            columns=["Value"]
        )

    # 접속 설정
    with st.expander("접속 설정 (IP/Port)", expanded=True):

        col_ip, col_port = st.columns(2)

        ip = col_ip.text_input(
            "IP 주소",
            "127.0.0.1"
        )

        port = col_port.number_input(
            "포트 번호",
            min_value=1,
            max_value=65535,
            value=8000
        )

    st.markdown("---")

    # OSC 슬라이더
    osc_value = st.slider(
        "OSC 전송 값 조절 (0.0 ~ 1.0)",
        0.0,
        1.0,
        0.5,
        step=0.01
    )

    # 버튼
    btn_col1, btn_col2 = st.columns(2)

    if btn_col1.button(
        "보내기",
        type="primary"
    ):
        st.session_state.running = True

    if btn_col2.button("멈추기"):
        st.session_state.running = False

    st.markdown("---")

    # 상태 영역
    status_holder = st.empty()
    chart_holder = st.empty()
    table_holder = st.empty()

    # 실행 중
    if st.session_state.running:

        # 0.5초마다 자동 새로고침
        st_autorefresh(
            interval=500,
            key="osc_refresh"
        )

        status_holder.success(
            f"전송 중: {ip}:{port}"
        )

        try:

            # OSC 클라이언트 생성
            client = udp_client.SimpleUDPClient(
                ip,
                int(port)
            )

            # OSC 전송
            client.send_message(
                "/param",
                float(osc_value)
            )

            # 기록 저장
            new_entry = pd.DataFrame({
                "Value": [osc_value]
            })

            st.session_state.history = pd.concat(
                [
                    st.session_state.history,
                    new_entry
                ],
                ignore_index=True
            ).tail(30)

        except Exception as e:

            st.error(f"오류 발생: {e}")
            st.session_state.running = False

    else:

        status_holder.info(
            "현재 정지 상태입니다."
        )

    # 차트 출력
    if not st.session_state.history.empty:

        chart_holder.line_chart(
            st.session_state.history
        )

        table_holder.dataframe(
            st.session_state.history.sort_index(
                ascending=False
            ),
            use_container_width=True
        )
