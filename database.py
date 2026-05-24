import sqlite3
from datetime import datetime

DB_PATH = "fitness.db"

# 지원 거리 목록 (단위: m)
DISTANCES = [500, 1000, 2000, 5000, 10000]

# 추천 로직 대상 거리 (5k/10k는 기록 전용)
RECOMMEND_DISTANCES = [500, 1000, 2000]

# 훈련 종류
WORKOUT_TYPES = ["UT2", "AT", "VO2", "AN", "TEST", "FREE"]

# 목표 유형
GOAL_TYPES = ["PR", "PACE_HOLD", "WATTS_HOLD", "NOTE"]


def get_connection():
    """DB 연결 반환"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """테이블 초기화 (없으면 생성)"""
    conn = get_connection()

    # 로잉 세션 기록
    conn.execute("""
        CREATE TABLE IF NOT EXISTS rowing_logs (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            date            TEXT    NOT NULL,            -- YYYY-MM-DD HH:MM:SS
            workout_type    TEXT    NOT NULL,            -- UT2/AT/VO2/AN/TEST/FREE
            distance_m      INTEGER NOT NULL,
            total_time_sec  REAL    NOT NULL,
            avg_split_sec   REAL    NOT NULL,            -- 500m당 평균 페이스(초)
            avg_watts       REAL,                        -- 자동 계산값
            stroke_rate     REAL,                        -- spm (선택)
            condition       TEXT    NOT NULL,            -- 상/중/하
            note            TEXT
        )
    """)

    # 목표
    conn.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_type        TEXT    NOT NULL,           -- PR/PACE_HOLD/WATTS_HOLD/NOTE
            distance_m       INTEGER,                    -- WATTS_HOLD 시간 기반이면 NULL
            duration_sec     INTEGER,                    -- WATTS_HOLD에서 시간 기반일 때
            target_time_sec  REAL,                       -- PR용
            target_split_sec REAL,                       -- PACE_HOLD용
            target_watts     REAL,                       -- WATTS_HOLD용
            max_stroke_rate  REAL,                       -- 선택
            note             TEXT,
            set_date         TEXT    NOT NULL,
            active           INTEGER NOT NULL DEFAULT 1  -- 1=활성, 0=비활성
        )
    """)

    # 설정 (key-value 저장소)
    # 사용 키:
    #   reference_2k_sec  — Pete Plan 목표 페이스 산출용 기준 2k 시간(초)
    #   plan_start_date   — Pete Plan 시작 날짜 (YYYY-MM-DD)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    # 클로즈 베타 신청자
    conn.execute("""
        CREATE TABLE IF NOT EXISTS beta_signups (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            email       TEXT    NOT NULL UNIQUE,
            experience  TEXT,                       -- 로잉 경력
            motivation  TEXT,                       -- 신청 동기
            created_at  TEXT    NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# 설정 (key-value)
# ─────────────────────────────────────────────

def get_setting(key: str, default=None):
    """설정값 조회. 없으면 default 반환"""
    conn = get_connection()
    row = conn.execute(
        "SELECT value FROM settings WHERE key = ?", (key,)
    ).fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key: str, value):
    """설정값 저장 또는 갱신"""
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO settings (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """,
        (key, str(value)),
    )
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# 클로즈 베타 신청
# ─────────────────────────────────────────────

def save_beta_signup(name: str, email: str, experience: str = "", motivation: str = ""):
    """베타 신청 저장. 이메일 중복 시 sqlite3.IntegrityError 발생"""
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO beta_signups (name, email, experience, motivation, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name, email, experience, motivation,
         datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()


def get_beta_signups():
    """베타 신청 전체 조회 (관리자용)"""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM beta_signups ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def count_beta_signups() -> int:
    """베타 신청자 수"""
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) AS c FROM beta_signups").fetchone()
    conn.close()
    return row["c"]


# ─────────────────────────────────────────────
# 로잉 세션 기록
# ─────────────────────────────────────────────

def save_rowing_log(
    workout_type: str,
    distance_m: int,
    total_time_sec: float,
    avg_split_sec: float,
    condition: str,
    avg_watts: float = None,
    stroke_rate: float = None,
    note: str = "",
):
    """세션 기록 저장"""
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO rowing_logs
            (date, workout_type, distance_m, total_time_sec, avg_split_sec,
             avg_watts, stroke_rate, condition, note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            workout_type, distance_m, total_time_sec, avg_split_sec,
            avg_watts, stroke_rate, condition, note,
        ),
    )
    conn.commit()
    conn.close()


def get_rowing_history(distance_m: int = None, limit: int = 50):
    """세션 히스토리 조회. 거리 지정 시 해당 거리만"""
    conn = get_connection()
    if distance_m is not None:
        rows = conn.execute(
            "SELECT * FROM rowing_logs WHERE distance_m = ? ORDER BY date DESC LIMIT ?",
            (distance_m, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM rowing_logs ORDER BY date DESC LIMIT ?",
            (limit,),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_pr(distance_m: int):
    """특정 거리의 PR (최단 완주시간) 1건. 없으면 None"""
    conn = get_connection()
    row = conn.execute(
        """
        SELECT * FROM rowing_logs
        WHERE distance_m = ?
        ORDER BY total_time_sec ASC
        LIMIT 1
        """,
        (distance_m,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_recent_logs(limit: int = 5):
    """최근 세션 N개 (거리 무관) — 추천 로직에서 사용"""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM rowing_logs ORDER BY date DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─────────────────────────────────────────────
# 목표
# ─────────────────────────────────────────────

def save_goal(
    goal_type: str,
    distance_m: int = None,
    duration_sec: int = None,
    target_time_sec: float = None,
    target_split_sec: float = None,
    target_watts: float = None,
    max_stroke_rate: float = None,
    note: str = "",
):
    """목표 저장 (active=1로 생성)"""
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO goals
            (goal_type, distance_m, duration_sec,
             target_time_sec, target_split_sec, target_watts,
             max_stroke_rate, note, set_date, active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            goal_type, distance_m, duration_sec,
            target_time_sec, target_split_sec, target_watts,
            max_stroke_rate, note,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    conn.commit()
    conn.close()


def get_active_goals():
    """현재 활성 목표 전체"""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM goals WHERE active = 1 ORDER BY set_date DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_goals():
    """모든 목표 (활성/비활성 포함)"""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM goals ORDER BY set_date DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def deactivate_goal(goal_id: int):
    """목표 비활성화"""
    conn = get_connection()
    conn.execute("UPDATE goals SET active = 0 WHERE id = ?", (goal_id,))
    conn.commit()
    conn.close()
