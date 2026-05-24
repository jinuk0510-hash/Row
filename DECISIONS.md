# 프로젝트 의사결정 & 핵심 지식 기록

> 이 문서는 대화에서 나온 **중요한 결정, 발견, 근거**를 정리한 것입니다.
> 프롬프트 원문은 `prompts_history.md` 참고.
> 최종 갱신: 2026-05-17

---

## 0. 프로젝트 개요

- **무엇**: 실내조정(Concept2 에르고미터) 사용자를 위한 개인 맞춤 트레이닝 코치 웹앱
- **MVP**: 개인 코치형 — 내 2k 기록 기반으로 검증된 Pete Plan을 자동 처방
- **차별점**: 임의 알고리즘 X. 검증된 Pete Plan + Concept2 공식 Watts 공식 기반

---

## 1. 프로젝트 방향 전환 (보디빌딩 → 로잉)

- 처음엔 보디빌딩 4대운동(벤치/스쿼트/데드/OHP) 무게 추천 앱이었음
- **로잉 트레이닝 앱으로 전환** — 4대운동은 폐기
- 거리: 500m / 1k / 2k (추천 핵심), 5k / 10k (기록 전용)

---

## 2. 핵심 원칙: 모든 설계는 레퍼런스 기반 (★★★)

> **임의의 숫자/처방 금지. 모든 공식·페이스·처방은 공식 자료/논문/검증된 프로그램 출처를 명시.**

- 사용자가 명시적으로 요구한 최우선 원칙
- 적용 예: Watts 공식(Concept2 공식), Pete Plan 페이스(블로그+포럼), 출처를 코드 주석/UI에 명시
- **교훈**: Claude가 기억에 의존해 만든 Standard 플랜이 실제와 달랐음 → 반드시 1차 출처 확인 후 구현

---

## 3. TRAINING / RECORD 분리 (★★)

**문제**: 기록을 저장할 때마다 추천 페이스가 자동으로 바뀌면 통제 불가.

**결정**:
- 훈련 목표는 **"기준 2k"(reference 2k)** 라는 명시적 값에만 의존
- 기록(Log)에 새 PR을 저장해도 **자동 갱신 안 됨**
- 새 PR 시 "기준 갱신할래요?" 버튼만 띄우고, 사용자가 누를 때만 반영
- 이게 Pete Plan 본래 방식과도 일치 (2k 테스트 시점에만 기준 갱신)

---

## 4. Pete Plan 정확한 구조 (출처: thepeteplan.wordpress.com + Concept2 Forum)

### 두 가지 버전
| 버전 | 대상 | 구조 |
|---|---|---|
| **Beginner** | 입문자 | 24주 progression, 매주 core 3 + optional 2 |
| **Standard** | 중급+ (베이스 있음) | 3주 사이클, 주 7세션(6훈련+1휴식) |

### Standard Pete Plan (3주 사이클) — 7일 고정 배치 (★ 정정됨)
거리 세션 4개가 다 똑같은 게 아님. **하드 3 + 스테디 3 + 휴식 1**:

| Day | 세션 |
|---|---|
| Day 1 | 스피드 인터벌 (주차별 로테이션) |
| Day 2 | Steady distance (8~15km, 이지) |
| Day 3 | 지구력 인터벌 (주차별 로테이션) |
| Day 4 | Steady distance |
| **Day 5** | **Hard distance (5k+)** — 거리 4개 중 이것만 하드 |
| Day 6 | Steady distance |
| Day 7 | 완전 휴식 |

- **Steady 목적 = 회복** (다음날 하드 세션 위해). 지구력 인터벌보다 10초+ 느리게, 22~25 spm, "헷갈리면 더 느리게"
- 처음엔 거리 4개를 동일 스테디로 잘못 구현 → 7일 배치로 정정

| 주차 | 스피드 인터벌 (Day1) | 지구력 인터벌 (Day3) |
|---|---|---|
| Week 1 | 8 × 500m / 3:30R | 5 × 1500m / 5:00R |
| Week 2 | 250-500-750-1k-750-500-250 / 1:30R per 250m | 4 × 2000m / 5:00R |
| Week 3 | 4 × 1000m / 5:00R | 3k, 2.5k, 2k / 5:00R |

### 페이스 — 전부 2k PB 기준 (★ 사용자 요청대로 3주 내내 PR 고정)
| 세션 | 타겟 (2k 페이스 대비) | SPM |
|---|---|---|
| 8 × 500m | 2k − 3초 | 32–36 |
| 피라미드 | ≈2k 페이스 (일정→가속) | 30–34 |
| 4 × 1000m | 2k + 1초 | 30–34 |
| 5 × 1500m | 2k + 5~7초 (≈5k 페이스) | 28–32 |
| 4 × 2000m | 2k + 5~7초 (≈5k 페이스) | 28–30 |
| 3k·2.5k·2k | 2k + 5~7초 (≈5k 페이스) | 28–30 |
| Distance/Steady | ≈10k 페이스 +5~7초 | 22–25 |

- 출처: 8×500/4×1000/5×1500은 블로그 명시, 나머지는 Concept2 Forum 컨센서스
- 코드엔 +6초를 +5~7 밴드의 중간값으로 사용

