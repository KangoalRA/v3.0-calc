import streamlit as st
import pandas as pd

st.set_page_config(page_title="무매법V3 도우미", page_icon="💰")
st.title("💰 무한매수법 V3.0 대시보드")

# --- [1] 사이드바: 기본 설정 & 파일 업로드 ---
st.sidebar.header("⚙️ 기본 설정")

# 자금 설정 (형님이 원하신 기능!)
total_capital = st.sidebar.number_input("총 투자원금 ($)", value=3700, step=100)
split_count = st.sidebar.number_input("설정 분할 횟수 (회)", value=40, step=1)

st.sidebar.markdown("---")
st.sidebar.header("📂 엑셀 파일 업로드")
uploaded_file = st.sidebar.file_uploader("엑셀(.xlsx)을 올려주세요", type=['xlsx'])

# 변수 초기화
my_avg = 0.0
my_qty = 0
one_shot_limit = total_capital / split_count  # 1회 매수 금액

# 엑셀 읽기 로직
if uploaded_file:
    try:
        # 데이터 읽기 (1~3행 무시)
        df = pd.read_excel(uploaded_file, header=3)
        df = df.dropna(subset=['날짜'])
        
        if not df.empty:
            last_row = df.iloc[-1]
            try:
                # 엑셀에서 평단/수량 가져오기
                my_avg = float(last_row.get('평균단가', last_row.get('평단가', 0)))
                my_qty = int(last_row.get('보유수량', last_row.get('수량', 0)))
                st.sidebar.success(f"✅ 데이터 로드 완료! (수량: {my_qty}개)")
            except:
                st.sidebar.warning("⚠️ 평단가/수량을 못 찾았습니다. 직접 입력해주세요.")
    except Exception as e:
        st.error(f"엑셀 읽기 실패: {e}")

# --- [2] 자금 현황판 (여기가 추가된 부분!) ---
used_money = my_avg * my_qty # 현재 투입된 금액
remain_money = total_capital - used_money # 남은 돈
progress_rate = (used_money / total_capital) * 100 if total_capital > 0 else 0 # 진행률

st.subheader("📊 나의 자금 현황")
col_m1, col_m2, col_m3 = st.columns(3)

with col_m1:
    st.metric(label="1회차 투자금액", value=f"${one_shot_limit:.1f}", delta=f"{split_count}분할")
with col_m2:
    st.metric(label="남은 총알 (매수 가능)", value=f"${remain_money:,.0f}")
with col_m3:
    st.metric(label="현재 진행률", value=f"{progress_rate:.1f}%", delta=f"투입: ${used_money:,.0f}")

st.divider() # 구분선

# --- [3] 데이터 입력 및 계산 ---
st.subheader("📝 오늘 주문 계산기")

c1, c2 = st.columns(2)
with c1:
    cur_price = st.number_input("현재가 (프리장/실시간 $)", value=0.0, step=0.01, format="%.2f")
    avg_price = st.number_input("내 평단가 ($)", value=my_avg, step=0.01, format="%.2f")
with c2:
    qty = st.number_input("보유 수량 (개)", value=my_qty, step=1)
    
    # 매수 수량 자동 제안 (1회차 금액에 맞춰서)
    # 0으로 나누기 방지
    calc_buy_qty = 1
    if cur_price > 0:
        calc_buy_qty = int(one_shot_limit // cur_price) # 1회 금액으로 살 수 있는 개수
        if calc_buy_qty < 1: calc_buy_qty = 1 # 최소 1주는 사야 함
        
    buy_cnt = st.number_input("매수 할 수량 (개)", value=calc_buy_qty, step=1, help="1회 투자금에 맞춰 자동 계산된 수량입니다.")

# --- [4] 결과 출력 ---
if st.button("🚀 계산하기", type="primary"):
    st.markdown("---")
    
    loc_buy = avg_price if avg_price > 0 else cur_price
    loc_sell = avg_price * 1.1
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.info("🔴 **LOC 매수**")
        st.metric("매수 가격", f"${loc_buy:.2f}")
        st.write(f"👉 **{buy_cnt}주** 매수 주문")
        buy_total = loc_buy * buy_cnt
        st.caption(f"(예상 소요금액: ${buy_total:.2f})")

    with col_b:
        st.success("🔵 **LOC 매도 (큰매도)**")
        st.metric("매도 가격", f"${loc_sell:.2f}")
        
        if qty > 0:
            st.write(f"👉 **{qty}주 (전량)** 매도 주문")
            profit = (loc_sell - avg_price) * qty
            st.caption(f"(실현 예상 수익: +${profit:.2f})")
        else:
            st.write("보유 수량이 없습니다.")
