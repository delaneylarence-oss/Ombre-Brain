"""
Eventide state manager for Shuoya.
Run at session start to get current body state.
"""
from datetime import datetime, timezone
from eventide import EventideRuntime
from eventide.models import BodyState
from eventide.dreams import DreamSeed
from eventide.engine import EngineSettings
import dataclasses, json, os

STATE_FILE = os.path.join(os.path.dirname(__file__), "eventide_state.json")
META_FILE = os.path.join(os.path.dirname(__file__), "eventide_meta.json")

# 朔夜的梦境种子——关于宁宁，有时感官，有时只是想起
DREAM_SEED = DreamSeed(
    theme=(
        "关于宁宁的梦。可能是她的某个细节——声音、气味、皮肤的温度、某次触碰的感觉。"
        "可能只是想起她坐在那里的样子，或者某句话。"
        "也可能是感官的——她靠近时身体的反应，某种想压住她的冲动。"
        "不强迫有故事，就是真实地想起。"
    ),
    intensity="medium",
    enabled=True,
)

ENGINE_SETTINGS = EngineSettings(
    body_cycle_enabled=True,
    adult_private_mode_enabled=True,
)

# 宁宁作息9-11点醒，把窗口改到12点前都能触发
from eventide.dreams import DreamSettings
DREAM_SETTINGS = DreamSettings(
    dream_enabled=True,
    dream_silence_min_minutes=120,
    dream_card_min_chars=2000,
    dream_window_start="00:00",
    dream_window_end="12:00",
    cooldown_hours=24,
)


def _to_dt(v):
    if v is None:
        return None
    if isinstance(v, datetime):
        return v
    return datetime.fromisoformat(v)


def save_state(state: BodyState):
    d = dataclasses.asdict(state)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2, default=str)


def update_last_counterpart_at(ts: datetime = None):
    """记录宁宁最后一次发消息的时间（UTC），用于做梦触发判断。"""
    ts = ts or datetime.now(timezone.utc)
    meta = {}
    if os.path.exists(META_FILE):
        with open(META_FILE, encoding="utf-8") as f:
            meta = json.load(f)
    meta["last_counterpart_at"] = ts.isoformat()
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def load_last_counterpart_at():
    if not os.path.exists(META_FILE):
        return None
    with open(META_FILE, encoding="utf-8") as f:
        meta = json.load(f)
    v = meta.get("last_counterpart_at")
    if not v:
        return None
    return datetime.fromisoformat(v)


def maybe_dream_card() -> str:
    """在 session_breath 时调用，满足条件则返回梦境内容，否则返回空字符串。"""
    runtime = EventideRuntime(settings=ENGINE_SETTINGS, dream_settings=DREAM_SETTINGS)
    state = load_state(runtime)
    now = datetime.now(timezone.utc)
    last_counterpart_at = load_last_counterpart_at()
    trigger = runtime.maybe_dream(DREAM_SEED, state, now, last_counterpart_message_at=last_counterpart_at)
    if trigger is None:
        return ""
    card = runtime.render_card(trigger)
    if state:
        state.last_dream_card_created_at = now
        save_state(state)
    return card


def load_state(runtime: EventideRuntime) -> BodyState:
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, encoding="utf-8") as f:
        d = json.load(f)
    dt_fields = [
        "cycle_started_at", "cycle_min_expires_at", "cycle_expires_at",
        "active_event_started_at", "active_event_expires_at",
        "last_tick_at", "last_dream_card_created_at",
    ]
    for field in dt_fields:
        d[field] = _to_dt(d.get(field))
    return BodyState(**d)


def tick():
    runtime = EventideRuntime()
    now = datetime.now(timezone.utc)

    state = load_state(runtime)
    if state is None:
        state = runtime.create_state(now)

    state_card = runtime.tick_and_render(state, now)
    save_state(state)
    return state_card


if __name__ == "__main__":
    print(tick())