### Beginner Pete Plan (24주)
- 매주 core 3개(필수) + optional 2개(여유될 때)
- 1~11주: 거리 +500m/주 증가 / 12~15주: 10000m 유지·페이스 집중 / 16~20주: 거리 재증가 / 21~24주: 2k 테스트 준비
- 첫 사이클은 모든 세션 절반으로 줄여도 됨
- 페이스: progressive (지난 기록 갱신)
- 24주 전체 표는 `index.html`의 `BEGINNER_PLAN`에 verbatim 저장됨

---

## 5. Beginner ↔ Standard 전환 기준 (★)

> **고정 2k 시간 컷오프(예: 7:07)는 안 됨** — 나이/체중/성별 따라 달라서 보편 기준 불가.

**Pete Plan 실제 기준 = 능력(capability), 기록 아님**:
- 구조적 훈련 3개월+
- 30분 연속 로잉 편안
- 인터벌 경험 있음
- Standard 8×500m을 목표 페이스로 완주 가능

→ 앱에 4문항 자가진단 구현 (3개 이상 체크 → Standard 추천)
→ 객관 지표 원하면 Concept2 공식 랭킹(나이·체급·성별 백분위)이 유일하게 신뢰 가능한 출처

---

## 6. Watts 공식 (Concept2 공식)

```
W = 2.80 / (pace_sec_per_meter)³
```
- 페이스를 출력값으로 변환하는 공식 (concept2.com 명시)
- 의미: 1:35 → 1:30 (500m)은 출력 약 **+18%** 필요 → 이게 앱의 핵심 동기부여 포인트

---

## 7. Pete Marston (Pete Plan 제작자) 신뢰성 (★)

처음엔 "취미 로워"로 잘못 평가 → LinkedIn 확인 후 정정:

- 🏆 **100km 세계기록 보유자**
- 🏆 **GB(영국) 국가대표 인도어 로잉 팀 코치** (2011–2013)
- 🎓 **King's College London** 객원 부교수, **응용생리학 박사 지도교수**
- 🎓 Chartered Mathematician + Chartered Ergonomist (수학·인간공학 전문가)
- 🛡️ Martin-Baker(항공 사출좌석) Head of Human Engineering / QinetiQ 수석과학자 10년
- Pete Plan Coaching 18년 운영

→ **"검증된 시스템"이라 부를 충분한 근거.** 학술 + 실전 + 본업 모두 입증.

---

## 8. 운동 강도 / 실패 처리

- Standard는 빡센 게 정상 (입문자용 아님). 특히 4×2000m(지구력)이 가장 빡셈
- **양극화(Polarized)**: 하드 3일은 진짜 빡세게, 스테디 2일은 진짜 가볍게(대화 가능 수준)
- 흔한 실수: 스테디 데이를 너무 세게 탐
- **세션 실패 시**: 끝까지 완주 → 2회 연속 실패면 **기준 2k가 너무 높은 것** → 5~10초 늦춰서 재시도
- "매 세션 죽을 것 같으면" 뭔가 잘못된 것 (기준 과대 / Beginner 필요 / 스테디 과부하)

---

## 9. 기술 아키텍처 결정

- **정적 HTML 단일 페이지 앱** (`index.html`) — Streamlit 설치/서버 불필요, 더블클릭으로 구동
  - 이유: 사용자가 빠른 검증 원함, 모바일 접근성
- **저장소: 브라우저 localStorage** (데모용)
  - 한계: 기기/브라우저 간 데이터 동기화 안 됨 → 추후 클라우드 DB 필요
- **사진 자동 인식(OCR)**: Claude Vision으로 가능하나 장당 ~$0.01 → 사용자가 수동 입력 선택
- **클로즈 베타**: 회원가입 제거, 바로 구동 (개인 검증 목적)
- 모바일 접속: Netlify Drop 권장 (폴더 드래그 → URL)
- **주차 진행**: 날짜 기반 X → **플랜별 독립 카운터** (`plan_progress_standard/beginner`), "Mark Complete"로 수동 진행, 리셋 버튼 제공

### Python 파일 (`app.py`, `database.py`, `pace_calc.py`, `pete_plan.py`)
- Streamlit 버전. 추후 백엔드 붙일 때 재사용 가능하도록 보존
- ⚠️ Python 쪽 `pete_plan.py`는 구버전 페이스(부정확)일 수 있음 — 정확한 최신본은 `index.html` 기준

---

## 10. 작업 규칙 (CLAUDE.md)

- 코드 수정 전 계획 먼저 설명
- 한 번에 하나의 파일만 수정
- 수정 후 변경 부분 요약
- 매 프롬프트마다 `prompts_history.md`에 append
- 모든 설계는 공식 자료 기반
- 설명은 한국어

---

## 부록: 출처 모음
- Standard Pete Plan: https://thepeteplan.wordpress.com/the-pete-plan/
- Beginner Pete Plan: https://thepeteplan.wordpress.com/beginner-training/
- Pete Plan 페이싱 컨센서스: Concept2 Forum (c2forum.com)
- Watts 공식: https://www.concept2.com/indoor-rowers/training/calculators/watts-calculator
- Pete Marston 약력: LinkedIn
