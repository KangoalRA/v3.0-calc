import streamlit as st
import pandas as pd
import math

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="무한매수법 V3.0 실전 계산기",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 유틸리티 함수 (계산 로직) ---
def roundup(num, decimals=0):
    """엑셀의 ROUNDUP 함수 구현"""
    multiplier = 10 ** decimals
    return math.ceil(num * multiplier) / multiplier

def calculate_t_value(holding_qty, avg_price, one_time_budget):
    """현재 보유 상태를 기반으로 T값 추정 계산"""
    if one_time_budget == 0: return 0
    total_invested = holding_qty * avg_price
    # 엑셀과 동일하게 소수점 둘째자리 올림 처리
    t_val = roundup(total_invested / one_time_budget, 2)
    return t_val

def get_star_percent(ticker_base_star, current_t, divisions):
    """T값에 따른 별% 계산 (V3.0 로직)"""
    half_point = divisions / 2
    if current_t < half_point:
        return ticker_base_star # 전반전: 기본 별% 유지
    else:
        # 후반전: 선형 감소 로직 (T가 분할수 끝에 다다르면 0% 근접)
        decayed_star = ticker_base_star * (1 - (current_t / divisions))
        return max(decayed_star, 0) # 0% 밑으로는 안내려감

def safe_price_cap(calculated_price, current_price):
    """주문 거부 방지: 현재가의 +15%로 가격 제한(MIN 함수)"""
    cap_price = current_price * 1.15
    return min(calculated_price, cap_price)

# --- 사이드바: 기본 설정 (잘 안 바뀌는 값) ---
with st.sidebar:
    st.header("⚙️ 기본 설정 (Settings)")
    st.info("종목별 시작 별%와 자본금을 설정하세요.")
    
    ticker_name = st.text_input("종목명 (예: SOXL)", value="SOXL")
    base_star_percent = st.number_input("시작 별% (예: 20)", min_value=5.0, max_value=30.0, value=20.0, step=1.0, format="%.1f")
    total_capital = st.number_input("총 투자 자본금 ($)", min_value=1000.0, value=10000.0, step=100.0)
    divisions = st.number_input("총 분할 횟수 (예: 40)", min_value=10, max_value=100, value=40, step=10)

    # 1회 매수금 계산
    one_time_budget = total_capital / divisions
    st.divider()
    st.metric(label="💵 1회차 매수 배정금", value=f"${one_time_budget:,.2f}")
    st.caption(f"*총 자본을 {divisions}분할한 금액입니다.")

# --- 메인 화면: 일일 데이터 입력 ---
st.title("📈 무한매수법 V3.0 오늘의 주문표")
st.markdown("매일 장 시작 전, 최신 데이터를 입력하면 주문표가 생성됩니다.")

col1, col2, col3 = st.columns(3)
with col1:
    current_price = st.number_input("① 현재가 (프리장/종가) ($)", min_value=0.01, value=22.00, step=0.1, format="%.2f")
with col2:
    avg_price = st.number_input("② 현재 평균단가 ($)", min_value=0.0, value=0.0, step=0.1, format="%.2f")
with col3:
    holding_qty = st.number_input("③ 현재 보유수량 (개)", min_value=0, value=0, step=1)

st.divider()

# --- 핵심 계산 로직 실행 ---

# 1. 대시보드 계산
if holding_qty > 0 and avg_price > 0:
    current_t = calculate_t_value(holding_qty, avg_price, one_time_budget)
else:
    current_t = 0.0 # 보유량 없으면 T=0

half_point = divisions / 2
status = "전반전 (수량확보)" if current_t < half_point else "후반전 (탈출관리)"
today_star_percent = get_star_percent(base_star_percent, current_t, divisions)

# 2. 대시보드 출력
st.subheader("📊 나의 상태 대시보드")
dash_col1, dash_col2, dash_col3 = st.columns(3)
dash_col1.metric("현재 진행 T값", f"T-{current_t:.2f}", delta=f"반환점: T-{half_point}")
dash_col2.metric("현재 상태", status, delta_color="off")
dash_col3.metric("오늘 적용 별%", f"{today_star_percent:.2f}%")

