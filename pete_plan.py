"""
Pete Plan (Standard) 워크아웃 정의 및 목표 페이스 계산.

출처:
  Pete Marston — thepeteplan.wordpress.com
  Standard Pete Plan: 주 5세션 (하드 3 + Steady State 2), 3주 로테이션.

목표 페이스 오프셋(2k PR 페이스 기준)은 Pete Plan 블로그에서 통용되는
가이드라인을 사용. 데모 버전이며 사용자 본인 데이터에 맞춰 조정 가능.
"""

from datetime import date, datetime

from pace_calc import calc_avg_split


# ─────────────────────────────────────────────
# Pete Plan 하드 세션 정의 (3주 로테이션)
# 출처: thepeteplan.wordpress.com (Standard Pete Plan)
# ─────────────────────────────────────────────

# 각 세션:
#   name              : 표시명
#   workout_type      : DB 저장용 (AT/VO2/AN/UT2/TEST)
#   intervals         : [(거리_m, 휴식_초), ...] 또는 단일 거리
#   pace_offset_sec   : 2k 페이스 대비 오프셋 (음수=빠르게, 양수=느리게)
#   description       : 사용자 안내 문구

PETE_PLAN_WEEKS = [
    # ── Week 1 ──
    {
        "week": 1,
        "hard_sessions": [
            {
                "name": "8 × 500m / 3:30R",
                "workout_type": "VO2",
                "intervals": [(500, 210)] * 8,   # 210초 = 3:30
                "pace_offset_sec": -3,
                "description": "단거리 인터벌. 2k 페이스보다 약 3초 빠르게.",
            },
            {
                "name": "4 × 2000m / 5:00R",
                "workout_type": "AT",
                "intervals": [(2000, 300)] * 4,
                "pace_offset_sec": +5,
                "description": "임계점 세션. 2k 페이스보다 약 5초 느리게.",
            },
            {
                "name": "5000m hard",
                "workout_type": "TEST",
                "intervals": [(5000, 0)],
                "pace_offset_sec": +6,
                "description": "5k 하드 거리. 2k 페이스 +6초 목표.",
            },
        ],
    },
    # ── Week 2 ──
    {
        "week": 2,
        "hard_sessions": [
            {
                "name": "4 × 1000m / 5:00R",
                "workout_type": "VO2",
                "intervals": [(1000, 300)] * 4,
                "pace_offset_sec": -1,
                "description": "중거리 인터벌. 2k 페이스보다 약 1초 빠르게.",
            },
            {
                "name": "4 × 2000m / 5:00R",
                "workout_type": "AT",
                "intervals": [(2000, 300)] * 4,
                "pace_offset_sec": +5,
                "description": "임계점 세션. 2k 페이스보다 약 5초 느리게.",
            },
            {
                "name": "6000m hard",
                "workout_type": "TEST",
                "intervals": [(6000, 0)],
                "pace_offset_sec": +7,
                "description": "6k 하드 거리. 2k 페이스 +7초 목표.",
            },
        ],
    },
    # ── Week 3 ──
    {
        "week": 3,
        "hard_sessions": [
            {
                "name": "5 × 1500m / 5:00R",
                "workout_type": "AT",
                "intervals": [(1500, 300)] * 5,
                "pace_offset_sec": +1,
                "description": "중장거리 인터벌. 2k 페이스 +1초 목표.",
            },
            {
                "name": "4 × 2000m / 5:00R",
                "workout_type": "AT",
                "intervals": [(2000, 300)] * 4,
                "pace_offset_sec": +5,
                "description": "임계점 세션. 2k 페이스 +5초 목표.",
            },
            {
                "name": "8000m hard",
                "workout_type": "TEST",
                "intervals": [(8000, 0)],
                "pace_offset_sec": +8,
                "description": "8k 하드 거리. 2k 페이스 +8초 목표.",
            },
        ],
    },
]

# Steady State (UT2) — 주 2회 공통
# 출처: Pete Plan 일반 가이드 — UT2 = 2k 페이스 + 약 20초/500m
STEADY_STATE_SESSION = {
    "name": "Steady State 40~70분",
    "workout_type": "UT2",
    "intervals": None,                  # 시간 기반
    "duration_range_min": (40, 70),
    "pace_offset_sec": +20,
    "stroke_rate_range": (18, 20),      # Pete Plan 권장 spm
    "description": "UT2 베이스. 2k 페이스 +20초/500m, 18~20 spm 유지.",
}


# ─────────────────────────────────────────────
# 목표 페이스 계산
# ─────────────────────────────────────────────

def calc_target_split(pr_2k_total_sec: float, offset_sec: float) -> float:
    """
    2k PR 시간 → 해당 세션의 목표 500m 스플릿(초).

    예) 2k PR이 7:30 (450초)이면 2k 평균 스플릿 = 112.5초 (1:52.5)
        offset +5초 → 목표 117.5초 (1:57.5/500m)
    """
    base_split = calc_avg_split(2000, pr_2k_total_sec)
    return base_split + offset_sec


def get_week_plan(week_index_1to3: int) -> dict:
    """주차(1~3)의 Pete Plan 세션 목록 반환"""
    if week_index_1to3 not in (1, 2, 3):
        raise ValueError("week_index는 1, 2, 3 중 하나여야 합니다.")
    return PETE_PLAN_WEEKS[week_index_1to3 - 1]


def get_current_week_index(plan_start_date_str: str, today: date = None) -> int:
    """
    Pete Plan 시작일 기준 현재 주차(1~3) 반환.

    매개변수:
        plan_start_date_str : 'YYYY-MM-DD' 포맷
        today               : 기준 날짜 (없으면 오늘)

    Pete Plan은 3주 사이클이므로 (경과주 % 3) + 1.
    세션 기록 추가/삭제는 주차에 영향을 주지 않음(달력 기반).
    """
    if today is None:
        today = date.today()
    start = datetime.strptime(plan_start_date_str, "%Y-%m-%d").date()
    days_elapsed = (today - start).days
    if days_elapsed < 0:
        return 1  # 시작 전이면 Week 1으로 표시
    weeks_elapsed = days_elapsed // 7
    return (weeks_elapsed % 3) + 1
