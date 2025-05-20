import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(layout="wide")

st.title("글로벌 시가총액 TOP 10 기업의 1년 주가 변화")
st.markdown("Yahoo Finance 데이터를 기반으로 주요 기업들의 최근 1년간 주가 추이를 시각화합니다.")

# 💡 참고: Yahoo Finance에서 직접적으로 "글로벌 시가총액 TOP 10" 리스트를 제공하지 않습니다.
#       따라서, 일반적으로 알려진 시가총액 상위 기업들의 티커를 수동으로 입력해야 합니다.
#       아래 리스트는 2023년 말 ~ 2024년 초 기준으로 많이 언급되는 기업들입니다.
#       실제 TOP 10은 변동성이 크므로, 필요에 따라 업데이트해야 합니다.
#       (예: S&P 500 또는 NASDAQ 100 상위 종목 참조)
top_10_tickers = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA", # 최근 급성장으로 상위권 진입
    "Amazon": "AMZN",
    "Alphabet (GOOGL)": "GOOGL",
    "Alphabet (GOOG)": "GOOG",
    "Meta Platforms": "META",
    "Berkshire Hathaway": "BRK-B",
    "Tesla": "TSLA",
    "Eli Lilly": "LLY", # 최근 급성장으로 상위권 진입
    "Broadcom": "AVGO", # 최근 급성장으로 상위권 진입
}

selected_company_name = st.selectbox(
    "시가총액 상위 기업을 선택하세요:",
    list(top_10_tickers.keys())
)

ticker_symbol = top_10_tickers[selected_company_name]

st.subheader(f"📈 {selected_company_name} ({ticker_symbol}) 최근 1년간 주가 변화")

@st.cache_data
def get_stock_data(ticker, period):
    """
    주식 데이터를 Yahoo Finance에서 가져옵니다.
    """
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period)
        return data
    except Exception as e:
        st.error(f"'{ticker}' 주식 데이터를 가져오는 데 실패했습니다: {e}")
        return pd.DataFrame()

# 최근 1년 데이터 기간 설정
end_date = datetime.now()
start_date = end_date - timedelta(days=365) # 1년 전

# 주식 데이터 가져오기
df = get_stock_data(ticker_symbol, period="1y")

if not df.empty:
    # Plotly 시각화
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        mode='lines',
        name='종가',
        line=dict(color='blue')
    ))

    # 최고가와 최저가 표시
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['High'],
        mode='lines',
        name='최고가',
        line=dict(color='green', dash='dot')
    ))
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Low'],
        mode='lines',
        name='최저가',
        line=dict(color='red', dash='dot')
    ))

    # 레이아웃 설정
    fig.update_layout(
        title=f'{selected_company_name} ({ticker_symbol}) 1년 주가 추이',
        xaxis_title='날짜',
        yaxis_title='주가 (USD)',
        xaxis_rangeslider_visible=True,
        hovermode="x unified",
        template="plotly_white",
        legend_title="지표"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("데이터 테이블")
    st.dataframe(df[['Open', 'High', 'Low', 'Close', 'Volume']].tail(100).sort_index(ascending=False)) # 최근 100개 데이터 표시
else:
    st.warning("선택한 기업의 주식 데이터를 가져올 수 없습니다. 티커를 확인해주세요.")

st.markdown("""
<style>
    .stApp {
        background-color: #f0f2f6;
    }
    .css-1d3z3hw { /* Streamlit header */
        color: #26272e;
    }
</style>
""", unsafe_allow_html=True)
