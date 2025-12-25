import streamlit as st
import pandas as pd

# 1. 페이지 설정 (넓은 레이아웃)
st.set_page_config(page_title="무한매수법 대시보드", layout="wide")

# ==========================================
# [LEFT] 사이드바: 데이터 입력 공간
# ==========================================
with st.sidebar:
    st.header("📝 데이터 입력")
    st.caption("매일 변동되는 데이터를 이곳에 입력하세요.")
    
    st.divider()
    
    # 1. 가격 정보
    st.subheader("1. 가격 정보")
    current_price = st.number_input("현재가 (프리장/실시간 $)", value=55.36, step=0.01, format="%.2f")
    my_avg_price = st.number_input("내 평단가 ($)", value=54.20, step=0.01, format="%.2f")
    
    st.divider()

    # 2. 자산 정보
    st.subheader("2. 내 자산 정보")
    holdings = st.number_input("보유 수량 (개)", value=1, step=1)
    total_seed = st.number_input("남은 총알 (예수금 $)", value=3646.0, step=10.0)
    
    st.divider()

    # 3. 설정 정보
    st.subheader("3. 매수 설정")
    daily_base_qty = st.number_input("오늘 기본 매수 수량 (개)", value=1, step=1)
    one_time_invest = st.number_input("1회 투자금 ($)", value=74.0, step=1.0, help="한 번 매수 시 사용할 최대 금액")
    
    st.markdown("---")
    st.caption("Created with Streamlit")

# ==========================================
# [RIGHT] 메인 화면: 대시보드 및 계산 결과
# ==========================================

# --- 계산 로직 ---
total_purchase_amt = my_avg_price * holdings
current_eval_amt = current_price * holdings
eval_profit = current_eval_amt - total_purchase_amt
profit_rate = (eval_profit / total_purchase_amt) * 100 if total_purchase_amt > 0 else 0
burn_rate = (one_time_invest / total_seed) * 100 if total_seed > 0 else 0

# 1. 내 계좌 실시간 평가 (가장 위)
st.title("📊 내 계좌 실시간 평가")

# 메트릭 카드 배치
col1, col2, col3 = st.columns(3)
col1.metric("총 매수금액", f"${total_purchase_amt:,.2f}")
col2.metric("현재 평가금액", f"${current_eval_amt:,.2f}")
col3.metric("평가 손익", f"${eval_profit:,.2f}", f"{profit_rate:.2f}%")

# 진행 상황 바
st.info(f"🔄 현재 진행 상황: 자금 소진율 {burn_rate:.1f}%")

# 세부 정보 (작게 표시)
k1, k2, k3 = st.columns(3)
k1.metric("📌 1회 투자금 한도", f"${one_time_invest:,.0f}")
k2.metric("💰 남은 총알", f"${total_seed:,.0f}")
k3.metric("📉 자금 소진율", f"{burn_rate:.1f}%")

st.divider()

# 2. 작전 실행 버튼 및 결과
if st.button("🚀 작전 실행 (계산하기)", type="primary", use_container_width=True):
    
    st.subheader("🔴 매수 작전 (LOC Buy)")
    
    # 결과 화면도 좌우로 나누어 보기 좋게 배치
    col_def, col_crash = st.columns([1, 1.5])
    
    # [왼쪽] 기본 방어
    with col_def:
        container = st.container(border=True) # 테두리 추가
        container.markdown("### 🛡️ 기본 방어")
        container.caption("내 평단가 방어용 주문")
        
        def_qty = daily_base_qty
        def_amount = my_avg_price * def_qty
        
        # 1회 투자금 초과 체크
        if def_amount > one_time_invest:
            container.warning(f"⚠️ 금액 초과: ${def_amount:.2f}")
        
        container.success(f"**가격: ${my_avg_price}**")
        container.success(f"**수량: {def_qty}주**")
        container.markdown(f"예상 금액: **${def_amount:.2f}**")

    # [오른쪽] 떡락 대응
    with col_crash:
        st.markdown("### 📉 떡락 대응 (지하실 줍줍)")
        st.caption("폭락 시 대응 (1회 투자금 한도 자동 적용)")
        
        drops = [0.10, 0.15, 0.20, 0.30]
        data = []
        
        for drop in drops:
            target_price = current_price * (1 - drop)
            
            # 수량 로직
            if drop == 0.10: add_qty = 1
            elif drop == 0.15: add_qty = 1
            elif drop == 0.20: add_qty = 2
            else: add_qty = 3
            
            planned_qty = daily_base_qty + add_qty
            
            # --- [핵심] 1회 투자금 캡(Cap) 로직 ---
            estimated_cost = target_price * planned_qty
            
            final_qty = planned_qty
            note = ""
            
            if estimated_cost > one_time_invest:
                # 돈이 모자르면 살 수 있는 만큼만 계산
                max_buyable_qty = int(one_time_invest // target_price)
                
                if max_buyable_qty == 0:
                    final_qty = 0
                    estimated_cost = 0.0
                    note = "🚫 자금 부족"
                else:
                    final_qty = max_buyable_qty
                    estimated_cost = target_price * final_qty
                    note = f"⚠️ 한도 제한 ({planned_qty}→{final_qty}주)"
            else:
                note = f"🔥 {planned_qty}주 (평소+{add_qty})"

            data.append({
                "하락률": f"- {int(drop*100)}%",
                "매수 가격 (LOC)": f"${target_price:.2f}",
                "주문 수량": note,
                "예상 금액": f"${estimated_cost:.1f}"
            })
            
        df = pd.DataFrame(data)
        st.table(df)
