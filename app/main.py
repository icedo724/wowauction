import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

st.set_page_config(page_title="와우 '한밤' 경제 지표", layout="wide")

st.markdown("""
    <style>
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    [data-testid="stMetricValue"] { color: #ffcc00; }
    </style>
    """, unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
history_file = os.path.join(BASE_DIR, 'data', 'market_history.csv')

midnight_date = datetime(2026, 3, 2)
days_left = (midnight_date - datetime.now()).days
st.sidebar.header("⚔️ 확장팩 카운트다운")
st.sidebar.metric("한밤(Midnight) 출시", f"D-{days_left}일")
st.sidebar.markdown("---")
st.sidebar.write("💡 **수집 안내**")
st.sidebar.caption("블리자드 공식 API를 통해 매시간 한국 서버의 실시간 경매장 시세를 기록합니다.")

st.title("🏹 월드 오브 워크래프트: 한밤 실시간 거래소")

if os.path.exists(history_file):
    df_wide = pd.read_csv(history_file, index_col=0)

    df_long = df_wide.reset_index().melt(id_vars='item_name', var_name='수집 시각', value_name='가격')
    df_long.rename(columns={'item_name': '품목명'}, inplace=True)
    df_long['수집 시각'] = pd.to_datetime(df_long['수집 시각'])

    latest_col = df_wide.columns[-1]
    prev_col = df_wide.columns[-2] if len(df_wide.columns) > 1 else latest_col

    token_price = df_wide.loc['WoW 토큰', latest_col] if 'WoW 토큰' in df_wide.index else 0
    token_diff = token_price - df_wide.loc['WoW 토큰', prev_col] if 'WoW 토큰' in df_wide.index else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🪙 현재 토큰 시세", f"{token_price:,.0f} G", f"{token_diff:,.0f} G")
    with col2:
        gold_per_won = (token_price / 22000) if token_price > 0 else 0
        st.metric("💸 1,000원당 가치", f"{gold_per_won:,.0f} G")
    with col3:
        st.metric("📦 추적 중인 품목", f"{len(df_wide)}개")
    with col4:
        if len(df_wide.columns) > 1:
            change = ((df_wide[latest_col] - df_wide[prev_col]) / df_wide[prev_col] * 100).fillna(0)
            top_riser = change.idxmax()
            st.metric("🔥 급등 품목", top_riser, f"{change.max():.1f}%")

    st.divider()

    left_col, right_col = st.columns([1, 3])

    with left_col:
        st.subheader("🛠️ 시세 필터")
        all_items = sorted(df_wide.index.unique())
        default_items = [i for i in ['WoW 토큰', '창연', '더럽혀진 부싯깃 상자'] if i in all_items]
        selected_items = st.multiselect("차트에 표시할 품목을 선택하세요", all_items, default=default_items)

        st.markdown("---")
        st.write("📊 **품목별 현재가 (골드)**")
        display_df = df_wide[[latest_col]].sort_values(by=latest_col, ascending=False)
        display_df.columns = ['현재 가격']
        st.dataframe(display_df, use_container_width=True)

    with right_col:
        plot_df = df_long[df_long['품목명'].isin(selected_items)].dropna()
        if not plot_df.empty:
            fig = px.line(
                plot_df,
                x='수집 시각',
                y='가격',
                color='품목명',
                markers=True,
                line_shape='spline',
                labels={'가격': '가격 (골드)', '수집 시각': '날짜 및 시간', '품목명': '아이템 이름'}
            )
            fig.update_layout(
                hovermode="x unified",
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(title="선택된 아이템", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("왼쪽 필터에서 분석할 아이템을 선택해 주세요.")

else:
    st.error("데이터 파일을 읽을 수 없습니다. GitHub Actions가 첫 데이터를 수집할 때까지 기다려 주세요.")