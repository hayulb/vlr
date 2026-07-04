import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. 페이지 레이아웃 설정
st.set_page_config(
    page_title="발로란트 무기 스탯 대시보드",
    page_icon="🔫",
    layout="wide"
)

# 2. 데이터 로드 함수
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("valorant-stats.csv")
        return df
    except FileNotFoundError:
        st.error("데이터 파일('valorant-stats.csv')을 찾을 수 없습니다. 파일이 main.py와 같은 폴더에 있는지 확인해주세요.")
        return None

df = load_data()

if df is not None:
    # 대시보드 타이틀
    st.title("🔫 발로란트 무기 스탯 분석기")
    st.markdown("업로드된 데이터를 바탕으로 무기들의 가격, 연사력, 데미지 스탯을 비교하고 분석합니다.")
    st.markdown("---")

    # ---- 사이드바 설정 (필터링) ----
    st.sidebar.header("🛠️ 필터 및 설정")
    
    # 무기 종류 필터 (전체, Sidearm, SMG, Rifle 등)
    weapon_types = ["전체"] + sorted(df["Weapon Type"].dropna().unique().tolist())
    selected_type = st.sidebar.selectbox("무기 종류 선택", weapon_types)

    # 가격 범위 필터
    min_price, max_price = int(df["Price"].min()), int(df["Price"].max())
    selected_price = st.sidebar.slider("가격 범위 선택", min_price, max_price, (min_price, max_price))

    # 필터링 데이터 적용
    filtered_df = df[(df["Price"] >= selected_price[0]) & (df["Price"] <= selected_price[1])]
    if selected_type != "전체":
        filtered_df = filtered_df[filtered_df["Weapon Type"] == selected_type]

    # ---- 상단 요약 지표 (KPI) ----
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("선택된 무기 수", f"{len(filtered_df)} 개")
    with col2:
        st.metric("평균 가격", f"{int(filtered_df['Price'].mean()):,} 크레드")
    with col3:
        st.metric("최고 연사력", f"{filtered_df['Fire Rate'].max()} 발/초")

    st.markdown("---")

    # ---- 메인 화면 1: 데이터 테이블 ----
    st.subheader("📊 무기 스탯 데이터 목록")
    st.dataframe(
        filtered_df,
        column_config={
            "Name": "무기 이름",
            "Weapon Type": "종류",
            "Price": st.column_config.NumberColumn("가격", format="%d 크레드"),
            "Fire Rate": st.column_config.NumberColumn("연사력"),
            "Wall Penetration": "관통력",
            "Magazine Capacity": st.column_config.NumberColumn("탄창 크기"),
        },
        hide_index=True,
        use_container_width=True
    )

    st.markdown("---")

    # ---- 메인 화면 2: 데미지 비교 차트 ----
    st.subheader("⚔️ 무기별 데미지 비교 (기본 거리)")
    
    # 그래프로 비교할 무기를 다중 선택하는 박스 (기본값으로 상위 5개 선택)
    available_weapons = filtered_df["Name"].tolist()
    default_selection = available_weapons[:5] if len(available_weapons) >= 5 else available_weapons
    
    selected_weapons = st.multiselect(
        "비교할 무기를 선택하세요 (여러 개 선택 가능)", 
        available_weapons, 
        default=default_selection
    )

    if selected_weapons:
        chart_df = filtered_df[filtered_df["Name"].isin(selected_weapons)]
        
        # Plotly 그룹 바 차트 시각화
        fig = go.Figure()
        fig.add_trace(go.Bar(x=chart_df["Name"], y=chart_df["HDMG_0"], name="헤드샷 (Head)", marker_color="#FF4B4B"))
        fig.add_trace(go.Bar(x=chart_df["Name"], y=chart_df["BDMG_0"], name="바디샷 (Body)", marker_color="#0068C9"))
        fig.add_trace(go.Bar(x=chart_df["Name"], y=chart_df["LDMG_0"], name="레그샷 (Leg)", marker_color="#29B09D"))

        fig.update_layout(
            barmode='group',
            xaxis_title="무기 이름",
            yaxis_title="데미지 수치",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ 차트를 표시하려면 최소 하나의 무기를 선택해주세요.")

else:
    st.info("데이터셋을 로드하는 데 실패했습니다.")
