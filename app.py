import streamlit as st
import pandas as pd
import math

# --- [1] 페이지 기본 설정 ---
st.set_page_config(page_title="무매법V3 마스터", page_icon="💰", layout="wide")
st.title("💰 무한매수법 V3.0 작전상황판")

# --- [2] 사이드바: 자금 및 전략 설정 ---
st.sidebar.header("⚙️ 내 자금 설정")
total_capital = st.sidebar.number_input("총 투자원금 ($)", value=3700, step=100)
split_count = st.sidebar.number_input("설정 분할 횟수 (회)", value=40, step=1)

st.sidebar.markdown("---")
st.sidebar.header("📉 떡락 대응(물타기) 강도")
# 하락 시 수량을 얼마나 공격적으로 늘릴지 결정 (1: 기본, 3: 아주 공격적)
panic_step = st.sidebar.slider("물타기 강도 (Step)", 1, 3, 1, help="하락폭이 커질 때 수량을 얼마나 더 늘릴지 결정합니다.")

st.sidebar.markdown("---")
st.sidebar.header("📂 엑셀 파일 업로드")
uploaded_file = st.sidebar.file_uploader("엑셀(.xlsx)을 올려주세요", type=['xlsx'])

# 변수 초기화
default_avg = 0.0
default_qty = 0
one_shot_limit = total_capital / split_count if split_count > 0 else 0

# 엑셀 읽기 로직
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
                st.sidebar.warning("⚠️ 엑셀에서 평단/수량을 못 찾았습니다.")
    except Exception as e:
        st.error(f"엑셀 읽기 실패: {e}")

# --- [3] 메인 입력 화면 ---
st.subheader("📝 오늘 데이터 입력")
c1, c2, c3 = st.columns(3)

with c1:
    cur_price = st.number_input("현재가 (프리장/실시간 $)", value=0.0, step=0.01, format="%.2f")
with c2:
    real_avg = st.number_input("내 평단가 ($)", value=default_avg, step=0.01, format="%.2f")
with c3:
    real_qty = st.number_input("보유 수량 (개)", value=default_qty, step=1)

