#######################
# Import libraries
import textwrap

import pandas as pd
import streamlit as st

#######################
# Page configuration
st.set_page_config(
    page_title="Equity Strategy Planner",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

#######################
# Helpers
def format_structure_diagram(lines: list[str]) -> str:
    cleaned = [line.strip() for line in lines if line.strip()]
    if not cleaned:
        return "정책 → 지원 수단 → 수혜 영역 → 기업군"
    return "\n".join(f"{idx + 1}. {line}" for idx, line in enumerate(cleaned))


def build_strategy_table(stock_rows: pd.DataFrame, config: dict) -> pd.DataFrame:
    df = stock_rows.copy()
    df["현재가"] = pd.to_numeric(df["현재가"], errors="coerce")

    df["적정 매수가"] = (df["현재가"] * (1 - config["buy_discount"])).round(2)
    df["1차 목표가"] = (df["현재가"] * (1 + config["target1"])).round(2)
    df["2차 목표가"] = (df["현재가"] * (1 + config["target2"])).round(2)
    df["3차 목표가"] = (df["현재가"] * (1 + config["target3"])).round(2)
    df["손절가"] = (df["현재가"] * (1 - config["stop_loss"])).round(2)
    df["트레일링 스탑(%)"] = f"{int(config['trailing_stop'] * 100)}%"

    df = df.rename(
        columns={
            "역할": "역할(대장주/핵심부품)",
            "종목명": "종목명",
            "코드": "코드",
        }
    )

    return df[
        [
            "역할(대장주/핵심부품)",
            "종목명",
            "코드",
            "현재가",
            "적정 매수가",
            "1차 목표가",
            "2차 목표가",
            "3차 목표가",
            "손절가",
            "트레일링 스탑(%)",
        ]
    ]


def build_excel_ready_table(strategy_table: pd.DataFrame, trailing_stop: float) -> pd.DataFrame:
    excel_table = strategy_table.copy()
    excel_table["트레일링 스탑 수식(엑셀)"] = ""
    for idx in range(len(excel_table)):
        row_number = idx + 2  # header row + 1
        excel_table.loc[idx, "트레일링 스탑 수식(엑셀)"] = (
            f"=MAX(H{row_number}, D{row_number}*(1-{trailing_stop}))"
        )
    return excel_table


#######################
# Sidebar
with st.sidebar:
    st.header("입력 설정")
    industry_theme = st.text_input("산업 테마", value="AI 반도체")
    analysis_date = st.text_input("기준 시점", value="2026년 1월")

    st.markdown("---")
    st.subheader("정책 방향 요약")
    policy_direction = st.text_area(
        "정부 정책 방향(핵심 키워드 중심)",
        value="국가 전략산업 지정, 설비투자 세액공제, 인재 양성 확대, 공급망 내재화",
        height=120,
    )
    policy_structure = st.text_area(
        "정책 구조도(줄 단위로 입력)",
        value="국가 전략산업 지정 → 예산/세액공제 확대 → 공급망 자립 및 생산능력 확대 → 팹/소재/장비 수혜",
        height=120,
    )

    st.markdown("---")
    st.subheader("가격 가정")
    buy_discount = st.slider("적정 매수가 할인율", 0.0, 0.3, 0.07, 0.01)
    target1 = st.slider("1차 목표가 상승률", 0.0, 1.0, 0.25, 0.01)
    target2 = st.slider("2차 목표가 상승률", 0.0, 2.0, 0.45, 0.01)
    target3 = st.slider("3차 목표가 상승률", 0.0, 3.0, 0.7, 0.01)
    stop_loss = st.slider("손절가 하락률", 0.0, 0.5, 0.12, 0.01)
    trailing_stop = st.slider("트레일링 스탑(%)", 0.0, 0.5, 0.08, 0.01)

    st.markdown("---")
    st.subheader("추가 분석 옵션")
    option_sector = st.checkbox("시장 상황에 따라 섹터별 추천 종목")
    option_value = st.checkbox("PER, ROE, PBR 기반의 저평가 종목")
    option_style = st.checkbox("장기성장주 vs 고배당가치주 비교 분석")
    option_defense = st.checkbox("위기 상황 속에서도 견디는 버핏형 방어주")
    option_re_rating = st.checkbox("실적 시즌 직후 상향 리레이팅 가능성")

    st.markdown("---")
    st.caption("⚠️ 본 앱은 학습용 예시이며, 실제 투자 조언이 아닙니다.")

#######################
# Main content
st.title("주식 전략 분석 템플릿")
st.write(
    "요청하신 구조를 바탕으로 산업 테마 분석, 정책 구조도, 종목 선별, 매매 전략 표, "
    "리스크 점검을 한 번에 정리합니다."
)

st.markdown("### 1) 산업 테마 요약")
st.write(
    f"- **관심 산업:** {industry_theme}\n"
    f"- **기준 시점:** {analysis_date}\n"
    "- **핵심 포인트:** 글로벌 수요, 공급망 안정화, 기술 격차, 정책 모멘텀을 통합 점검"
)

st.markdown("### 2) 정책 분석 (구조도)")
structure_lines = format_structure_diagram(policy_structure.splitlines())
st.markdown(f"```\n{structure_lines}\n```")
st.markdown("**정책 방향 요약**")
for bullet in textwrap.wrap(policy_direction, width=80):
    st.write(f"- {bullet}")

st.markdown("### 3) 유망 종목 선정")
st.caption("대장주/핵심 부품주를 포함해 4개 종목을 입력하세요.")

default_rows = pd.DataFrame(
    [
        {"역할": "대장주", "종목명": "대표 기업 A", "코드": "A0001", "현재가": 100.0},
        {"역할": "핵심 부품주", "종목명": "부품 기업 B", "코드": "B0002", "현재가": 75.0},
        {"역할": "핵심 부품주", "종목명": "소재 기업 C", "코드": "C0003", "현재가": 55.0},
        {"역할": "대장주", "종목명": "플랫폼 기업 D", "코드": "D0004", "현재가": 120.0},
    ]
)

stock_rows = st.data_editor(
    default_rows,
    width="stretch",
    num_rows="fixed",
    column_config={
        "현재가": st.column_config.NumberColumn(format="%.2f"),
    },
)

strategy_table = build_strategy_table(
    stock_rows,
    {
        "buy_discount": buy_discount,
        "target1": target1,
        "target2": target2,
        "target3": target3,
        "stop_loss": stop_loss,
        "trailing_stop": trailing_stop,
    },
)

st.markdown("### 4) 매매 전략 표")
st.dataframe(strategy_table, width="stretch", hide_index=True)

st.markdown("### 5) 모멘텀 선반영 및 리스크 체크")
st.write(
    f"- **{analysis_date} 기준 반영 수준 점검:** 정책 발표 이후 밸류에이션 멀티플이 "
    "얼마나 선반영되었는지 PER/PBR 변화 추적 필요.\n"
    "- **수급 리스크:** 특정 테마로 과열될 경우 단기 변동성 확대 가능.\n"
    "- **펀더멘털 리스크:** 수주/매출 가시성이 약하면 목표가 조정 가능."
)

st.markdown("### 6) 가능한 제안 유형 (1~5번 대응)")

sector_rotation_table = pd.DataFrame(
    [
        {
            "시장 국면": "금리 인하 + 경기 확장",
            "수혜 섹터": "경기소비재, IT, 산업재",
            "대장주·부품주": "대표 기업 A / 부품 기업 B",
            "전략 키워드": "성장주 비중 확대",
        },
        {
            "시장 국면": "금리 동결 + 경기 둔화",
            "수혜 섹터": "필수소비재, 헬스케어",
            "대장주·부품주": "플랫폼 기업 D / 소재 기업 C",
            "전략 키워드": "방어 섹터 리밸런싱",
        },
    ]
)

value_screen_table = pd.DataFrame(
    [
        {"종목명": "저평가 후보 1", "PER": 8.5, "ROE": "12%", "PBR": 0.8, "업종 평균 대비 괴리율": "-25%"},
        {"종목명": "저평가 후보 2", "PER": 9.2, "ROE": "10%", "PBR": 0.9, "업종 평균 대비 괴리율": "-18%"},
    ]
)

style_compare_table = pd.DataFrame(
    [
        {
            "구분": "장기성장주",
            "핵심 지표": "매출 CAGR, R&D 비중, 정책 수혜",
            "포트폴리오 제안": "성장 테마 60% + 핵심 부품 40%",
            "변동성/방어력": "변동성 높음 / 방어력 낮음",
        },
        {
            "구분": "고배당가치주",
            "핵심 지표": "배당수익률, FCF, 배당 지속성",
            "포트폴리오 제안": "배당 안정 70% + 성장 30%",
            "변동성/방어력": "변동성 낮음 / 방어력 높음",
        },
    ]
)

defense_table = pd.DataFrame(
    [
        {"종목명": "방어주 후보 1", "핵심 강점": "독점력/가격전가력", "과거 하락장 방어 성과": "+4.2%"},
        {"종목명": "방어주 후보 2", "핵심 강점": "반복 매출 구조", "과거 하락장 방어 성과": "+2.8%"},
    ]
)

re_rating_table = pd.DataFrame(
    [
        {"종목명": "리레이팅 후보 1", "실적 서프라이즈": "+12%", "가이던스 상향": "있음", "리레이팅 여력 점수": 82},
        {"종목명": "리레이팅 후보 2", "실적 서프라이즈": "+9%", "가이던스 상향": "부분적", "리레이팅 여력 점수": 75},
    ]
)

with st.expander("① 시장 상황에 따라 섹터별 추천 종목", expanded=option_sector):
    st.markdown("**가능한 분석**")
    st.write("- 금리/환율/정책 방향에 따른 섹터 로테이션 점검")
    st.write("- 경기 국면별 유리 업종 도출")
    st.markdown("**산출물**")
    st.dataframe(sector_rotation_table, width="stretch", hide_index=True)

with st.expander("② PER·ROE·PBR 기반 저평가 종목", expanded=option_value):
    st.markdown("**가능한 분석**")
    st.write("- 절대/상대 가치지표 기반 스크리닝")
    st.write("- 업종 평균 대비 밸류에이션 디스카운트 비교")
    st.markdown("**산출물**")
    st.dataframe(value_screen_table, width="stretch", hide_index=True)

with st.expander("③ 장기성장주 vs 고배당가치주 비교", expanded=option_style):
    st.markdown("**가능한 분석**")
    st.write("- 성장주: 매출 CAGR, R&D 비중, 정책 수혜")
    st.write("- 배당주: 배당수익률, FCF, 배당 지속성")
    st.markdown("**산출물**")
    st.dataframe(style_compare_table, width="stretch", hide_index=True)

with st.expander("④ ‘버핏형 방어주’ (위기 대응)", expanded=option_defense):
    st.markdown("**가능한 분석**")
    st.write("- 경기 침체/금리 변동기 실적 방어 가능 기업 점검")
    st.write("- 독점력, 가격전가력, 반복 매출 구조 평가")
    st.markdown("**산출물**")
    st.dataframe(defense_table, width="stretch", hide_index=True)

with st.expander("⑤ 실적 시즌 직후 리레이팅 후보", expanded=option_re_rating):
    st.markdown("**가능한 분석**")
    st.write("- 실적 서프라이즈 + 가이던스 상향 기업 추출")
    st.write("- PER 재평가 가능성 점수화")
    st.markdown("**산출물**")
    st.dataframe(re_rating_table, width="stretch", hide_index=True)

st.markdown("### 엑셀 붙여넣기용 요약 표")
excel_ready = build_excel_ready_table(strategy_table, trailing_stop)
st.dataframe(excel_ready, width="stretch", hide_index=True)
st.code(excel_ready.to_csv(index=False), language="text")

st.markdown("---")
st.caption(
    "트레일링 스탑 예시 수식: 손절가(H열)와 현재가(D열)를 기준으로 자동 상향 조정."
)
