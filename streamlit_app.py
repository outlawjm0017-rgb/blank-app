#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

#######################
# Page configuration
st.set_page_config(
    page_title="US Population Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("default")

#######################
# CSS styling
#######################
# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

/* Metric 카드 배경색 수정 */
[data-testid="stMetric"] {
    background-color: #f9f9f9;   /* 밝은 회색 배경 */
    border: 1px solid #e0e0e0;   /* 옅은 테두리 */
    border-radius: 8px;          /* 모서리 둥글게 */
    text-align: center;
    padding: 15px 0;
    color: #000000 !important;   /* 글자색 검정 */
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
  color: #333333 !important;     /* 라벨 글자색 */
}

[data-testid="stMetricDeltaIcon-Up"],
[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)



#######################
# Load data
df_reshaped = pd.read_csv('titanic.csv') ## 분석 데이터 넣기


#######################
# Sidebar
with st.sidebar:
    st.header("Titanic Survival Dashboard")
    st.caption("필터를 적용해 분석 대상을 선택하세요.")

    # ── 색상 테마
    color_theme = st.selectbox(
        "색상 테마 선택",
        ["blues", "viridis", "plasma", "inferno", "magma", "turbo"],
        index=0,
        help="시각화에 사용할 컬러맵"
    )

    st.markdown("---")

    # ── 범주형 필터
    sex_opts = sorted(df_reshaped["Sex"].dropna().unique())
    pclass_opts = sorted(df_reshaped["Pclass"].dropna().unique())
    embarked_opts = sorted(df_reshaped["Embarked"].dropna().unique())

    sel_sex = st.multiselect("성별 선택", options=sex_opts, default=sex_opts)
    sel_pclass = st.multiselect("선실 등급(Pclass) 선택", options=pclass_opts, default=pclass_opts)
    #sel_embarked = st.multiselect("승선 항구(Embarked) 선택", options=embarked_opts, default=embarked_opts)
    sel_embarked = st.multiselect(
    "승선 항구(Embarked) 선택",
    options=df_reshaped['Embarked'].dropna().unique(),
    default=df_reshaped['Embarked'].dropna().unique(),
    format_func=lambda x: x   # 한글 자동 번역 방지
)

    st.markdown("---")

    # ── 수치형 필터 (나이/요금)
    age_min, age_max = (
        int(df_reshaped["Age"].dropna().min()),
        int(df_reshaped["Age"].dropna().max())
    )
    fare_min, fare_max = (
        float(df_reshaped["Fare"].dropna().min()),
        float(df_reshaped["Fare"].dropna().max())
    )

    sel_age = st.slider("나이(Age) 범위 선택", min_value=age_min, max_value=age_max, value=(age_min, age_max))
    sel_fare = st.slider("운임(Fare) 범위 선택", min_value=float(fare_min), max_value=float(fare_max),
                         value=(float(fare_min), float(fare_max)))

    st.markdown("---")

    # ── 전처리 옵션
    drop_na = st.checkbox("핵심 분석 컬럼(Age, Fare, Embarked) 결측치 제외", value=True)

    # ── 필터 적용 / 리셋
    if st.button("필터 초기화"):
        st.experimental_rerun()

# ── 선택값을 반영한 필터링 데이터프레임 생성
df = df_reshaped.copy()
if drop_na:
    df = df.dropna(subset=["Age", "Fare", "Embarked"])

if sel_sex:
    df = df[df["Sex"].isin(sel_sex)]
if sel_pclass:
    df = df[df["Pclass"].isin(sel_pclass)]
if sel_embarked:
    df = df[df["Embarked"].isin(sel_embarked)]

df = df[(df["Age"].between(sel_age[0], sel_age[1], inclusive="both")) &
        (df["Fare"].between(sel_fare[0], sel_fare[1], inclusive="both"))]

# ── 전역 상태 공유 (플롯에서 사용)
st.session_state["filtered_df"] = df
st.session_state["color_theme"] = color_theme



#######################
# Plots



#######################
# Dashboard Main Panel
col = st.columns((1.5, 4.5, 2), gap='medium')


with col[0]:
    st.subheader("요약 지표")

    df = st.session_state["filtered_df"]

    # 전체 인원
    total_passengers = len(df)
    survived_count = df["Survived"].sum()
    died_count = total_passengers - survived_count

    st.metric("전체 탑승객 수", f"{total_passengers} 명")
    st.metric("생존자 수", f"{survived_count} 명")
    st.metric("사망자 수", f"{died_count} 명")

    st.markdown("---")

    # 성별 생존율
    st.markdown("**성별 생존율**")
    sex_survival = (
        df.groupby("Sex")["Survived"]
        .mean()
        .reset_index()
        .rename(columns={"Survived": "SurvivalRate"})
    )

    chart_sex = alt.Chart(sex_survival).mark_bar().encode(
        x=alt.X("Sex:N", title="성별"),
        y=alt.Y("SurvivalRate:Q", title="생존율", axis=alt.Axis(format="%")),
        color=alt.Color("Sex:N", scale=alt.Scale(scheme=st.session_state["color_theme"]))
    ).properties(width=200, height=200)

    st.altair_chart(chart_sex, use_container_width=True)

    st.markdown("---")

    # 승선 항구별 탑승자 분포
    st.markdown("**승선 항구별 탑승자 수**")
    embarked_dist = (
        df["Embarked"].value_counts().reset_index()
        .rename(columns={"index": "Embarked", "Embarked": "Count"})
    )

    chart_embarked = alt.Chart(embarked_dist).mark_bar().encode(
        x=alt.X("Embarked:N", title="항구"),
        y=alt.Y("Count:Q", title="탑승객 수"),
        color=alt.Color("Embarked:N", scale=alt.Scale(scheme=st.session_state["color_theme"]))
    ).properties(width=200, height=200)

    st.altair_chart(chart_embarked, use_container_width=True)



with col[1]:
    st.subheader("분포 · 히트맵 시각화")
    df = st.session_state["filtered_df"]
    scheme = st.session_state.get("color_theme", "blues")

    # =========================
    # 1) 선실등급 × 성별 생존율 히트맵
    # =========================
    st.markdown("**선실등급 × 성별 생존율**")
    heat1 = (
        df.dropna(subset=["Pclass", "Sex"])
          .groupby(["Pclass", "Sex"])["Survived"]
          .mean()
          .reset_index()
          .rename(columns={"Survived": "SurvivalRate"})
    )

    chart_heat1 = (
        alt.Chart(heat1)
        .mark_rect()
        .encode(
            x=alt.X("Pclass:O", title="선실 등급"),
            y=alt.Y("Sex:N", title="성별"),
            color=alt.Color("SurvivalRate:Q",
                            title="생존율",
                            scale=alt.Scale(scheme=scheme),
                            legend=alt.Legend(format="%")),
            tooltip=[
                alt.Tooltip("Pclass:O", title="등급"),
                alt.Tooltip("Sex:N", title="성별"),
                alt.Tooltip("SurvivalRate:Q", title="생존율", format=".1%")
            ]
        )
        .properties(height=220)
    )
    st.altair_chart(chart_heat1, use_container_width=True)

    st.markdown("---")

    # =========================
    # 2) 연령대 × 생존(0/1) 인원 히트맵  (★ 수정됨)
    # =========================
    st.markdown("**연령대 × 생존 여부 인원수**")
    age_df = df.dropna(subset=["Age"]).copy()

    # ── bins/labels 개수 일치: 0–9, 10–19, …, 80–89, 90+
    bins = list(range(0, 100, 10)) + [120]      # 0,10,20,...,90,120 → 11개 모서리 = 10개 구간
    labels = [f"{b}–{b+9}" for b in range(0, 90, 10)] + ["90+"]  # 10개 라벨

    age_df["AgeGroup"] = pd.cut(age_df["Age"], bins=bins, labels=labels, right=False, include_lowest=True)

    heat2 = (
        age_df.groupby(["AgeGroup", "Survived"])
              .size()
              .reset_index(name="Count")
    )
    chart_heat2 = (
        alt.Chart(heat2)
        .mark_rect()
        .encode(
            x=alt.X("AgeGroup:N", title="연령대", sort=labels),
            y=alt.Y("Survived:O", title="생존(1)/사망(0)"),
            color=alt.Color("Count:Q", title="인원수", scale=alt.Scale(scheme=scheme)),
            tooltip=[
                alt.Tooltip("AgeGroup:N", title="연령대"),
                alt.Tooltip("Survived:O", title="생존여부"),
                alt.Tooltip("Count:Q", title="인원수")
            ]
        )
        .properties(height=220)
    )
    st.altair_chart(chart_heat2, use_container_width=True)

    st.markdown("---")

    # =========================
    # 3) 나이 분포 (생존/사망 비교)
    # =========================
    st.markdown("**나이 분포 (생존/사망 비교)**")
    chart_age = (
        alt.Chart(age_df)
        .transform_bin("AgeBin", field="Age", bin=alt.Bin(maxbins=30))
        .mark_bar(opacity=0.8)
        .encode(
            x=alt.X("AgeBin:Q", title="나이"),
            y=alt.Y("count():Q", title="빈도"),
            color=alt.Color("Survived:N",
                            title="생존(1)/사망(0)",
                            scale=alt.Scale(scheme=scheme)),
            tooltip=[alt.Tooltip("count():Q", title="빈도")]
        )
        .properties(height=240)
    )
    st.altair_chart(chart_age, use_container_width=True)

    st.markdown("---")

    # =========================
    # 4) 운임(Fare) 분포 박스플롯 (등급별)
    # =========================
    st.markdown("**운임(Fare) 분포 (등급별 박스플롯)**")
    fare_df = df.dropna(subset=["Fare", "Pclass"]).copy()
    fig_box = px.box(
        fare_df, x="Pclass", y="Fare", points="suspectedoutliers",
        labels={"Pclass": "선실 등급", "Fare": "운임(Fare)"},
        template="plotly_white"
    )
    st.plotly_chart(fig_box, use_container_width=True)











with col[2]:
    st.subheader("상세 통계 · Top 그룹")

    df = st.session_state["filtered_df"]
    scheme = st.session_state.get("color_theme", "blues")

    # =========================
    # 1) 선실 등급별 생존율 순위
    # =========================
    st.markdown("**선실 등급별 생존율 순위**")
    pclass_survival = (
        df.groupby("Pclass")["Survived"]
          .mean()
          .reset_index()
          .rename(columns={"Survived": "SurvivalRate"})
          .sort_values("SurvivalRate", ascending=False)
    )

    chart_pclass = (
        alt.Chart(pclass_survival)
        .mark_bar()
        .encode(
            x=alt.X("SurvivalRate:Q", title="생존율", axis=alt.Axis(format="%")),
            y=alt.Y("Pclass:O", title="선실 등급", sort='-x'),
            color=alt.Color("Pclass:O", scale=alt.Scale(scheme=scheme)),
            tooltip=[
                alt.Tooltip("Pclass:O", title="선실 등급"),
                alt.Tooltip("SurvivalRate:Q", title="생존율", format=".1%")
            ]
        )
        .properties(height=200)
    )
    st.altair_chart(chart_pclass, use_container_width=True)

    st.markdown("---")

    # =========================
    # 2) 성별 + 등급 조합별 생존율 상위/하위 그룹
    # =========================
    st.markdown("**성별+등급 조합별 Top 그룹**")
    combo_survival = (
        df.groupby(["Sex", "Pclass"])["Survived"]
          .mean()
          .reset_index()
          .rename(columns={"Survived": "SurvivalRate"})
          .sort_values("SurvivalRate", ascending=False)
    )

    # 상위 3개, 하위 3개 그룹
    top3 = combo_survival.head(3)
    bottom3 = combo_survival.tail(3)

    st.write("🔼 **생존율 상위 그룹 (Top 3)**")
    st.table(top3.style.format({"SurvivalRate": "{:.1%}"}))

    st.write("🔽 **생존율 하위 그룹 (Bottom 3)**")
    st.table(bottom3.style.format({"SurvivalRate": "{:.1%}"}))

    st.markdown("---")

    # =========================
    # 3) 가족 동반 여부에 따른 생존율
    # =========================
    st.markdown("**가족 동반 여부에 따른 생존율**")
    df["Family"] = df["SibSp"] + df["Parch"]
    df["WithFamily"] = df["Family"].apply(lambda x: "동반" if x > 0 else "단독")

    family_survival = (
        df.groupby("WithFamily")["Survived"]
          .mean()
          .reset_index()
          .rename(columns={"Survived": "SurvivalRate"})
    )

    chart_family = (
        alt.Chart(family_survival)
        .mark_bar()
        .encode(
            x=alt.X("WithFamily:N", title="가족 동반 여부"),
            y=alt.Y("SurvivalRate:Q", title="생존율", axis=alt.Axis(format="%")),
            color=alt.Color("WithFamily:N", scale=alt.Scale(scheme=scheme)),
            tooltip=[
                alt.Tooltip("WithFamily:N", title="가족 동반 여부"),
                alt.Tooltip("SurvivalRate:Q", title="생존율", format=".1%")
            ]
        )
        .properties(height=200)
    )
    st.altair_chart(chart_family, use_container_width=True)

    st.markdown("---")

    # =========================
    # 4) 데이터 출처
    # =========================
    st.markdown("**About**")
    st.info(
        """
        데이터셋: [Titanic Dataset (Kaggle)](https://www.kaggle.com/c/titanic)  
        1912년 타이타닉호 침몰 사건의 실제 승객 데이터를 기반으로 구성되었습니다.  
        본 대시보드는 Streamlit을 활용한 데이터 분석 및 시각화 예시입니다.
        """
    )
