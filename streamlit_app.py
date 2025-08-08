import json
import textwrap
import streamlit as st
from datetime import datetime

# -------------------- 기본 설정 --------------------
st.set_page_config(
    page_title="8비트 학습 성향 진단 (MBTI)",
    page_icon="🕹️",
)

# 8비트 느낌의 폰트/스타일 (Google Fonts - Press Start 2P)
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
<style>
:root{
  --retro-bg: #0f172a;   /* 슬레이트-900 */
  --retro-card: #111827; /* 그레이-900 */
  --retro-accent: #22d3ee; /* 시안 */
  --retro-accent-2: #a78bfa; /* 퍼플 */
  --retro-text: #e5e7eb; /* 그레이-200 */
  --retro-warn: #f59e0b; /* 앰버 */
}
html, body, [class*="block-container"]{
  font-family: 'Press Start 2P', system-ui, -apple-system, Segoe UI, Roboto, 'Noto Sans KR', sans-serif;
  background: var(--retro-bg);
  color: var(--retro-text);
}
h1, h2, h3 { letter-spacing: 1px; }
.retro-card{
  border: 4px solid var(--retro-accent);
  border-radius: 12px;
  padding: 18px;
  background: linear-gradient(180deg, #0b1220, var(--retro-card));
  box-shadow: 0px 0px 0px 4px #0b1220, 0 0 24px rgba(34,211,238,.25) inset;
}
.retro-chip{
  display:inline-block;
  padding:6px 10px;
  border:3px solid var(--retro-accent-2);
  border-radius: 10px;
  margin-right:6px;
  margin-bottom:6px;
  font-size:12px;
}
.pixel-btn>button{
  border: 4px solid var(--retro-accent-2) !important;
  background: #1f2937 !important;
  color: var(--retro-text) !important;
  box-shadow: 0 0 0 4px #0b1220, inset 0 0 12px rgba(167,139,250,.25) !important;
}
.small { font-size: 11px; opacity:.9; }
hr { border-top: 4px dashed #334155; margin: 18px 0; }
</style>
""", unsafe_allow_html=True)

st.title("🕹️ 8비트 학습 성향 진단 (MBTI)")

st.markdown(
    "<div class='retro-card'>"
    "<b>안내</b><br>"
    "아래 문항은 당신의 학습 성향을 MBTI 4지표(E/I, S/N, T/F, J/P)에 기반해 진단합니다.<br>"
    "각 문항에 대해 평소 나에게 <u>가장 가까운</u> 선택지를 고르세요."
    "</div>",
    unsafe_allow_html=True
)

# -------------------- 문항 정의 --------------------
# key: 지표, val: (문항, reverse?)  reverse=True면 점수 반대로 집계
QUESTIONS = {
    "EI": [
        ("여럿이 함께 공부하면 에너지가 나고 더 잘 된다.", False),
        ("수업 발표/토론이 있을 때 부담보다는 기대가 된다.", False),
        ("혼자 공부하는 시간이 가장 편하고 집중이 잘 된다.", True),
    ],
    "SN": [
        ("개념보다 먼저 예시/사례를 봐야 이해가 된다.", False),
        ("세부 사실·절차를 하나씩 따라가며 배우는 편이다.", False),
        ("아이디어를 확장하고 상상하는 활동이 재미있다.", True),
    ],
    "TF": [
        ("정답·근거가 분명한 문제를 더 선호한다.", False),
        ("과제에서 사람들의 감정이나 관계도 중요하다고 느낀다.", True),
        ("의사결정 시 데이터·논리를 가장 우선한다.", False),
    ],
    "JP": [
        ("플래너로 일정을 정리하고 계획대로 진행한다.", False),
        ("〝마감 직전 몰입〞이 오히려 효율적일 때가 많다.", True),
        ("계획이 바뀌어도 즉석에서 유연하게 대응한다.", True),
    ],
}

CHOICES = [
    "매우 그렇다 (+2)",
    "그렇다 (+1)",
    "보통 (0)",
    "아니다 (-1)",
    "전혀 아니다 (-2)",
]

SCALE = {
    CHOICES[0]: 2,
    CHOICES[1]: 1,
    CHOICES[2]: 0,
    CHOICES[3]: -1,
    CHOICES[4]: -2,
}

# -------------------- 상태 초기화 --------------------
if "answers" not in st.session_state:
    st.session_state.answers = {}  # (axis, idx) -> choice
if "finished" not in st.session_state:
    st.session_state.finished = False
if "result" not in st.session_state:
    st.session_state.result = None

# -------------------- 설문 렌더링 --------------------
total_items = sum(len(v) for v in QUESTIONS.values())
answered = sum(1 for _k, v in st.session_state.answers.items() if v is not None)

st.progress(answered / total_items, text=f"{answered}/{total_items} 완료")

idx_counter = 0
for axis, items in QUESTIONS.items():
    st.subheader(f"🎯 {axis} 지표")
    for i, (q, reverse) in enumerate(items, start=1):
        idx_counter += 1
        key = (axis, i)
        with st.container(border=True):
            st.write(f"Q{idx_counter:02d}. {q}")
            st.session_state.answers[key] = st.radio(
                "선택", CHOICES,
                index=2 if key not in st.session_state.answers else CHOICES.index(st.session_state.answers[key]),
                horizontal=True,
                key=f"radio-{axis}-{i}",
                label_visibility="collapsed"
            )

st.divider()

# -------------------- 점수 계산 --------------------
def score_mbti(answers):
    # 축별 합산
    raw = {"EI": 0, "SN": 0, "TF": 0, "JP": 0}
    for axis, items in QUESTIONS.items():
        for i, (_q, reverse) in enumerate(items, start=1):
            choice = answers.get((axis, i))
            if choice is None:
                continue
            val = SCALE[choice]
            if reverse:
                val = -val
            raw[axis] += val

    # 축별 부호로 글자 결정
    # EI: +면 E, -면 I / SN: +면 S, -면 N (주의: 일반 MBTI는 S vs N이지만 여기선 +를 S로)
    # TF: +면 T, -면 F / JP: +면 J, -면 P
    # 0이면 중간값 -> 우측 글자로 치우치지 않도록 규칙 설정(0은 앞글자)
    letters = []
    letters.append("E" if raw["EI"] >= 0 else "I")
    letters.append("S" if raw["SN"] >= 0 else "N")
    letters.append("T" if raw["TF"] >= 0 else "F")
    letters.append("J" if raw["JP"] >= 0 else "P")
    return "".join(letters), raw

# -------------------- 결과 사전 --------------------
LEARNING_PROFILES = {
    "ISTJ": {
        "label": "체계적 실천가",
        "desc": "계획과 규칙에 강점. 체크리스트와 예제 반복으로 탄탄히 실력 쌓기.",
        "tips": [
            "단원별 체크리스트로 진도 관리",
            "예제 → 변형문제 → 서술형 순서로 난이도 상승",
            "오답노트에 ‘왜 틀렸는지’ 원인 기록"
        ],
    },
    "ISFJ": {
        "label": "성실한 서포터",
        "desc": "세심하고 꾸준함. 루틴과 자료정리로 안정감 있게 학습.",
        "tips": [
            "매일 같은 시간 25분 집중(포모도로) + 5분 정리",
            "요약 노트에 키워드-정의-예시 고정 포맷",
            "친구에게 설명하며 복습(티칭 효과)"
        ],
    },
    "INFJ": {
        "label": "통찰형 설계자",
        "desc": "핵심 의미를 파악해 구조화. 큰 그림 → 세부 구현에 강함.",
        "tips": [
            "개념지도를 그려 흐름 정리",
            "‘왜 중요한가?’ 질문으로 본질 점검",
            "프로젝트형 과제로 응용"
        ],
    },
    "INTJ": {
        "label": "전략가 플래너",
        "desc": "목표 지향적. 최소 노력으로 최대 효과를 설계.",
        "tips": [
            "시험 역산 스케줄(마감→주간→일간)",
            "핵심 20% 개념에 우선순위",
            "약점 과목은 ‘원인-대안’ 실험 로그"
        ],
    },
    "ISTP": {
        "label": "문제 해결 장인",
        "desc": "손으로 부딪치며 배우는 유형. 실습/코딩/실험 적합.",
        "tips": [
            "이론 30% → 실습 70% 비율",
            "디버깅/오류 노트 관리",
            "짧은 과제 여러 번 제출"
        ],
    },
    "ISFP": {
        "label": "감각적 탐색가",
        "desc": "차분하고 감각지향. 예시·케이스로 이해.",
        "tips": [
            "사례→개념→정리 순서",
            "시각 자료(도표/그림) 활용",
            "조용한 개인학습 공간 확보"
        ],
    },
    "INFP": {
        "label": "의미 추구자",
        "desc": "가치와 의미를 찾을 때 몰입. 글쓰기/프로젝트 학습에 강점.",
        "tips": [
            "학습 목표를 ‘나의 가치’와 연결",
            "저널링으로 배운 점/느낀 점 기록",
            "창작형 과제(포스터·블로그)로 확장"
        ],
    },
    "INTP": {
        "label": "개념 탐구자",
        "desc": "개념 간 연결·이론화에 강함. 깊게 파고드는 스타일.",
        "tips": [
            "정의-정리-증명 흐름으로 정리",
            "‘반례’ 찾기 훈련",
            "스터디에서 개념 질의응답 리드"
        ],
    },
    "ESTP": {
        "label": "액션 러너",
        "desc": "빠른 실행과 피드백 선호. 실전 문제로 배우기.",
        "tips": [
            "시간 제한 모의고사로 실전감각",
            "오답 유형별 즉시 처치",
            "성과 로그(점수, 소요시간) 기록"
        ],
    },
    "ESFP": {
        "label": "에너지 메이커",
        "desc": "사교적·현장형 학습. 활동 중심 과제 선호.",
        "tips": [
            "스몰 그룹 스터디 진행",
            "퀴즈/게임화로 동기 부여",
            "발표·티칭으로 아웃풋 내기"
        ],
    },
    "ENFP": {
        "label": "아이디어 점프러",
        "desc": "다양한 관심사와 창의성. 흥미 연결이 핵심.",
        "tips": [
            "학습 목표를 프로젝트와 연결",
            "할 일은 3가지 이하로 제한",
            "‘시작 장벽’을 낮추는 5분 규칙"
        ],
    },
    "ENTP": {
        "label": "토론형 혁신가",
        "desc": "질문과 반박으로 배우는 유형. 토의·디베이트 적합.",
        "tips": [
            "개념마다 ‘왜?’ 3회 질문",
            "상반된 관점 비교 표 만들기",
            "발표 과제로 정리"
        ],
    },
    "ESTJ": {
        "label": "운영 매니저",
        "desc": "규율·체계·실행력. 계획대로 밀어붙이는 힘.",
        "tips": [
            "주간 계획-일일 점검 루틴",
            "과제 체크리스트 완료율 관리",
            "학습 공간/자료 정리 시스템화"
        ],
    },
    "ESFJ": {
        "label": "협력 코디네이터",
        "desc": "사람 중심 협업형. 함께할 때 시너지.",
        "tips": [
            "역할 분담형 스터디",
            "피드백 교환 루틴",
            "서로 가르치기(페어 티칭)"
        ],
    },
    "ENFJ": {
        "label": "코치 리더",
        "desc": "동기 부여·조직화 강점. 팀 프로젝트에 적합.",
        "tips": [
            "팀 목표-역할-마감 명확화",
            "피어 리뷰 체크리스트",
            "성과 공유 시간 운영"
        ],
    },
    "ENTJ": {
        "label": "지휘 전략가",
        "desc": "목표 설정·자원 배치에 강함. 성과 중심.",
        "tips": [
            "OKR 방식(목표-핵심결과) 적용",
            "생산성 지표(시간/점수) 추적",
            "리소스(교재/도구) 최적 조합"
        ],
    },
}

def profile_for(mbti: str):
    # 없는 조합일 경우에 대비 (기본 안내)
    return LEARNING_PROFILES.get(mbti, {
        "label": "맞춤 프로필",
        "desc": "당신의 응답을 바탕으로 학습 성향을 요약했습니다.",
        "tips": ["핵심 개념 먼저 정리", "오답 원인 기록", "주 1회 메타인지 점검"],
    })

# -------------------- 버튼 영역 --------------------
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🧮 결과 계산", type="primary"):
        if any(v is None for v in st.session_state.answers.values()) or len(st.session_state.answers) < total_items:
            st.warning("모든 문항에 응답해주세요.")
        else:
            mbti, raw = score_mbti(st.session_state.answers)
            st.session_state.result = {"mbti": mbti, "raw": raw, "at": datetime.now().isoformat()}
            st.session_state.finished = True
with col2:
    if st.button("🔁 초기화"):
        st.session_state.answers = {}
        st.session_state.finished = False
        st.session_state.result = None
        st.experimental_rerun()
with col3:
    if st.session_state.result:
        result_txt = textwrap.dedent(f"""
        [8비트 학습 성향 진단 결과]
        MBTI: {st.session_state.result['mbti']}
        점수 합계: {st.session_state.result['raw']}
        측정시각: {st.session_state.result['at']}
        """).strip()
        st.download_button("💾 결과 텍스트 저장", data=result_txt.encode("utf-8"), file_name="learning_mbti_result.txt")
        st.download_button("💾 결과 JSON 저장", data=json.dumps(st.session_state.result, ensure_ascii=False, indent=2), file_name="learning_mbti_result.json")

st.write("")

# -------------------- 결과 표시 --------------------
if st.session_state.finished and st.session_state.result:
    mbti = st.session_state.result["mbti"]
    raw = st.session_state.result["raw"]
    prof = profile_for(mbti)

    st.markdown(f"## 🧠 결과: **{mbti}**")
    st.markdown(
        f"<div class='retro-card'>"
        f"<div class='retro-chip'>E/I: {raw['EI']:+d}</div>"
        f"<div class='retro-chip'>S/N: {raw['SN']:+d}</div>"
        f"<div class='retro-chip'>T/F: {raw['TF']:+d}</div>"
        f"<div class='retro-chip'>J/P: {raw['JP']:+d}</div>"
        f"<br><br><b>{prof['label']}</b><br>{prof['desc']}"
        f"</div>",
        unsafe_allow_html=True
    )

    st.markdown("### 🔧 공부 팁")
    for t in prof["tips"]:
        st.markdown(f"- {t}")

    st.info(
        "⚠️ 이 진단은 학습 성향을 **참고**하기 위한 도구입니다. "
        "상황/과목에 따라 전략을 달리 적용해 보세요."
    )
else:
    st.markdown(
        "<span class='small'>※ ‘결과 계산’을 누르면 MBTI 유형과 맞춤 학습 팁이 표시됩니다.</span>",
        unsafe_allow_html=True
    )

st.markdown("---")
with st.expander("⚙️ 커스터마이즈 방법"):
    st.markdown("""
- **문항 바꾸기:** `QUESTIONS` 딕셔너리에서 텍스트 수정, `reverse=True`로 역채점 설정  
- **척도 변경:** `CHOICES`와 `SCALE` 맵 바꾸면 됨  
- **프로필 설명/팁 변경:** `LEARNING_PROFILES`에서 유형별 텍스트 수정  
- **UI 색상:** 상단 CSS의 `--retro-*` 변수 조정  
- **주의:** 이 앱은 재미/자기이해용 도구로, 과학적 진단 대신 **학습 전략 인사이트** 제공을 목표로 합니다.
""")
# 앱 코드 제일 마지막 부분에 추가
st.markdown(
    """
    <hr style="margin-top:50px; margin-bottom:10px; border: 1px solid #334155;">
    <div style='text-align: center; font-size: 12px; color: #94a3b8;'>
        © 2025 이대형. All rights reserved.<br>
        <a href="https://aicreatorz.netlify.app/" target="_blank" style="color:#22d3ee; text-decoration: none;">
            https://aicreatorz.netlify.app/
        </a>
    </div>
    """,
    unsafe_allow_html=True
)
