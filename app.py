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
    
    # [핵심] 기본 매수 수량이 표시될 자리 (메인 입력 후 자동 업데이트)
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


# 2. 작전 실행 (매도 & 매수)
st.markdown("---")
if st.button("🚀 작전 실행 (계산하기)", type="primary", use_container_width=True):
    
    # ---------------------------------------------------
    # [매도 작전] (업데이트됨: 5% 쿼터 / 15% 전량)
    # ---------------------------------------------------
    st.subheader("🔵 매도 작전 (LOC Sell)")
    st.caption("수익률 구간별 매도 전략입니다. (LOC 매도로 설정하세요)")
    
    # 매도 목표가 계산
    price_quarter = my_avg_price * 1.05 # 5% 수익
    price_all = my_avg_price * 1.15     # 15% 수익
    
    # 매도 수량 계산
    qty_quarter = max(1, int(holdings * 0.25)) # 쿼터(1/4)
    qty_all = holdings                         # 전량
    
    # 화면 표시 (2분할)
    col_sell_1, col_sell_2 = st.columns(2)
    
    with col_sell_1:
        st.info("### 1️⃣ 1차 익절 (5%~)")
        st.markdown(f"**목표가: ${price_quarter:.2f}**")
        st.write(f"매도 수량: **{qty_quarter}주** (25%)")
        st.caption("수익률 5% 이상 15% 미만 구간")
        
    with col_sell_2:
        st.success("### 2️⃣ 졸업/대박 (15%~)")
        st.markdown(f"**목표가: ${price_all:.2f}**")
        st.write(f"매도 수량: **{qty_all}주** (전량)")
        st.caption("수익률 15% 이상 구간")
    
    st.markdown("---")
    
    # ---------------------------------------------------
    # [매수 작전]
    # ---------------------------------------------------
    st.subheader("🔴 매수 작전 (LOC Buy)")
    
    col_def, col_crash = st.columns([1, 1.5])
    
    # 1. 기본 방어 (평단가)
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

    # 2. 떡락 대응 (보내주신 엑셀 기준 적용)
