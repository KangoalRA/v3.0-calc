import streamlit as st
import pandas as pd

st.set_page_config(page_title="무매법V3 계산기", page_icon="📈")
st.title("📈 무한매수법 V3.0 도우미")

# 사이드바: 파일 업로드
st.sidebar.header("📂 엑셀 파일 업로드")
uploaded_file = st.sidebar.file_uploader("엑셀(.xlsx)을 올려주세요", type=['xlsx'])

# 기본 변수
my_avg = 0.0
my_qty = 0

if uploaded_file:
    try:
        # 핵심: 1~3행 무시하고 4행부터 읽기 (header=3)
        df = pd.read_excel(uploaded_file, header=3)
        df = df.dropna(subset=['날짜']) # 날짜 빈칸 제거
        
        if not df.empty:
            last_row = df.iloc[-1] # 마지막 줄
            # 컬럼명 자동 탐색 (형님 시트 기준)
            try:
                # 엑셀의 정확한 컬럼명을 찾아야 함 (보통 평균단가, 보유수량)
                my_avg = float(last_row.get('평균단가', last_row.get('평단가', 0)))
                my_qty = int(last_row.get('보유수량', last_row.get('수량', 0)))
                st.sidebar.success(f"✅ 데이터 로드 완료! (평단: ${my_avg})")
            except:
                st.sidebar.warning("⚠️ 데이터를 못 찾았습니다. 직접 입력해주세요.")
    except Exception as e:
        st.error(f"엑셀 읽기 실패: {e}")

# 메인 입력
st.subheader("📝 오늘 데이터 입력")
c1, c2 = st.columns(2)
with c1:
    cur_price = st.number_input("현재가 (어제 종가 $)", value=0.0, step=0.01, format="%.2f")
    avg_price = st.number_input("내 평단가 ($)", value=my_avg, step=0.01, format="%.2f")
with c2:
    qty = st.number_input("보유 수량 (개)", value=my_qty, step=1)
    buy_cnt = st.number_input("매수 할 수량 (개)", value=1, step=1)

# 계산 결과
if st.button("🚀 계산하기", type="primary"):
    st.markdown("---")
    # V3 공식: LOC매수(평단가 or 현재가), LOC매도(평단*1.1)
    loc_buy = avg_price if avg_price > 0 else cur_price
    loc_sell = avg_price * 1.1
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.info("🔴 **LOC 매수**")
        st.metric("가격", f"${loc_buy:.2f}")
        st.write(f"👉 **{buy_cnt}주** 매수 주문")
    with col_b:
        st.success("🔵 **LOC 매도 (큰매도)**")
        st.metric("가격", f"${loc_sell:.2f}")
        st.write(f"👉 **{qty}주 (전량)** 매도 주문")