# --- 주문표 계산 및 생성 ---

if current_price > 0:
    # A. 오늘 매수할 총 수량 계산 (소수점 버림)
    buy_qty_today_total = int(one_time_budget / current_price)
    
    # B. 수량 배분
    star_loc_qty = round(buy_qty_today_total / 2)
    avg_loc_qty = buy_qty_today_total - star_loc_qty
    
    # C. 매수 가격 계산 (안전 캡 적용)
    # 별LOC 가격: 평단 * (1 + 별%) 와 현재가*1.15 중 작은 값
    calc_star_price = avg_price * (1 + today_star_percent / 100)
    final_star_price = safe_price_cap(calc_star_price, current_price) if avg_price > 0 else current_price

    # 평단LOC 가격: 평단 와 현재가*1.15 중 작은 값
    final_avg_price = safe_price_cap(avg_price, current_price) if avg_price > 0 else current_price

    # --- 매수 주문 데이터프레임 생성 ---
    buy_data = [
        ["★LOC 매수 (공격)", f"${final_star_price:,.2f}", f"{star_loc_qty} 개", "LOC"],
        ["평단LOC 매수 (방어)", f"${final_avg_price:,.2f}", f"{avg_loc_qty} 개", "LOC"]
    ]
    
    # 거미줄 매수 추가 (현재가 대비 % 하락)
    spider_drops = [0.10, 0.125, 0.15, 0.175, 0.20] # 10% ~ 20%
    for drop in spider_drops:
        spider_price = current_price * (1 - drop)
        buy_data.append([f"거미줄 매수 (-{drop*100:.1f}%)", f"${spider_price:,.2f}", "1 개", "LOC"])

    buy_df = pd.DataFrame(buy_data, columns=["주문 항목", "주문 가격($)", "주문 수량", "주문 타입"])

    # --- 매도 주문 데이터프레임 생성 ---
    sell_data = []
    
    # 큰수매도 (졸업)
    big_win_price = avg_price * 1.15 if avg_price > 0 else 0
    sell_data.append(["큰수매도 (졸업)", f"${big_win_price:,.2f}", f"{holding_qty} 개 (전량)", "지정가"])
    
    # 쿼터매도 (탈출) - 후반전에만 활성화
    if "후반전" in status and holding_qty > 0:
        quarter_qty = round(holding_qty / 4)
        sell_data.append(["쿼터매도 (탈출)", f"${avg_price:,.2f} (평단)", f"{quarter_qty} 개 (1/4)", "LOC"])
    else:
        sell_data.append(["쿼터매도 (탈출)", "-", "주문 없음 (전반전)", "-"])

    sell_df = pd.DataFrame(sell_data, columns=["주문 항목", "주문 가격($)", "주문 수량", "주문 타입"])

    # --- 최종 주문표 출력 ---
    st.divider()
    st.header("📝 오늘의 최종 주문표 (Order Sheet)")
    
    col_buy, col_sell = st.columns(2)
    
    with col_buy:
        st.subheader("🟢 매수 주문 (Buy)")
        st.dataframe(buy_df, use_container_width=True, hide_index=True)
        st.caption("*LOC 매수는 장 마감 시 유리한 가격으로 체결됩니다.")
        st.caption("*주문 가격은 주문 거부 방지를 위해 현재가의 +15%로 제한됩니다.")
        
    with col_sell:
        st.subheader("🔴 매도 주문 (Sell)")
        st.dataframe(sell_df, use_container_width=True, hide_index=True)
        st.caption("*큰수매도는 지정가, 쿼터매도는 LOC 주문을 권장합니다.")

else:
    st.warning("현재가를 0보다 크게 입력해주세요.")

# --- 정보 표시 ---
with st.sidebar:
    st.divider()
    st.markdown("---")
    st.write("Made with ❤️ by 사용자 & AI Assistant")
    st.caption("Based on Infinite Buying Method V3.0 Logic")
