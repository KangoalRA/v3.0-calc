import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="무한매수법 대시보드", layout="wide")

# --- [핵심 변경 1] 상단 배치를 위한 컨테이너 미리 선언 ---
# 파이썬은 코드를 위에서 아래로 읽지만, Streamlit의 container를 쓰면
# 나중에 계산된 결과를 이 '빈 그릇' 안에 채워 넣어 화면 맨 위에 띄울 수 있습니다.
dashboard_container = st.container()

st.divider() # 시각적 분리선

# --- 2. 데이터 입력 섹션 (화면 중간) ---
st.header("📝 오늘 데이터 입력")

col_input1, col_input2, col_input3 = st.columns(3)

with col_input1:
    current_price = st.number_input("현재가 (프리장/실시간 $)", value=55.36, step=0.01, format="%.2f")

with col_input2:
    my_avg_price = st.number_input("내 평단가 ($)", value=54.20, step=0.01, format="%.2f")

with col_input3:
    holdings = st.number_input("보유 수량 (개)", value=1, step=1)

col_input4, col_input5, col_input6 = st.columns(3)
with col_input4:
    daily_base_qty = st.number_input("오늘 기본 매수 수량 (개)", value=1, step=1, help="평단 아래일 때 LOC 매수할 기본 수량")

with col_input5:
    one_time_invest = st.number_input("1회 투자금 ($)", value=74.0, step=1.0, help="한 번 매수 시 사용할 최대 가용 금액")
    
with col_input6:
    total_seed = st.number_input("남은 총알 (예수금 $)", value=3646.0, step=10.0)

# --- 계산 로직 ---
total_purchase_amt = my_avg_price * holdings
current_eval_amt = current_price * holdings
eval_profit = current_eval_amt - total_purchase_amt
profit_rate = (eval_profit / total_purchase_amt) * 100 if total_purchase_amt > 0 else 0
burn_rate = (one_time_invest / total_seed) * 100 if total_seed > 0 else 0

# --- [핵심 변경 1 적용] 내 계좌 실시간 평가 (화면 최상단 컨테이너에 내용 채우기) ---
with dashboard_container:
    st.title("📊 내 계좌 실시간 평가")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("총 매수금액", f"${total_purchase_amt:,.2f}")
    m2.metric("현재 평가금액", f"${current_eval_amt:,.2f}")
    m3.metric("평가 손익", f"${eval_profit:,.2f}", f"{profit_rate:.2f}%")
    
    # 진행 상황 바
    st.info(f"🔄 현재 진행 상황: 자금 소진율 {burn_rate:.1f}%")
    
    k1, k2, k3 = st.columns(3)
    k1.metric("📌 1회 투자금 한도", f"${one_time_invest:,.0f}")
    k2.metric("💰 남은 총알", f"${total_seed:,.0f}")
    k3.metric("📉 자금 소진율", f"{burn_rate:.1f}%")

# --- 작전 실행 버튼 ---
st.markdown("---")
if st.button("🚀 작전 실행 (계산하기)", type="primary", use_container_width=True):
    
    st.subheader("🔴 매수 작전 (LOC Buy)")
    
    col_def, col_crash = st.columns([1, 1.5])
    
    # 1. 기본 방어 (LOC 평단 매수)
    with col_def:
        st.markdown("### 1️⃣ 기본 방어")
        st.caption("내 평단가 방어용 주문입니다.")
        
        # 평단가 LOC 매수 계산
        def_qty = daily_base_qty
        def_amount = my_avg_price * def_qty
        
        # [핵심 변경 2] 기본 매수도 1회 투자금을 넘는지 체크
        if def_amount > one_time_invest:
            st.warning(f"⚠️ 경고: 기본 매수 금액(${def_amount:.2f})이 1회 투자금(${one_time_invest})을 초과합니다.")
        
        st.success(f"**가격: ${my_avg_price} (LOC)**")
        st.success(f"**수량: {def_qty}주**")
        st.caption("💡 평단 위 대기. 떨어지면 체결")

    # 2. 떡락 대응 (지하실 줍줍)
    with col_crash:
        st.markdown("### 2️⃣ 떡락 대응 (지하실 줍줍)")
        st.caption("혹시 모를 폭락 시, 수량을 늘려 대응합니다. **(1회 투자금 한도 내)**")
        
        drops = [0.10, 0.15, 0.20, 0.30] # 10%, 15%, 20%, 30% 하락
        data = []
        
        for drop in drops:
            target_price = current_price * (1 - drop)
            
            # 하락폭에 따른 추가 매수 수량 로직 (예시: 하락폭 클수록 더 많이)
            if drop == 0.10: add_qty = 1
            elif drop == 0.15: add_qty = 1
            elif drop == 0.20: add_qty = 2
            else: add_qty = 3
            
            planned_qty = daily_base_qty + add_qty
            
            # --- [핵심 변경 2] 1회 투자금 초과 방지 로직 ---
            # 1. 일단 원래 로직대로 예상 금액 계산
            estimated_cost = target_price * planned_qty
            
            # 2. 투자금을 초과한다면?
            final_qty = planned_qty
            note = ""
            
            if estimated_cost > one_time_invest:
                # 투자금 내에서 살 수 있는 최대 수량으로 강제 조정
                max_buyable_qty = int(one_time_invest // target_price)
                
                # 만약 최대 구매 가능 수량이 0개라면 아예 매수 불가
                if max_buyable_qty == 0:
                    final_qty = 0
                    estimated_cost = 0.0
                    note = "🚫 자금 부족"
                else:
                    final_qty = max_buyable_qty
                    estimated_cost = target_price * final_qty
                    note = f"⚠️ 한도 제한 (원래 {planned_qty}주)"
            else:
                # 한도 내라면 원래 계획대로
                note = f"🔥 {planned_qty}주 (평소+{add_qty})"

            # 데이터 추가
            data.append({
                "하락률": f"- {int(drop*100)}% 👇",
                "LOC 매수 가격": f"${target_price:.2f}",
                "주문 수량": note if note.startswith("⚠️") or note.startswith("🚫") else f"{final_qty}주 (평소+{add_qty})",
                "예상 금액": f"${estimated_cost:.1f}"
            })
            
        df = pd.DataFrame(data)
        st.table(df)
        st.caption("※ 모든 주문은 LOC 매수로 걸어야 안전합니다.")
