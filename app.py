"""
fitness-pt — 실내조정(Concept2) 트레이닝 앱 (Pete Plan 데모)
"""
import streamlit as st
import pandas as pd

from datetime import date

from database import (
    init_db, save_rowing_log, get_rowing_history, get_pr, get_recent_logs,
    save_goal, get_active_goals, deactivate_goal,
    get_setting, set_setting,
    DISTANCES, RECOMMEND_DISTANCES, WORKOUT_TYPES, GOAL_TYPES,
)
from pace_calc import (
    pace_to_watts, watts_to_pace,
    sec_to_mmss, mmss_to_sec,
    calc_avg_split,
)
from pete_plan import (
    PETE_PLAN_WEEKS, STEADY_STATE_SESSION,
    calc_target_split, get_week_plan, get_current_week_index,
)

# DB 초기화
init_db()

st.set_page_config(page_title="로잉 트레이닝", page_icon="🚣", layout="centered")
st.title("🚣 로잉 트레이닝 (Pete Plan)")

# 사이드바
page = st.sidebar.radio(
    "메뉴",
    ["대시보드", "세션 기록", "히스토리", "목표 설정"],
)
st.sidebar.divider()
st.sidebar.caption(
    "프로그램: **Standard Pete Plan**  \n"
    "출처: thepeteplan.wordpress.com  \n"
    "Watts 공식: Concept2 공식"
)


