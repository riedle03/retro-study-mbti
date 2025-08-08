```markdown
# 🕹️ 8bit Learning Style MBTI Test

**레트로(8비트) 게임 스타일**로 구성된 **학습 성향 MBTI 진단 검사**입니다.  
12문항을 통해 E/I, S/N, T/F, J/P 4지표를 측정하고,  
MBTI 기반의 학습 유형과 맞춤 공부 팁을 제공합니다.

![screenshot](docs/screenshot.png)

---

## ✨ 특징

- 🎨 **8비트 감성 UI** (Press Start 2P 폰트 + 레트로 색감)
- 🧠 **MBTI 기반 학습 성향 진단** (4지표, 16유형)
- 📊 지표별 점수 시각화 (E/I, S/N, T/F, J/P)
- 💡 유형별 맞춤 학습 팁 제공
- 💾 결과 저장 (`.txt`, `.json` 다운로드 가능)
- 🔄 초기화 기능으로 재검사 가능

---

## 📂 프로젝트 구조

```

.
├── streamlit\_app.py   # 메인 앱
├── requirements.txt   # 필요 패키지 목록
├── docs/
│   └── screenshot.png # 실행 화면 스크린샷
└── README.md

````

---

## 🛠 설치 및 실행 방법

### 1. 저장소 클론
```bash
git clone https://github.com/username/repo-name.git
cd repo-name
````

### 2. 가상환경(선택)

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

> `requirements.txt` 내용:
>
> ```
> streamlit
> ```

### 4. 앱 실행

```bash
streamlit run streamlit_app.py
```

---

## 📖 사용 방법

1. 앱 실행 후 **문항에 모두 응답**하세요.
2. `🧮 결과 계산` 버튼 클릭
3. MBTI 유형과 학습 유형 설명, 공부 팁 확인
4. 필요하면 `.txt` 또는 `.json`으로 결과 다운로드

---

## 🎯 예시 화면

| 질문 화면                    | 결과 화면                  |
| ------------------------ | ---------------------- |
| ![질문](docs/question.png) | ![결과](docs/result.png) |

---

## 🧩 커스터마이징

* **문항 변경:** `QUESTIONS` 딕셔너리 수정
* **척도 변경:** `CHOICES`와 `SCALE` 값 수정
* **유형 설명 변경:** `LEARNING_PROFILES` 딕셔너리 수정
* **UI 색상 변경:** 상단 CSS에서 `--retro-*` 변수 조정

---

## ⚠️ 주의사항

* 본 테스트는 **재미/자기 이해용**이며, 과학적·의학적 진단 도구가 아닙니다.
* 결과를 참고하여 학습 전략을 설계하되, 다양한 방법을 시도해 보세요.

---

## 📜 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.
자유롭게 수정, 재배포 가능합니다.

```
