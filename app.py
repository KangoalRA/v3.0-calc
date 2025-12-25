import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="무한매수법 대시보드", layout="wide")

# ==========================================
# [LEFT] 사이드바: 전략 설정 및 기준값
# ==========================================
with st.sidebar:
    st.header("⚙️ 전략 설정")
    st.info("투자 원칙을 설정하세요.")
    
    # 1. 원금 및 분할 설정
    total_principal = st.number_input("총 투자 원금 ($)", value=4000.0, step=100.0)
    split_count = st.number_input("분할 횟수 (회)", value=40, step=1)
    
    st.divider()
    st.subheader("📌 매수 기준 (자동 계산)")
    
    # 1회 투자금 한도 계산
    if split_count > 0:
        one_time_limit = total_principal / split_count
    else:
        one_time_limit = 0
    
    st.metric(label="1회 투자금 한도", value=f"${one_time_limit:,.2f}")
    
    # [핵심] 기본 매수 수량이 표시될 자리
    base_qty_placeholder = st.empty()
    st.caption(f"💡 한도(${one_time_limit:.0f}) ÷ 현재가")

# ==========================================
# [MAIN] 메인 화면
# ==========================================

dashboard_container = st.container()
st.divider()

# 1. 데이터 입력
st.subheader("📝 오늘 데이터 입력")
c1, c2, c3 = st.columns(3)
with c1:
    current_price = st.number_input("① 현재가 (실시간 $)", value=55.36, step=0.01, format="%.2f")
with c2:
    my_avg_price = st.number_input("② 내 평단가 ($)", value=54.20, step=0.01, format="%.2f")
with c3:
    holdings = st.number_input("③ 보유 수량 (개)", value=1, step=1)

# --- [자동 계산 로직] ---

# A. 오늘 기본 매수 수량 계산
if current_price > 0:
    daily_base_qty = int(one_time_limit // current_price)
else:
    daily_base_qty = 0

# [왼쪽 사이드바 업데이트]
with base_qty_placeholder.container():
    st.metric(label="오늘 기본 매수 수량", value=f"{daily_base_qty} 주")
    if daily_base_qty == 0:
        st.error("자금 부족 / 가격 오류")

# B. 현황 계산
total_purchase_amt = my_avg_price * holdings  
remaining_cash = total_principal - total_purchase_amt 
current_eval_amt = current_price * holdings
eval_profit = current_eval_amt - total_purchase_amt
profit_rate = (eval_profit / total_purchase_amt) * 100 if total_purchase_amt > 0 else 0

# C. [상단 대시보드 표시]
with dashboard_container:
    st.title("📊 내 계좌 실시간 평가")
    m1, m2, m3 = st.columns(3)
    m1.metric("총 매수금액", f"${total_purchase_amt:,.2f}")
    m2.metric("현재 평가금액", f"${current_eval_amt:,.2f}")
    m3.metric("평가 손익", f"${eval_profit:,.2f}", f"{profit_rate:.2f}%")
    st.info(f"💰 남은 총알: **${remaining_cash:,.2f}**")


# 2. 작전 실행
st.markdown("---")
if st.button("🚀 작전 실행 (계산하기)", type="primary", use_container_width=True):
    
    # ===================================================
    # [1] 매수 작전 (순서 변경: 매수가 위로 올라옴)
    # ===================================================
    st.subheader("🔴 매수 작전 (LOC Buy)")
    
    col_def, col_crash = st.columns([1, 1.5])
    
    # 1-1. 기본 방어 (평단가)
    with col_def:
        st.markdown("### 🛡️ 기본 방어")
        st.caption("내 평단가보다 낮을 때 매수")
        
        def_amount = my_avg_price * daily_base_qty
        
        # 한도 체크
        msg = ""
        if def_amount > one_time_limit:
            msg = f" (⚠️ 한도 ${one_time_limit:.0f} 초과)"
            
        st.success(f"**가격: ${my_avg_price}**")
        st.success(f"**수량: {daily_base_qty}주**")
        st.markdown(f"예상 금액: **${def_amount:.2f}**{msg}")

    # 1-2. 떡락 대응 (로직 전면 수정: 한도 내 N주 사려면?)
    with col_crash:
        st.markdown("### 📉 떡락 대응 (지하실 줍줍)")
        st.caption(f"1회 한도 **${one_time_limit:.0f}**로 N주를 사려면 얼마까지 떨어져야 할까?")
        
        data = []
        
        # 2주부터 5주까지 계산 (사용자 요청: 2주 ~ 5주)
        # N주를 사기 위한 최대 가격 = 1회 한도 / N
        for qty in [2, 3, 4, 5]:
            # 한도로 살 수 있는 최대 단가 계산
            target_unit_price = one_time_limit / qty
            
            # 현재가 대비 얼마나 떨어져야 하는지?
            if current_price > 0:
                drop_rate = (target_unit_price - current_price) / current_price * 100
            else:
                drop_rate = 0
                
            # 예: 현재가 $50, 목표가 $30이면 -> -40% 하락 필요
            # 단, 목표가가 현재가보다 높으면(이미 살 수 있으면) 하락률은 (+)로 표시됨 -> 0%로 처리하거나 그대로 표시
            
            # 예상 매수 금액 (거의 한도에 딱 맞음)
            est_total = target_unit_price * qty
            
            # 평단가(기본 LOC 매수가) 대비 하락률도 참고용으로 계산
            # drop_from_loc = (target_unit_price - my_avg_price) / my_avg_price * 100

            data.append({
                "목표 수량": f"🔥 {qty}주 매수",
                "필요 주가 (LOC)": f"${target_unit_price:.2f} 이하",
                "현재가 대비": f"{drop_rate:.1f}% ▼" if drop_rate < 0 else "매수 가능",
                "예상 금액": f"${est_total:.1f}"
            })
            
        df = pd.DataFrame(data)
        st.table(df)

    st.markdown("---")

    # ===================================================
    # [2] 매도 작전 (순서 변경: 매수 아래로 내려감)
    # ===================================================
    st.subheader("🔵 매도 작전 (LOC Sell)")
    st.caption("수익률 구간별 매도 전략 (LOC 매도)")
    
    # 매도 목표가 계산
    price_quarter = my_avg_price * 1.05 # 5% 수익
    price_all = my_avg_price * 1.15     # 15% 수익
    
    # 매도 수량 계산
    qty_quarter = max(1, int(holdings * 0.25)) # 쿼터(1/4)
    qty_all = holdings                         # 전량
    
    col_sell_1, col_sell_2 = st.columns(2)
    
    with col_sell_1:
        st.info("### 1️⃣ 1차 익절 (5%~)")
        st.markdown(f"**목표가: ${price_quarter:.2f}**")
        st.write(f"매도 수량: **{qty_quarter}주** (25%)")
        
    with col_sell_2:
        st.success("### 2️⃣ 졸업/대박 (15%~)")
        st.markdown(f"**목표가: ${price_all:.2f}**")
        st.write(f"매도 수량: **{qty_all}주** (전량)")
