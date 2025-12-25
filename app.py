import streamlit as st
import pandas as pd

st.set_page_config(page_title="무매법V3 도우미", page_icon="💰")
st.title("💰 무한매수법 V3.0 대시보드")

# --- [1] 사이드바: 기본 설정 & 파일 업로드 ---
st.sidebar.header("⚙️ 기본 설정")

# 자금 설정
total_capital = st.sidebar.number_input("총 투자원금 ($)", value=3700, step=100)
split_count = st.sidebar.number_input("설정 분할 횟수 (회)", value=40, step=1)

st.sidebar.markdown("---")
st.sidebar.header("📂 엑셀 파일 업로드")
uploaded_file = st.sidebar.file_uploader("엑셀(.xlsx)을 올려주세요", type=['xlsx'])

# 변수 초기화 (기본값)
default_avg = 0.0
default_qty = 0
one_shot_limit = total_capital / split_count  # 1회 매수 금액

# 엑셀 읽기
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, header=3)
        df = df.dropna(subset=['날짜'])
        if not df.empty:
            last_row = df.iloc[-1]
            try:
                default_avg = float(last_row.get('평균단가', last_row.get('평단가', 0)))
                default_qty = int(last_row.get('보유수량', last_row.get('수량', 0)))
                st.sidebar.success(f"✅ 데이터 로드 완료! (수량: {default_qty}개)")
            except:
                st.sidebar.warning("⚠️ 평단가/수량을 못 찾았습니다.")
    except Exception as e:
        st.error(f"엑셀 읽기 실패: {e}")

# --- [2] 현황판 자리를 먼저 찜해둠 (빈칸 만들기) ---
status_container = st.container()

# --- [3] 데이터 입력 (먼저 입력을 받아야 계산을 하니까!) ---
st.subheader("📝 오늘 데이터 입력")

c1, c2 = st.columns(2)
with c1:
    cur_price = st.number_input("현재가 (프리장/실시간 $)", value=0.0, step=0.01, format="%.2f")
    # 여기서 입력받은 값을 'real_avg' 변수에 저장
    real_avg = st.number_input("내 평단가 ($)", value=default_avg, step=0.01, format="%.2f")
with c2:
    # 여기서 입력받은 값을 'real_qty' 변수에 저장
    real_qty = st.number_input("보유 수량 (개)", value=default_qty, step=1)
    
    # 매수 수량 자동 제안
    calc_buy_qty = 1
    if cur_price > 0:
        calc_buy_qty = int(one_shot_limit // cur_price)
        if calc_buy_qty < 1: calc_buy_qty = 1
        
    buy_cnt = st.number_input("매수 할 수량 (개)", value=calc_buy_qty, step=1)

# --- [4] 이제 찜해둔 자리에 현황판 채워넣기 (실시간 계산) ---
# 사용자가 입력한 real_avg, real_qty로 계산함!
with status_container:
    used_money = real_avg * real_qty # 현재 투입금
    remain_money = total_capital - used_money # 남은 돈
    progress_rate = (used_money / total_capital) * 100 if total_capital > 0 else 0 # 진행률
    
    st.subheader("📊 나의 자금 현황 (실시간)")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric(label="1회차 투자금", value=f"${one_shot_limit:.1f}", delta=f"{split_count}분할")
    with m2:
        # 남은 돈 색깔 표시 (마이너스면 빨간색 경고)
        st.metric(label="남은 총알 (매수 가능)", value=f"${remain_money:,.0f}")
    with m3:
        st.metric(label="현재 진행률", value=f"{progress_rate:.1f}%", delta=f"투입: ${used_money:,.0f}")
    
    st.divider()

# --- [5] 결과 계산 버튼 ---
if st.button("🚀 계산하기", type="primary"):
    st.markdown("---")
    
    loc_buy = real_avg if real_avg > 0 else cur_price
    loc_sell = real_avg * 1.1
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.info("🔴 **LOC 매수**")
        st.metric("매수 가격", f"${loc_buy:.2f}")
        st.write(f"👉 **{buy_cnt}주** 매수 주문")
        st.caption(f"(예상: ${loc_buy * buy_cnt:.2f})")

    with col_b:
        st.success("🔵 **LOC 매도 (큰매도)**")
        st.metric("매도 가격", f"${loc_sell:.2f}")
        if real_qty > 0:
            st.write(f"👉 **{real_qty}주 (전량)** 매도 주문")
            st.caption(f"(예상수익: +${(loc_sell - real_avg) * real_qty:.2f})")
        else:
            st.write("보유 수량이 없습니다.")
