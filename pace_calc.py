"""
페이스/Watts/시간 변환 유틸리티.

Watts 공식 출처:
  Concept2 공식 — concept2.com/indoor-rowers/training/calculators/watts-calculator
  W = 2.80 / (pace_sec_per_meter)^3
  단, pace_sec_per_meter = (500m당 페이스 초) / 500
"""

# ─────────────────────────────────────────────
# Watts ↔ Pace 변환 (Concept2 공식)
# ─────────────────────────────────────────────

def pace_to_watts(pace_sec_per_500m: float) -> float:
    """500m당 페이스(초) → Watts"""
    if pace_sec_per_500m <= 0:
        return 0.0
    pace_per_meter = pace_sec_per_500m / 500.0
    return 2.80 / (pace_per_meter ** 3)


def watts_to_pace(watts: float) -> float:
    """Watts → 500m당 페이스(초)"""
    if watts <= 0:
        return 0.0
    pace_per_meter = (2.80 / watts) ** (1.0 / 3.0)
    return pace_per_meter * 500.0


# ─────────────────────────────────────────────
# 시간 포맷 변환
# ─────────────────────────────────────────────

def sec_to_mmss(total_sec: float) -> str:
    """초 → 'M:SS.s' 포맷"""
    if total_sec is None:
        return "-"
    minutes = int(total_sec // 60)
    seconds = total_sec - minutes * 60
    return f"{minutes}:{seconds:04.1f}"


def mmss_to_sec(mmss: str) -> float:
    """'M:SS' 또는 'M:SS.s' → 초"""
    parts = mmss.strip().split(":")
    if len(parts) != 2:
        raise ValueError(f"잘못된 시간 포맷: {mmss}")
    return int(parts[0]) * 60 + float(parts[1])


# ─────────────────────────────────────────────
# 평균 스플릿 계산
# ─────────────────────────────────────────────

def calc_avg_split(distance_m: int, total_time_sec: float) -> float:
    """완주 시간 → 500m당 평균 스플릿 (초)"""
    if distance_m <= 0:
        return 0.0
    return total_time_sec * 500.0 / distance_m


def calc_total_from_split(distance_m: int, split_sec_per_500m: float) -> float:
    """500m당 페이스 → 완주 예상 시간(초)"""
    return split_sec_per_500m * distance_m / 500.0
