import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="무한매수법 대시보드", layout="wide")

# ==========================================
# [LEFT] 사이드바: 고정 설정 (원금 & 분할)
# ==========================================
with st.sidebar:
    st.header("⚙️ 초기 설정")
    st.info("투자 원칙을 이곳에 설정하세요.")
    
    # 1. 총 투자 원금 입력
    total_principal = st.number_input(
        "총 투자 원금 ($)", 
        value=4000.0, 
        step=100.0, 
        help="이 종목에 할당한 전체 시드머니"
    )
    
    # 2. 분할 횟수 입력
    split_count = st.number_input(
        "분할 횟수 (회)", 
        value=50, 
        step=1, 
        help="총 몇 번에 나누어 살 것인가?"
    )
    
    st.divider()
    
    # [자동 계산] 1회 투자금 한도
    if split_count > 0:
        one_time_limit = total_principal / split_count
    else:
        one_time_limit = 0
        
    st.metric(label="1회 투자금 한도 (자동계산)", value=f"${one_time_limit:,.2f}")
    st.caption(f"💡 ${total_principal:,.0f} ÷ {split_count}회 = ${one_time_limit:,.2f}")

# ==========================================
# [MAIN] 메인 화면
# ==========================================

# 1. 상단 대시보드 (자리를 먼저 잡아둠)
dashboard_container = st.container()

st.divider()

# 2. 오늘 데이터 입력 (화면 중앙)
st.subheader("📝 오늘 데이터 입력")

# 첫 번째 줄: 가격 정보
c1, c2, c3 = st.columns(3)
with c1:
    current_price = st.number_input("현재가 (실시간 $)", value=55.36, step=0.01, format="%.2f")
with c2:
    my_avg_price = st.number_input("내 평단가 ($)", value=54.20, step=0.01, format="%.2f")
with c3:
    holdings = st.number_input("보유 수량 (개)", value=1, step=1)

# 두 번째 줄: 자산 및 매수 설정
c4, c5 = st.columns(2)
with c4:
    current_cash = st.number_input("남은 총알 (현재 예수금 $)", value=3646.0, step=10.0)
with c5:
    daily_base_qty = st.number_input("오늘 기본 매수 수량 (개)", value=1, step=1)

# --- 계산 로직 (메인 화면용) ---
total_purchase_amt = my_avg_price * holdings # 총 매수금액
current_eval_amt = current_price * holdings  # 현재 평가금액
eval_profit = current_eval_amt - total_purchase_amt # 평가손익
profit_rate = (eval_profit / total_purchase_amt) * 100 if total_purchase_amt > 0 else 0

# 자금 소진율 계산 (남은 총알 역산)
# 현재 사용한 돈 = 원금 - 남은 돈 (단, 정확한 기록을 위해선 별도 관리가 필요하지만 여기선 약식 계산)
used_capital = total_principal - current_cash
burn_rate = (used_capital / total_principal) * 100 if total_principal > 0 else 0


# 3. [상단 채우기] 내 계좌 실시간 평가
with dashboard_container:
    st.title("📊 내 계좌 실시간 평가")
    
    # 주요 지표 3개
    m1, m2, m3 = st.columns(3)
    m1.metric("총 매수금액", f"${total_purchase_amt:,.2f}")
    m2.metric("현재 평가금액", f"${current_eval_amt:,.2f}")
    m3.metric("평가 손익", f"${eval_profit:,.2f}", f"{profit_rate:.2f}%")
    
    # 진행 상황 (Progress Bar 느낌)
    st.info(f"⏳ 진행 상황: {split_count}회 중 약 {used_capital / one_time_limit:.1f}회분 소진 (자금 소진율 {burn_rate:.1f}%)")
    
    # 보조 지표
    k1, k2, k3 = st.columns(3)
    k1.metric("1회 한도", f"${one_time_limit:,.0f}")
    k2.metric("남은 총알", f"${current_cash:,.0f}")
    k3.metric("남은 횟수 (추정)", f"약 {int(current_cash // one_time_limit)}회")


# 4. 작전 실행 (하단)
st.markdown("---")
if st.button("🚀 작전 실행 (계산하기)", type="primary", use_container_width=True):
    
    st.subheader("🔴 매수 작전 (LOC Buy)")
    
    col_def, col_crash = st.columns([1, 1.5])
    
    # [왼쪽] 기본 방어
    with col_def:
        st.markdown("### 🛡️ 기본 방어")
        st.caption("내 평단가보다 낮을 때 매수")
        
        def_qty = daily_base_qty
        def_amount = my_avg_price * def_qty
        
        note_def = ""
        final_def_qty = def_qty
        
        # 1회 한도 초과 체크
        if def_amount > one_time_limit:
            st.warning(f"⚠️ 한도 초과: ${def_amount:.2f} > ${one_time_limit:.2f}")
            # 한도 내 최대 수량 재계산 (옵션)
            max_qty = int(one_time_limit // my_avg_price)
            if max_qty < def_qty:
                st.error(f"조정 제안: {max_qty}주 (한도 내)")
        
        st.success(f"**가격: ${my_avg_price}**")
        st.success(f"**수량: {def_qty}주**")
        st.caption(f"예상 금액: ${def_amount:.2f}")

    # [오른쪽] 떡락 대응
    with col_crash:
        st.markdown("### 📉 떡락 대응 (지하실 줍줍)")
        st.caption(f"한도 **${one_time_limit:.0f}** 내에서 수량 자동 조절")
        
        drops = [0.10, 0.15, 0.20, 0.30]
        data = []
        
        for drop in drops:
            target_price = current_price * (1 - drop)
            
            # 수량 설정 (기존 로직)
            if drop == 0.10: add_qty = 1
            elif drop == 0.15: add_qty = 1
            elif drop == 0.20: add_qty = 2
            else: add_qty = 3
            
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
                note = f"🔥 {planned_qty}주 (평소+{add_qty})"
                
            data.append({
                "하락률": f"- {int(drop*100)}%",
                "LOC 매수 가격": f"${target_price:.2f}",
                "주문 수량": note,
                "예상 금액": f"${estimated_cost:.1f}"
            })
            
        df = pd.DataFrame(data)
        st.table(df)
