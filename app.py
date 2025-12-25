import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="무한매수법 대시보드", layout="wide")

# ==========================================
# [LEFT] 사이드바: 전략 설정 및 기준값
# ==========================================
with st.sidebar:
    st.header("⚙️ 전략 설정")
    st.info("투자 원칙을 설정하면 기준값이 계산됩니다.")
    
    # 1. 원금 및 분할 설정
    total_principal = st.number_input(
        "총 투자 원금 ($)", 
        value=4000.0, 
        step=100.0
    )
    
    split_count = st.number_input(
        "분할 횟수 (회)", 
        value=40, 
        step=1
    )
    
    st.divider()
    st.subheader("📌 매수 기준 (자동 계산)")
    
    # 1회 투자금 한도 계산
    if split_count > 0:
        one_time_limit = total_principal / split_count
    else:
        one_time_limit = 0
    
    st.metric(label="1회 투자금 한도", value=f"${one_time_limit:,.2f}")
    
    # [핵심] 기본 매수 수량이 표시될 자리 미리 확보 (빈 공간 생성)
    # 메인 화면에서 현재가를 입력하면 이곳에 수량이 뜹니다.
    base_qty_placeholder = st.empty()
    st.caption(f"💡 1회 한도(${one_time_limit:.0f}) ÷ 현재가")

# ==========================================
# [MAIN] 메인 화면: 데이터 입력 및 현황
# ==========================================

# 1. 상단 대시보드 (자리 확보)
dashboard_container = st.container()

st.divider()

# 2. 오늘 데이터 입력 (가운데 정렬)
st.subheader("📝 오늘 데이터 입력")
st.caption("현재가, 평단가, 보유수량 3가지만 입력하세요.")

c1, c2, c3 = st.columns(3)
with c1:
    current_price = st.number_input("① 현재가 (실시간 $)", value=55.36, step=0.01, format="%.2f")
with c2:
    my_avg_price = st.number_input("② 내 평단가 ($)", value=54.20, step=0.01, format="%.2f")
with c3:
    holdings = st.number_input("③ 보유 수량 (개)", value=1, step=1)

# --- [자동 계산 로직] ---

# A. 오늘 기본 매수 수량 계산 (Limit / Current Price)
if current_price > 0:
    daily_base_qty = int(one_time_limit // current_price)
else:
    daily_base_qty = 0

# [중요] 계산된 수량을 왼쪽 사이드바 빈 공간에 표시
with base_qty_placeholder.container():
    st.metric(label="오늘 기본 매수 수량", value=f"{daily_base_qty} 주")
    if daily_base_qty == 0:
        st.error("자금 부족/가격 오류")

# B. 자산 현황 역산 (남은 총알 등)
total_purchase_amt = my_avg_price * holdings  
remaining_cash = total_principal - total_purchase_amt 

current_eval_amt = current_price * holdings
eval_profit = current_eval_amt - total_purchase_amt
profit_rate = (eval_profit / total_purchase_amt) * 100 if total_purchase_amt > 0 else 0
burn_rate = (total_purchase_amt / total_principal) * 100 if total_principal > 0 else 0

# 3. [상단 채우기] 내 계좌 실시간 평가
with dashboard_container:
    st.title("📊 내 계좌 실시간 평가")
    
    # 주요 지표
    m1, m2, m3 = st.columns(3)
    m1.metric("총 매수금액", f"${total_purchase_amt:,.2f}")
    m2.metric("현재 평가금액", f"${current_eval_amt:,.2f}")
    m3.metric("평가 손익", f"${eval_profit:,.2f}", f"{profit_rate:.2f}%")
    
    # 남은 총알 및 진행상황
    st.info(f"💰 남은 총알: **${remaining_cash:,.2f}** (자금 소진율 {burn_rate:.1f}%)")


# 4. 작전 실행 (버튼)
st.markdown("---")
if st.button("🚀 작전 실행 (계산하기)", type="primary", use_container_width=True):
    
    st.subheader("🔴 매수 작전 (LOC Buy)")
    
    col_def, col_crash = st.columns([1, 1.5])
    
    # [왼쪽] 기본 방어
    with col_def:
        st.markdown("### 🛡️ 기본 방어")
        st.caption("내 평단가보다 낮을 때 매수")
        
        def_amount = my_avg_price * daily_base_qty
        
        # 기본 매수도 한도 체크
        msg = ""
        if def_amount > one_time_limit:
            msg = f" (⚠️ 한도 초과)"
            
        st.success(f"**가격: ${my_avg_price}**")
        st.success(f"**수량: {daily_base_qty}주** (왼쪽 기준값)")
        st.markdown(f"예상 금액: **${def_amount:.2f}**{msg}")

    # [오른쪽] 떡락 대응
    with col_crash:
        st.markdown("### 📉 떡락 대응 (지하실 줍줍)")
        st.caption(f"1회 한도 **${one_time_limit:.0f}** 내 자동 조절")
        
        drops = [0.10, 0.15, 0.20, 0.30]
        data = []
        
        for drop in drops:
            target_price = current_price * (1 - drop)
            
            # 수량 가중치
            if drop == 0.10: add_qty = 1
            elif drop == 0.15: add_qty = 1
            elif drop == 0.20: add_qty = 2
            else: add_qty = 3
            
            planned_qty = daily_base_qty + add_qty
            estimated_cost = target_price * planned_qty
            
            # [한도 컷 로직]
            final_qty = planned_qty
            note = ""
            
            if estimated_cost > one_time_limit:
                max_buyable = int(one_time_limit // target_price)
                if max_buyable == 0:
                    final_qty = 0
                    estimated_cost = 0
                    note = "🚫 자금 부족"
                else:
                    final_qty = max_buyable
                    estimated_cost = target_price * final_qty
                    note = f"⚠️ 한도 제한 ({planned_qty}→{final_qty}주)"
            else:
                note = f"🔥 {planned_qty}주 (기본{daily_base_qty}+{add_qty})"
                
            data.append({
                "하락률": f"- {int(drop*100)}%",
                "LOC 매수 가격": f"${target_price:.2f}",
                "주문 수량": note,
                "예상 금액": f"${estimated_cost:.1f}"
            })
            
        df = pd.DataFrame(data)
        st.table(df)
