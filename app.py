import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="무한매수법 대시보드", layout="wide")

# ==========================================
# [LEFT] 사이드바: 고정 설정 (한 번만 세팅)
# ==========================================
with st.sidebar:
    st.header("⚙️ 초기 설정")
    st.info("이 종목에 대한 원칙을 설정합니다.")
    
    # 1. 총 투자 원금
    total_principal = st.number_input(
        "총 투자 원금 ($)", 
        value=4000.0, 
        step=100.0, 
        help="이 종목에 할당한 전체 시드머니"
    )
    
    # 2. 분할 횟수
    split_count = st.number_input(
        "분할 횟수 (회)", 
        value=50, 
        step=1, 
        help="보통 40분할 또는 50분할을 사용합니다."
    )
    
    st.divider()
    
    # [자동 계산 1] 1회 투자금 한도
    if split_count > 0:
        one_time_limit = total_principal / split_count
    else:
        one_time_limit = 0
        
    st.metric(label="1회 투자금 한도 (자동)", value=f"${one_time_limit:,.2f}")
    st.caption(f"💡 ${total_principal:,.0f} ÷ {split_count}회")

# ==========================================
# [MAIN] 메인 화면
# ==========================================

# 1. 상단 대시보드 (자리 확보)
dashboard_container = st.container()

st.divider()

# 2. 오늘 데이터 입력 (최소화됨)
st.subheader("📝 오늘 데이터 입력 (3가지만 입력하세요)")

c1, c2, c3 = st.columns(3)
with c1:
    current_price = st.number_input("① 현재가 (실시간 $)", value=55.36, step=0.01, format="%.2f")
with c2:
    my_avg_price = st.number_input("② 내 평단가 ($)", value=54.20, step=0.01, format="%.2f")
with c3:
    holdings = st.number_input("③ 보유 수량 (개)", value=1, step=1)

# --- [핵심] 자동 계산 로직 ---

# A. 자산 현황 역산
total_purchase_amt = my_avg_price * holdings  # 현재 매수된 총 금액
remaining_cash = total_principal - total_purchase_amt # 남은 총알 (원금 - 매수금액)

# B. 평가 금액 계산
current_eval_amt = current_price * holdings
eval_profit = current_eval_amt - total_purchase_amt
profit_rate = (eval_profit / total_purchase_amt) * 100 if total_purchase_amt > 0 else 0

# C. [자동 계산] 오늘 기본 매수 수량 (Daily Base Qty)
# 공식: 1회 투자금 한도 / 현재가 (소수점 버림)
if current_price > 0:
    daily_base_qty = int(one_time_limit // current_price)
else:
    daily_base_qty = 0

# D. 진행률 (횟수 기준)
used_count_approx = total_purchase_amt / one_time_limit if one_time_limit > 0 else 0
burn_rate = (total_purchase_amt / total_principal) * 100 if total_principal > 0 else 0


# 3. [상단 채우기] 내 계좌 실시간 평가
with dashboard_container:
    st.title("📊 내 계좌 실시간 평가")
    
    # 주요 지표
    m1, m2, m3 = st.columns(3)
    m1.metric("총 매수금액", f"${total_purchase_amt:,.2f}")
    m2.metric("현재 평가금액", f"${current_eval_amt:,.2f}")
    m3.metric("평가 손익", f"${eval_profit:,.2f}", f"{profit_rate:.2f}%")
    
    # 자동 계산된 정보 표시줄
    st.info(f"💰 남은 총알: **${remaining_cash:,.2f}** (자금 소진율 {burn_rate:.1f}%)")
    
    # 상세 정보
    k1, k2, k3 = st.columns(3)
    k1.metric("1회 투자 한도", f"${one_time_limit:,.2f}")
    k2.metric("오늘 기본 매수 수량 (자동)", f"{daily_base_qty} 주", help="1회 한도 내에서 현재가로 살 수 있는 최대 수량")
    k3.metric("진행 회차 (추정)", f"{used_count_approx:.1f} / {split_count} 회")


# 4. 작전 실행 (버튼 클릭 시 자동 계산된 수량 반영)
st.markdown("---")
if st.button("🚀 작전 실행 (계산하기)", type="primary", use_container_width=True):
    
    st.subheader("🔴 매수 작전 (LOC Buy)")
    
    col_def, col_crash = st.columns([1, 1.5])
    
    # [왼쪽] 기본 방어 (평단가 매수)
    with col_def:
        st.markdown("### 🛡️ 기본 방어")
        st.caption("내 평단가보다 낮을 때 매수")
        
        # 자동 계산된 daily_base_qty 사용
        def_amount = my_avg_price * daily_base_qty
        
        if daily_base_qty == 0:
            st.error("⚠️ 현재가가 1회 투자금보다 비싸서 매수할 수 없습니다.")
        else:
            # 기본 매수도 1회 한도를 넘는지 체크 (평단 > 현재가 일 수 있으므로)
            if def_amount > one_time_limit:
                st.warning(f"⚠️ 한도 초과 (${def_amount:.2f}). 수량 조절이 필요할 수 있습니다.")
            
            st.success(f"**가격: ${my_avg_price}**")
            st.success(f"**수량: {daily_base_qty}주** (자동계산)")
            st.caption(f"예상 금액: ${def_amount:.2f}")

    # [오른쪽] 떡락 대응
    with col_crash:
        st.markdown("### 📉 떡락 대응 (지하실 줍줍)")
        st.caption(f"1회 한도 **${one_time_limit:.0f}** 내에서 자동 수량 조절")
        
        drops = [0.10, 0.15, 0.20, 0.30]
        data = []
        
        for drop in drops:
            target_price = current_price * (1 - drop)
            
            # 수량 가중치 (하락폭 클수록 +1, +2, +3)
            if drop == 0.10: add_qty = 1
            elif drop == 0.15: add_qty = 1
            elif drop == 0.20: add_qty = 2
            else: add_qty = 3
            
            # 계획 수량 = (자동 계산된 기본 수량) + (추가 수량)
            planned_qty = daily_base_qty + add_qty
            estimated_cost = target_price * planned_qty
            
            # --- [한도 컷 로직] ---
            final_qty = planned_qty
            note = ""
            
            if estimated_cost > one_time_limit:
                # 돈 부족 시 수량 깎기
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
