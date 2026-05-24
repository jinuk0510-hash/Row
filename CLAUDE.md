# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

보디빌딩 경력 6개월 이상 사용자를 위한 개인 맞춤 헬스 기록 및 무게 추천 앱.

- **스택**: Python + Streamlit + SQLite
- **지원 종목**: 벤치프레스, 스쿼트, 데드리프트, OHP (4종목 고정)

## 실행 명령어

```bash
# 의존성 설치
pip install streamlit

# 앱 실행
streamlit run app.py
```

## 프로젝트 구조

```
fitness-pt/
├── app.py          # Streamlit 진입점 및 페이지 라우팅
├── database.py     # SQLite 연결 및 CRUD 함수
├── recommender.py  # 다음 세션 무게 추천 로직
└── fitness.db      # SQLite DB 파일 (자동 생성)
```

## 아키텍처

- `app.py` — UI 레이어. Streamlit 페이지(기록 입력 / 히스토리 / 추천) 구성
- `database.py` — DB 레이어. 테이블 초기화, 기록 저장, 히스토리 조회 함수 제공
- `recommender.py` — 비즈니스 로직. 최근 기록을 받아 다음 목표 무게를 계산

## 추천 로직 규칙

| 조건 | 기본 적용 |
|------|-----------|
| 횟수 증가 + 상체(벤치/OHP) | +2.5kg |
| 횟수 증가 + 하체(스쿼트/데드) | +5kg |
| 횟수 유지 또는 감소 | 유지 |
| 컨디션 하 | 한 단계 낮춰 적용 (증가 → 유지, 유지 → -해당 증분) |
| 컨디션 상 | 한 단계 높여 적용 (유지 → 증가, 증가 → +추가 증분) |

## 작업 원칙

- 코드 수정 전 반드시 계획 먼저 설명할 것
- 한 번에 하나의 파일만 수정할 것
- 수정 후 변경된 부분 요약할 것
- 요청하지 않은 파일은 건드리지 말 것
- 설명은 한국어로 할 것
- **매 사용자 프롬프트마다 `prompts_history.md` 파일 맨 아래에 새 항목으로 append할 것** (번호 + 코드블록 형식)
- **모든 프로그램 설계/공식/처방은 공식 자료(Concept2 공식 문서, 출판된 트레이닝 프로그램, 논문 등) 기반으로 할 것. 임의의 숫자나 처방은 금지. 출처를 코드 주석이나 설명에 명시할 것**
- **중요한 의사결정·발견·근거(설계 변경, 페이스 출처, 신뢰성 근거 등)는 `DECISIONS.md`에 정리/갱신할 것** (`prompts_history.md`는 프롬프트 원문, `DECISIONS.md`는 핵심 지식)

## 코드 스타일

- 변수명: 영어 `snake_case`
- 주석: 한국어
- 파일 수정 시 변경된 부분만 표시