# ─────────────────────────────────────────────
# 페이지 1: 대시보드
# ─────────────────────────────────────────────
if page == "대시보드":
    st.header("🏠 대시보드")

    # 거리별 PR 표시
    st.subheader("거리별 PR")
    pr_cols = st.columns(len(DISTANCES))
    for col, dist in zip(pr_cols, DISTANCES):
        pr = get_pr(dist)
        with col:
            label = f"{dist}m" if dist < 1000 else f"{dist // 1000}k"
            if pr:
                col.metric(label, sec_to_mmss(pr["total_time_sec"]))
            else:
                col.metric(label, "-")

    st.divider()

    # ── Pete Plan 셋업 (기준 2k + 시작일) ──
    st.subheader("⚙️ Pete Plan 셋업")
    ref_2k_raw  = get_setting("reference_2k_sec")
    plan_start  = get_setting("plan_start_date")
    ref_2k_sec  = float(ref_2k_raw) if ref_2k_raw else None

    with st.expander("기준 2k / 시작일 설정", expanded=(ref_2k_sec is None or plan_start is None)):
        st.caption(
            "Pete Plan은 **기준 2k**를 토대로 목표 페이스를 계산합니다. "
            "기록을 새로 저장해도 자동 갱신되지 않으며, 여기서 명시적으로 갱신해야 합니다. "
            "**시작일**은 3주 사이클의 기준점입니다."
        )
        c1, c2 = st.columns(2)
        with c1:
            mm = st.number_input("기준 2k — 분",
                                 min_value=0, max_value=20,
                                 value=int(ref_2k_sec // 60) if ref_2k_sec else 8, step=1)
            ss = st.number_input("기준 2k — 초",
                                 min_value=0.0, max_value=59.9,
                                 value=float(ref_2k_sec % 60) if ref_2k_sec else 0.0,
                                 step=0.1, format="%.1f")
            if st.button("기준 2k 저장"):
                set_setting("reference_2k_sec", mm * 60 + ss)
                st.success("기준 2k 저장됨")
                st.rerun()
        with c2:
            default_start = date.fromisoformat(plan_start) if plan_start else date.today()
            new_start = st.date_input("Pete Plan 시작일", value=default_start)
            if st.button("시작일 저장"):
                set_setting("plan_start_date", new_start.isoformat())
                st.success("시작일 저장됨")
                st.rerun()

    st.divider()

    # ── 이번 주 Pete Plan 추천 ──
    st.subheader("🔥 이번 주 추천 세션 (Pete Plan)")

    if not ref_2k_sec or not plan_start:
        st.warning("위에서 **기준 2k**와 **시작일**을 먼저 설정해주세요.")
    else:
        pr_2k_sec = ref_2k_sec
        st.info(f"기준 2k: **{sec_to_mmss(pr_2k_sec)}** "
                f"(평균 스플릿 {sec_to_mmss(calc_avg_split(2000, pr_2k_sec))}/500m)")

        # 시작일 기준 주차 계산 (RECORD와 무관)
        current_week = get_current_week_index(plan_start, date.today())
        week_plan = get_week_plan(current_week)

        days_elapsed = (date.today() - date.fromisoformat(plan_start)).days
        st.caption(f"시작일 {plan_start} 기준 {days_elapsed}일 경과 → Pete Plan **Week {current_week}**")

        # 하드 세션 카드
        for i, sess in enumerate(week_plan["hard_sessions"], start=1):
            with st.container(border=True):
                st.markdown(f"**하드 #{i} — {sess['name']}** ({sess['workout_type']})")
                target_split = calc_target_split(pr_2k_sec, sess["pace_offset_sec"])
                target_watts = pace_to_watts(target_split)
                st.write(
                    f"🎯 목표 스플릿: **{sec_to_mmss(target_split)}/500m**  "
                    f"(약 {target_watts:.0f}W)"
                )
                st.caption(sess["description"])

        # Steady State
        ss = STEADY_STATE_SESSION
        with st.container(border=True):
            st.markdown(f"**Steady State × 2 (주 2회) — {ss['name']}** ({ss['workout_type']})")
            target_split = calc_target_split(pr_2k_sec, ss["pace_offset_sec"])
            target_watts = pace_to_watts(target_split)
            st.write(
                f"🎯 목표 스플릿: **{sec_to_mmss(target_split)}/500m**  "
                f"(약 {target_watts:.0f}W), {ss['stroke_rate_range'][0]}~{ss['stroke_rate_range'][1]} spm"
            )
            st.caption(ss["description"])

    st.divider()

    # 활성 목표
    st.subheader("🎯 활성 목표")
    active_goals = get_active_goals()
    if not active_goals:
        st.caption("활성 목표 없음. '목표 설정' 페이지에서 추가하세요.")
    else:
        for g in active_goals:
            with st.container(border=True):
                _render_goal_card(g) if False else None  # placeholder, 아래서 정의
                # 인라인 렌더
                if g["goal_type"] == "PR":
                    st.write(
                        f"**PR 목표** — {g['distance_m']}m을 "
                        f"**{sec_to_mmss(g['target_time_sec'])}**에"
                    )
                elif g["goal_type"] == "PACE_HOLD":
                    extra = f", {g['max_stroke_rate']:.0f} spm 이하" if g['max_stroke_rate'] else ""
                    st.write(
                        f"**페이스 유지** — {g['distance_m']}m을 "
                        f"**{sec_to_mmss(g['target_split_sec'])}/500m**{extra}"
                    )
                elif g["goal_type"] == "WATTS_HOLD":
                    base = (f"{g['duration_sec']//60}분" if g['duration_sec']
                            else f"{g['distance_m']}m")
                    extra = f", {g['max_stroke_rate']:.0f} spm 이하" if g['max_stroke_rate'] else ""
                    st.write(f"**출력 유지** — {base} 동안 **{g['target_watts']:.0f}W**{extra}")
                else:  # NOTE
                    st.write(f"**메모** — {g['note']}")
                if g["note"] and g["goal_type"] != "NOTE":
                    st.caption(g["note"])


# ─────────────────────────────────────────────
# 페이지 2: 세션 기록
# ─────────────────────────────────────────────
elif page == "세션 기록":
    st.header("📝 세션 기록")

    workout_type = st.selectbox("훈련 종류", WORKOUT_TYPES, index=WORKOUT_TYPES.index("FREE"))
    distance_m = st.selectbox(
        "거리",
        DISTANCES,
        format_func=lambda d: f"{d}m" if d < 1000 else f"{d//1000}k",
    )

    st.caption("완주 시간을 분/초로 입력")
    c1, c2 = st.columns(2)
    minutes = c1.number_input("분", min_value=0, max_value=120, value=0, step=1)
    seconds = c2.number_input("초", min_value=0.0, max_value=59.9, value=0.0, step=0.1, format="%.1f")
    total_time_sec = minutes * 60 + seconds

    stroke_rate = st.number_input("평균 스트로크 레이트 (spm, 선택)", min_value=0.0, max_value=50.0, value=0.0, step=0.5)
    condition = st.radio("컨디션", ["상", "중", "하"], horizontal=True, index=1)
    note = st.text_input("메모 (선택)")

    # 미리 계산
    if total_time_sec > 0:
        avg_split = calc_avg_split(distance_m, total_time_sec)
        avg_watts = pace_to_watts(avg_split)
        st.info(
            f"평균 스플릿: **{sec_to_mmss(avg_split)}/500m**  ·  평균 출력: **{avg_watts:.0f}W**"
        )

    if st.button("기록 저장", type="primary", disabled=(total_time_sec <= 0)):
        avg_split = calc_avg_split(distance_m, total_time_sec)
        avg_watts = pace_to_watts(avg_split)

        # 저장 전에 이전 PR과 기준 2k 확인 (PR 갱신 알림용)
        prev_pr = get_pr(distance_m)
        prev_pr_sec = prev_pr["total_time_sec"] if prev_pr else None

        save_rowing_log(
            workout_type=workout_type,
            distance_m=distance_m,
            total_time_sec=total_time_sec,
            avg_split_sec=avg_split,
            condition=condition,
            avg_watts=avg_watts,
            stroke_rate=stroke_rate if stroke_rate > 0 else None,
            note=note,
        )
        st.success(f"저장 완료! 평균 스플릿 {sec_to_mmss(avg_split)}/500m, {avg_watts:.0f}W")

        # PR 갱신 여부 표시 + 2k면 기준 2k 갱신 옵션
        if prev_pr_sec is None or total_time_sec < prev_pr_sec:
            st.balloons()
            label = f"{distance_m}m" if distance_m < 1000 else f"{distance_m//1000}k"
            st.success(f"🏆 새 PR! {label} {sec_to_mmss(total_time_sec)}")

            if distance_m == 2000:
                current_ref = get_setting("reference_2k_sec")
                if not current_ref or total_time_sec < float(current_ref):
                    st.info(
                        f"기준 2k는 자동으로 갱신되지 않습니다. "
                        f"새 PR({sec_to_mmss(total_time_sec)})을 기준으로 Pete Plan 목표를 다시 잡으려면 아래 버튼을 누르세요."
                    )
                    if st.button("기준 2k를 새 PR로 갱신"):
                        set_setting("reference_2k_sec", total_time_sec)
                        st.success("기준 2k 갱신 완료!")
                        st.rerun()


# ─────────────────────────────────────────────
# 페이지 3: 히스토리
# ─────────────────────────────────────────────
elif page == "히스토리":
    st.header("📈 히스토리")

    filter_dist = st.selectbox(
        "거리 필터",
        ["전체"] + DISTANCES,
        format_func=lambda d: d if d == "전체" else (f"{d}m" if d < 1000 else f"{d//1000}k"),
    )
    dist_param = None if filter_dist == "전체" else filter_dist
    logs = get_rowing_history(distance_m=dist_param, limit=100)

    if not logs:
        st.info("아직 기록이 없습니다.")
    else:
        df = pd.DataFrame(logs)
        # 표시용 변환
        df["distance"] = df["distance_m"].apply(lambda d: f"{d}m" if d < 1000 else f"{d//1000}k")
        df["total_time"] = df["total_time_sec"].apply(sec_to_mmss)
        df["avg_split"] = df["avg_split_sec"].apply(sec_to_mmss)
        df["avg_watts"] = df["avg_watts"].apply(lambda w: f"{w:.0f}" if w else "-")
        df["stroke_rate"] = df["stroke_rate"].apply(lambda r: f"{r:.1f}" if r else "-")

        show = df[[
            "date", "workout_type", "distance", "total_time",
            "avg_split", "avg_watts", "stroke_rate", "condition", "note",
        ]].copy()
        show.columns = [
            "날짜", "종류", "거리", "완주", "스플릿/500m", "Watts", "spm", "컨디션", "메모",
        ]
        st.dataframe(show, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────
# 페이지 4: 목표 설정
# ─────────────────────────────────────────────
elif page == "목표 설정":
    st.header("🎯 목표 설정")

    # 활성 목표 목록 + 비활성화 버튼
    st.subheader("현재 활성 목표")
    active = get_active_goals()
    if not active:
        st.caption("활성 목표 없음.")
    else:
        for g in active:
            cols = st.columns([4, 1])
            with cols[0]:
                if g["goal_type"] == "PR":
                    txt = f"**PR**: {g['distance_m']}m을 {sec_to_mmss(g['target_time_sec'])}에"
                elif g["goal_type"] == "PACE_HOLD":
                    extra = f" / ≤{g['max_stroke_rate']:.0f}spm" if g['max_stroke_rate'] else ""
                    txt = f"**페이스 유지**: {g['distance_m']}m, {sec_to_mmss(g['target_split_sec'])}/500m{extra}"
                elif g["goal_type"] == "WATTS_HOLD":
                    base = (f"{g['duration_sec']//60}분" if g['duration_sec']
                            else f"{g['distance_m']}m")
                    extra = f" / ≤{g['max_stroke_rate']:.0f}spm" if g['max_stroke_rate'] else ""
                    txt = f"**출력 유지**: {base} 동안 {g['target_watts']:.0f}W{extra}"
                else:
                    txt = f"**메모**: {g['note']}"
                st.write(txt)
                if g["note"] and g["goal_type"] != "NOTE":
                    st.caption(g["note"])
            with cols[1]:
                if st.button("종료", key=f"deact_{g['id']}"):
                    deactivate_goal(g["id"])
                    st.rerun()

    st.divider()

    # 새 목표 추가
    st.subheader("새 목표 추가")
    goal_type = st.selectbox(
        "목표 유형",
        GOAL_TYPES,
        format_func=lambda t: {
            "PR": "PR (개인 기록)",
            "PACE_HOLD": "페이스 유지",
            "WATTS_HOLD": "출력 유지",
            "NOTE": "자유 메모",
        }[t],
    )

    # 입력 필드 (유형별)
    distance_m = duration_sec = None
    target_time_sec = target_split_sec = target_watts = None
    max_stroke_rate = None
    note = ""

    if goal_type == "PR":
        distance_m = st.selectbox(
            "거리", DISTANCES,
            format_func=lambda d: f"{d}m" if d < 1000 else f"{d//1000}k",
        )
        c1, c2 = st.columns(2)
        mm = c1.number_input("목표 분", min_value=0, max_value=120, value=7, step=1)
        ss = c2.number_input("목표 초", min_value=0.0, max_value=59.9, value=30.0, step=0.1, format="%.1f")
        target_time_sec = mm * 60 + ss

    elif goal_type == "PACE_HOLD":
        distance_m = st.selectbox(
            "거리", DISTANCES,
            format_func=lambda d: f"{d}m" if d < 1000 else f"{d//1000}k",
        )
        c1, c2 = st.columns(2)
        mm = c1.number_input("스플릿 분(500m당)", min_value=0, max_value=10, value=2, step=1)
        ss = c2.number_input("스플릿 초", min_value=0.0, max_value=59.9, value=0.0, step=0.1, format="%.1f")
        target_split_sec = mm * 60 + ss
        max_spm = st.number_input("최대 스트로크 레이트 (spm, 0=제한 없음)", min_value=0.0, max_value=50.0, value=0.0, step=0.5)
        max_stroke_rate = max_spm if max_spm > 0 else None

    elif goal_type == "WATTS_HOLD":
        mode = st.radio("기준", ["거리 기반", "시간 기반"], horizontal=True)
        if mode == "거리 기반":
            distance_m = st.selectbox(
                "거리", DISTANCES,
                format_func=lambda d: f"{d}m" if d < 1000 else f"{d//1000}k",
            )
        else:
            duration_min = st.number_input("시간 (분)", min_value=1, max_value=180, value=20, step=1)
            duration_sec = duration_min * 60
        target_watts = st.number_input("목표 Watts", min_value=50.0, max_value=600.0, value=250.0, step=5.0)
        max_spm = st.number_input("최대 spm (0=제한 없음)", min_value=0.0, max_value=50.0, value=0.0, step=0.5)
        max_stroke_rate = max_spm if max_spm > 0 else None

    note = st.text_input("메모 (선택)" if goal_type != "NOTE" else "메모 내용")

    if st.button("목표 저장", type="primary"):
        save_goal(
            goal_type=goal_type,
            distance_m=distance_m,
            duration_sec=duration_sec,
            target_time_sec=target_time_sec,
            target_split_sec=target_split_sec,
            target_watts=target_watts,
            max_stroke_rate=max_stroke_rate,
            note=note,
        )
        st.success("목표 저장 완료!")
        st.rerun()