# 매수 수량 자동 계산 (1회차 금액 기준)
calc_buy_qty = 1
if cur_price > 0:
    calc_buy_qty = int(one_shot_limit // cur_price)
    if calc_buy_qty < 1: calc_buy_qty = 1

# 수량 입력칸은 별도로 아래 배치
buy_cnt = st.number_input("오늘 기본 매수 수량 (개)", value=calc_buy_qty, step=1, help="1회 투자금에 맞춰 자동 계산된 수량입니다.")

st.markdown("---")

# --- [4] 계좌 현황판 (Red/Blue) ---
# 수량이 있을 때만 보여줌
if real_qty > 0 and cur_price > 0:
    total_invested = real_avg * real_qty  # 총 매수금
    total_eval = cur_price * real_qty     # 총 평가금
    profit_loss = total_eval - total_invested # 평가손익($)
    profit_pct = (profit_loss / total_invested) * 100 # 수익률(%)

    st.subheader("📊 내 계좌 실시간 평가")
    
    # 3단 컬럼으로 보기 좋게 배치
    k1, k2, k3 = st.columns(3)
    k1.metric("총 매수금액", f"${total_invested:,.2f}")
    k2.metric("현재 평가금액", f"${total_eval:,.2f}")
    
    # 수익이면 빨강, 손실이면 파랑 (한국 주식 스타일)
    # delta_color="inverse"를 쓰면 한국식(빨강=상승)과 비슷하게 맞출 수 있음
    k3.metric("평가 손익", f"${profit_loss:,.2f}", f"{profit_pct:.2f}%")
    
    st.divider()

# --- [5] 자금 관리 현황 (회차 표시) ---
status_container = st.container()
with status_container:
    used_money = real_avg * real_qty
    remain_money = total_capital - used_money
    
    # 현재 회차 계산 (수량이 0이면 0회차로 리셋)
    current_round = used_money / one_shot_limit if (one_shot_limit > 0 and real_qty > 0) else 0.0
    progress_pct = (used_money / total_capital) * 100 if total_capital > 0 else 0
    
    # 깔끔한 정보 박스
    st.info(f"🔄 **현재 진행 상황: {current_round:.1f}회차** (총 {split_count}회 중)")
    
    s1, s2, s3 = st.columns(3)
    s1.metric("💸 1회 투자금", f"${one_shot_limit:.0f}")
    s2.metric("💰 남은 총알", f"${remain_money:,.0f}")
    s3.metric("📈 자금 소진율", f"{progress_pct:.1f}%")

# --- [6] 매매 전략 계산 버튼 ---
st.markdown("###") # 여백
if st.button("🚀 작전 실행 (계산하기)", type="primary", use_container_width=True):
    st.markdown("---")
    
    loc_buy_price = real_avg if real_avg > 0 else cur_price
    sell_price_10 = real_avg * 1.10
    sell_price_5 = real_avg * 1.05
    
    # [A] 매수 작전 (Buy)
    st.header("🔴 매수 작전 (LOC Buy)")
    
    col_buy1, col_buy2 = st.columns([1, 1.5]) # 비율 1:1.5
    
    # 1. 기본 매수
    with col_buy1:
        st.subheader("1️⃣ 기본 방어")
        st.write("내 평단가 방어용 주문입니다.")
        st.success(f"**가격: ${loc_buy_price:.2f} (LOC)**")
        st.success(f"**수량: {buy_cnt}주**")
        
        if cur_price < real_avg:
             st.caption("📉 현재 평단 아래! 적극 매수 구간")
        else:
             st.caption("🛡️ 평단 위 대기. 떨어지면 체결")

    # 2. 떡락 대응 (표)
    with col_buy2:
        st.subheader("2️⃣ 떡락 대응 (지하실 줍줍)")
        st.write("혹시 모를 폭락 시, **자동으로 수량을 늘려** 대응합니다.")
        
        # 표 데이터 생성
        drop_scenarios = [10, 15, 20, 30] # 하락률 %
        table_data = []
        
        for drop in drop_scenarios:
            target_price = real_avg * (1 - drop/100) # 목표 가격
            
            # 물타기 수량 공식: 기본수량 + (하락률/10 * 강도)
            # 예: 20% 하락, 강도1 -> 2주 추가
            add_qty = int((drop / 10) * panic_step)
            final_qty = buy_cnt + add_qty
            
            table_data.append({
                "하락률": f"- {drop}% 👇",
                "LOC 매수 가격": f"${target_price:.2f}",
                "주문 수량": f"🔥 {final_qty}주 (평소+{add_qty})",
                "예상 금액": f"${target_price * final_qty:.1f}"
            })
            
        st.dataframe(pd.DataFrame(table_data), hide_index=True, use_container_width=True)
        st.caption(f"※ 모든 주문은 **LOC 매수**로 걸어야 안전합니다.")

    st.markdown("---")

    # [B] 매도 작전 (Sell)
    st.header("🔵 매도 작전 (LOC Sell)")
    
    tab1, tab2, tab3 = st.tabs(["💰 10% 익절 (정석)", "💵 5% 반익절 (옵션)", "📋 전체 매도표"])
    
    qty_all = real_qty
    qty_half = math.floor(real_qty * 0.5)
    qty_quarter = math.floor(real_qty * 0.25)
    
    with tab1:
        st.info(f"**목표가: ${sell_price_10:.2f} (LOC)**")
        c1, c2 = st.columns(2)
        c1.metric("전량 매도(100%)", f"+ ${(sell_price_10 - real_avg)*qty_all:.2f} 이익")
        c2.metric("절반 매도(50%)", f"+ ${(sell_price_10 - real_avg)*qty_half:.2f} 이익")
        
    with tab2:
        st.warning(f"**반익절가: ${sell_price_5:.2f} (LOC)**")
        st.write("장이 불안할 때 챙기는 구간입니다.")
        c3, c4 = st.columns(2)
        c3.metric("절반 매도(50%)", f"{qty_half}주")
        c4.metric("쿼터 매도(25%)", f"{qty_quarter}주")
        
    with tab3:
        # 통합 테이블
        data = {
            "구분": ["전량(100%)", "절반(50%)", "쿼터(25%)"],
            "10% 가격": [f"${sell_price_10:.2f}"] * 3,
            "10% 수량": [f"{qty_all}주", f"{qty_half}주", f"{qty_quarter}주"],
            "5% 가격": [f"${sell_price_5:.2f}"] * 3,
            "5% 수량": [f"{qty_all}주", f"{qty_half}주", f"{qty_quarter}주"],
        }
        st.table(pd.DataFrame(data))
