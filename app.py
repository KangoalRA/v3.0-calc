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

# 변수 초기화
default_avg = 0.0
default_qty = 0
one_shot_limit = total_capital / split_count if split_count > 0 else 0 # 1회 매수 금액

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

# --- [2] 현황판 자리를 먼저 찜해둠 ---
status_container = st.container()

# --- [3] 데이터 입력 ---
st.subheader("📝 오늘 데이터 입력")

c1, c2 = st.columns(2)
with c1:
    cur_price = st.number_input("현재가 (프리장/실시간 $)", value=0.0, step=0.01, format="%.2f")
    real_avg = st.number_input("내 평단가 ($)", value=default_avg, step=0.01, format="%.2f")
with c2:
    real_qty = st.number_input("보유 수량 (개)", value=default_qty, step=1)
    
    # 매수 수량 자동 제안
    calc_buy_qty = 1
    if cur_price > 0:
        calc_buy_qty = int(one_shot_limit // cur_price)
        if calc_buy_qty < 1: calc_buy_qty = 1
        
    buy_cnt = st.number_input("매수 할 수량 (개)", value=calc_buy_qty, step=1)

# --- [4] 현황판 채워넣기 (회차 기능 추가!) ---
with status_container:
    used_money = real_avg * real_qty # 현재 투입금
    remain_money = total_capital - used_money # 남은 돈
    
    # 현재 회차 계산 (투입금 / 1회차금액)
    current_round = used_money / one_shot_limit if one_shot_limit > 0 else 0
    progress_pct = (used_money / total_capital) * 100 if total_capital > 0 else 0
    
    st.subheader("📊 나의 자금 현황 (실시간)")
    
    # 4개 컬럼으로 나눠서 보기 좋게 배치
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(label="1회차 투자금", value=f"${one_shot_limit:.0f}")
    with m2:
        # 여기가 핵심! (현재 회차 표시)
        st.metric(label="현재 진행", value=f"{current_round:.1f}회차", delta=f"총 {split_count}회")
    with m3:
        st.metric(label="남은 총알", value=f"${remain_money:,.0f}")
    with m4:
        st.metric(label="진행률", value=f"{progress_pct:.1f}%")
        
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
