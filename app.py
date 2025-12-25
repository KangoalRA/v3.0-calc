import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="무매법V3 도우미", page_icon="💰")
st.title("💰 무한매수법 V3.0 대시보드")

# --- [1] 사이드바: 기본 설정 ---
st.sidebar.header("⚙️ 기본 설정")
total_capital = st.sidebar.number_input("총 투자원금 ($)", value=3700, step=100)
split_count = st.sidebar.number_input("설정 분할 횟수 (회)", value=40, step=1)

st.sidebar.markdown("---")
st.sidebar.header("📂 엑셀 파일 업로드")
uploaded_file = st.sidebar.file_uploader("엑셀(.xlsx)을 올려주세요", type=['xlsx'])

# 변수 초기화
default_avg = 0.0
default_qty = 0
one_shot_limit = total_capital / split_count if split_count > 0 else 0

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
                st.sidebar.warning("⚠️ 평단가/수량을 못 찾았습니다.")
    except Exception as e:
        st.error(f"엑셀 읽기 실패: {e}")

# --- [2] 현황판 (실시간) ---
status_container = st.container()

# --- [3] 데이터 입력 ---
st.subheader("📝 오늘 데이터 입력")
c1, c2 = st.columns(2)
with c1:
    cur_price = st.number_input("현재가 (프리장/실시간 $)", value=0.0, step=0.01, format="%.2f")
    real_avg = st.number_input("내 평단가 ($)", value=default_avg, step=0.01, format="%.2f")
with c2:
    real_qty = st.number_input("보유 수량 (개)", value=default_qty, step=1)
    
    # 매수 수량 자동 계산
    calc_buy_qty = 1
    if cur_price > 0:
        calc_buy_qty = int(one_shot_limit // cur_price)
        if calc_buy_qty < 1: calc_buy_qty = 1
    buy_cnt = st.number_input("매수 할 수량 (개)", value=calc_buy_qty, step=1)

# --- [4] 현황판 로직 ---
with status_container:
    used_money = real_avg * real_qty
    remain_money = total_capital - used_money
    current_round = used_money / one_shot_limit if one_shot_limit > 0 else 0
    progress_pct = (used_money / total_capital) * 100 if total_capital > 0 else 0
    
    st.subheader("📊 나의 자금 현황")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("1회차 금액", f"${one_shot_limit:.0f}")
    m2.metric("현재 진행", f"{current_round:.1f}회차", f"총 {split_count}회")
    m3.metric("남은 총알", f"${remain_money:,.0f}")
    m4.metric("진행률", f"{progress_pct:.1f}%")
    st.divider()

# --- [5] 결과 및 상세 매매 작전판 ---
if st.button("🚀 계산하기", type="primary"):
    st.markdown("---")
    
    # 가격 계산
    loc_buy_price = real_avg if real_avg > 0 else cur_price
    sell_price_10 = real_avg * 1.10  # 10% 수익
    sell_price_5 = real_avg * 1.05   # 5% 수익
    
    # 수량 계산 (소수점 버림)
    qty_quarter = math.floor(real_qty * 0.25) # 쿼터(1/4)
    qty_half = math.floor(real_qty * 0.5)     # 반(1/2)
    qty_all = real_qty                        # 전량
    
    # 1. 매수 섹션
    st.subheader("🔴 매수 전략 (Buy)")
    b1, b2 = st.columns(2)
    with b1:
        st.info(f"**기본 LOC 매수**")
        st.write(f"가격: **${loc_buy_price:.2f}**")
        st.write(f"수량: **{buy_cnt}주**")
    with b2:
        # 하락장 대비 (평단보다 낮을 때)
        if cur_price < real_avg:
            st.warning(f"📉 **현재가가 평단보다 낮습니다!**")
            st.write("규칙대로 정량 매수 진행")
        else:
            st.write("평단 이하 매수 대기 중...")

    st.markdown("---")

    # 2. 매도 섹션 (형님이 원하신 쿼터/반/전량!)
    st.subheader("🔵 매도 전략 (Sell Options)")
    
    # 탭으로 깔끔하게 정리
    tab1, tab2, tab3 = st.tabs(["💰 10% (전량/반)", "💵 5% (쿼터/반)", "📋 전체 보기"])
    
    with tab1:
        st.success(f"**목표 수익 10% 도달 시 (가격: ${sell_price_10:.2f})**")
        c_sell1, c_sell2 = st.columns(2)
        c_sell1.metric("전량 매도(100%)", f"{qty_all}주", f"+${(sell_price_10 - real_avg)*qty_all:.2f} 이익")
        c_sell2.metric("절반 매도(50%)", f"{qty_half}주", f"+${(sell_price_10 - real_avg)*qty_half:.2f} 이익")
        
    with tab2:
        st.warning(f"**중간 수익 5% 도달 시 (가격: ${sell_price_5:.2f})**")
        c_sell3, c_sell4 = st.columns(2)
        c_sell3.metric("절반 매도(50%)", f"{qty_half}주")
        c_sell4.metric("쿼터 매도(25%)", f"{qty_quarter}주")
        
    with tab3:
        # 표로 한눈에 보기
        data = {
            "구분": ["전량(100%)", "반(50%)", "쿼터(25%)"],
            "10% 수익 가격": [f"${sell_price_10:.2f}"] * 3,
            "10% 매도 수량": [f"{qty_all}주", f"{qty_half}주", f"{qty_quarter}주"],
            "5% 수익 가격": [f"${sell_price_5:.2f}"] * 3,
            "5% 매도 수량": [f"{qty_all}주", f"{qty_half}주", f"{qty_quarter}주"],
        }
        st.table(pd.DataFrame(data))

    if real_qty < 4:
        st.caption("※ 보유 수량이 4주 미만이라 쿼터/반 계산이 0으로 보일 수 있습니다. (정상입니다)")
