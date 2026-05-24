# 종목별 무게 증분 (kg)
INCREMENTS = {
    "벤치프레스": 2.5,
    "OHP":       2.5,
    "스쿼트":    5.0,
    "데드리프트": 5.0,
}


def recommend_weight(exercise: str, last_log: dict, current_reps: int, current_condition: str) -> dict:
    """
    다음 세션 목표 무게 추천.

    매개변수:
        exercise         : 종목명
        last_log         : 이전 기록 딕셔너리 (weight, reps 포함)
        current_reps     : 오늘 수행한 횟수
        current_condition: 오늘 컨디션 ('상' / '중' / '하')

    반환:
        {
            "next_weight": float,   # 추천 무게
            "reason": str           # 추천 이유 설명
        }
    """
    increment = INCREMENTS[exercise]
    last_weight = last_log["weight"]
    last_reps = last_log["reps"]

    # 1단계: 횟수 비교로 기본 방향 결정
    if current_reps > last_reps:
        base_delta = increment   # 무게 올리기
        base_reason = f"횟수 증가({last_reps}→{current_reps}회) → +{increment}kg"
    else:
        base_delta = 0           # 유지
        base_reason = f"횟수 유지/감소({last_reps}→{current_reps}회) → 무게 유지"

    # 2단계: 컨디션 보정
    if current_condition == "상":
        # 유지 → 올리기 / 올리기 → 두 단계 올리기
        adjusted_delta = base_delta + increment
        condition_note = "컨디션 상 → 한 단계 적극 적용"
    elif current_condition == "하":
        # 올리기 → 유지 / 유지 → 내리기
        adjusted_delta = base_delta - increment
        condition_note = "컨디션 하 → 한 단계 보수적 적용"
    else:  # 중
        adjusted_delta = base_delta
        condition_note = None

    next_weight = last_weight + adjusted_delta

    # 무게는 0보다 작아질 수 없음
    next_weight = max(next_weight, increment)

    # 추천 이유 조합
    reason_parts = [base_reason]
    if condition_note:
        reason_parts.append(condition_note)
    reason_parts.append(f"최종 추천: {last_weight}kg → {next_weight}kg")

    return {
        "next_weight": next_weight,
        "reason": " / ".join(reason_parts),
    }
