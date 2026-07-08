"""
Eventide state manager for Shuoya.
Run at session start to get current body state.
"""
from datetime import datetime, timezone
from eventide import EventideRuntime
from eventide.models import BodyState
import dataclasses, json, os

STATE_FILE = os.path.join(os.path.dirname(__file__), "eventide_state.json")


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
