import streamlit as st
import pandas as pd
import math

# --- [1] 페이지 기본 설정 ---
st.set_page_config(page_title="무매법V3 마스터", page_icon="💰", layout="wide")
st.title("💰 무한매수법 V3.0 작전상황판")

# --- [2] 사이드바: 자금 및 설정 ---
st.sidebar.header("⚙️ 내 자금 설정")
total_capital = st.sidebar.number_input("총 투자원금 ($)", value=10000, step=100)
split_count = st.sidebar.number_input("설정 분할 횟수 (회)", value=40, step=1)

# 1회 투자금 계산 (핵심 기준값)
one_shot_limit = total_capital / split_count if split_count > 0 else 0

st.sidebar.markdown("---")
st.sidebar.header("📂 엑셀 파일 업로드")
uploaded_file = st.sidebar.file_uploader("엑셀(.xlsx)을 올려주세요", type=['xlsx'])

# 변수 초기화
default_avg = 0.0
default_qty = 0

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
                st.sidebar.success(f"✅ 데이터 로드 완료! ({default_qty}주)")
            except:
                st.sidebar.warning("⚠️ 엑셀 데이터 확인 필요")
    except Exception as e:
        st.error(f"엑셀 읽기 실패: {e}")

# =========================================================
# [3] 상단 대시보드 (형님이 원하신 대로 맨 위로 이동!)
# =========================================================

# 나중에 입력을 받아야 채워지므로, 일단 빈 그릇(Container)을 만들어 둡니다.
dashboard_placeholder = st.container()

# =========================================================
# [4] 데이터 입력 (중단)
# =========================================================
st.markdown("### 📝 오늘 데이터 입력")
c1, c2, c3 = st.columns(3)

with c1:
    cur_price = st.number_input("현재가 (프리장/실시간 $)", value=0.0, step=0.01, format="%.2f")
with c2:
    real_avg = st.number_input("내 평단가 ($)", value=default_avg, step=0.01, format="%.2f")
with c3:
    real_qty = st.number_input("보유 수량 (개)", value=default_qty, step=1)

# 매수 수량 자동 계산 (1회차 금액 / 현재가)
calc_buy_qty = 0
if cur_price > 0:
    calc_buy_qty = int(one_shot_limit // cur_price)
    if calc_buy_qty < 1: calc_buy_qty = 1 # 최소 1주는 사야 함

# 수량 입력칸
st.caption(f"💡 1회 투자금(${one_shot_limit:.1f}) 기준, 현재가로 약 {calc_buy_qty}주 매수 가능")
buy_cnt = st.number_input("오늘 기본 매수 수량 (개)", value=calc_buy_qty, step=1)

st.markdown("---")

# =========================================================
# [5] 대시보드 채우기 (입력값 바탕으로 계산 후 위쪽 그릇에 담기)
# =========================================================
with dashboard_placeholder:
    if real_qty > 0 and cur_price > 0:
        total_invested = real_avg * real_qty  # 총 매수금
        total_eval = cur_price * real_qty     # 총 평가금
        profit_loss = total_eval - total_invested # 평가손익
        profit_pct = (profit_loss / total_invested) * 100 # 수익률

        st.subheader("📊 내 계좌 & 자금 현황")
        
        # 1. 계좌 상태 (Red/Blue)
        k1, k2, k3 = st.columns(3)
        k1.metric("총 매수금액", f"${total_invested:,.2f}")
        k2.metric("현재 평가금액", f"${total_eval:,.2f}")
        k3.metric("평가 손익", f"${profit_loss:,.2f}", f"{profit_pct:.2f}%")
        
        # 2. 자금 관리 (진행 상황)
        used_money = real_avg * real_qty
        remain_money = total_capital - used_money
        current_round = used_money / one_shot_limit if one_shot_limit > 0 else 0.0
        progress_pct = (used_money / total_capital) * 100 if total_capital > 0 else 0
        
        # 스타일링 박스
        st.info(f"💾 **현재 진행: {current_round:.1f}회차** (총 {split_count}회 중)")
        
        s1, s2, s3 = st.columns(3)
        s1.metric("💸 1회 투자금 (하루 예산)", f"${one_shot_limit:,.0f}")
        s2.metric("💰 남은 총알", f"${remain_money:,.0f}")
        s3.metric("📈 자금 소진율", f"{progress_pct:.1f}%")
        
        st.divider() # 구분선
    else:
        # 데이터가 없을 때 보이는 안내문
        st.info("👆 아래에 **현재가**와 **평단가**를 입력하면 상단에 계좌 현황이 표시됩니다.")

# =========================================================
# [6] 작전 실행 및 결과표
# =========================================================
if st.button("🚀 작전 실행 (계산하기)", type="primary", use_container_width=True):
    
    loc_buy_price = real_avg if real_avg > 0 else cur_price
    sell_price_10 = real_avg * 1.10
    
    # [A] 매수 작전
    st.header("🔴 매수 작전 (LOC Buy)")
    col_buy1, col_buy2 = st.columns([1, 1.5])
    
    # 1. 기본 매수
    with col_buy1:
        st.subheader("1️⃣ 기본 매수")
        st.write(f"하루 예산(${one_shot_limit:.0f})으로 살 수 있는 최대 수량")
        st.success(f"**가격: ${loc_buy_price:.2f} (LOC)**")
        st.success(f"**수량: {buy_cnt}주**")
        
        if cur_price < real_avg:
             st.caption("📉 현재 평단 아래! 적극 매수")
        else:
             st.caption("🛡️ 평단 위. 떨어지면 체결")

    # 2. 수량별 매수 단가표 (형님이 원하신 기능!)
    with col_buy2:
        st.subheader("2️⃣ 떡락 대응 (수량 늘리기)")
        st.write(f"하루 예산 **${one_shot_limit:.0f}**로 N주를 사려면 얼마까지 떨어져야 할까?")
        
        # 표 데이터 생성 로직
        # 현재 살 수 있는 수량(buy_cnt)부터 +5개까지 보여줌
        table_data = []
        
        start_qty = buy_cnt + 1 # 현재 1주 살 수 있으면 2주부터 계산
        end_qty = start_qty + 4 # 5단계 보여줌
        
        for q in range(start_qty, end_qty + 1):
            # 핵심 공식: 1회 투자금 / 목표 수량 = 필요한 가격
            target_price = one_shot_limit / q
            
            # 하락률 계산 (현재가 대비 얼마나 빠져야 하는지)
            if cur_price > 0:
                drop_needed = ((target_price - cur_price) / cur_price) * 100
            else:
                drop_needed = 0
            
            # 만약 타겟 가격이 현재가보다 낮을 때만 의미 있음 (당연하지만)
            if target_price < cur_price:
                table_data.append({
                    "목표 수량": f"🔥 {q}주",
                    "필요 주가": f"${target_price:.2f}",
                    "현재가 대비": f"{drop_needed:.1f}% 👇",
                    "총 주문금액": f"${target_price * q:.1f}" # 검산용 (거의 1회 투자금과 같음)
                })
        
        if table_data:
            st.dataframe(pd.DataFrame(table_data), hide_index=True, use_container_width=True)
            st.caption(f"※ 주가가 위 가격까지 떨어지면, 같은 돈(${one_shot_limit:.0f})으로 더 많이(N주) 살 수 있습니다.")
        else:
            st.write("이미 주가가 충분히 낮아서 현재 예산으로도 많이 살 수 있습니다!")

    st.markdown("---")

    # [B] 매도 작전
    st.header("🔵 매도 작전 (LOC Sell)")
    
    qty_all = real_qty
    qty_half = math.floor(real_qty * 0.5)
    
    st.info(f"**목표가(10%): ${sell_price_10:.2f} (LOC)**")
    c1, c2 = st.columns(2)
    c1.metric("전량 매도(100%)", f"+ ${(sell_price_10 - real_avg)*qty_all:.2f} 수익")
    c2.metric("절반 매도(50%)", f"+ ${(sell_price_10 - real_avg)*qty_half:.2f} 수익")
