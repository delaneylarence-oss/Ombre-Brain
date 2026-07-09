#!/usr/bin/env python3
import json, os, sys
from datetime import datetime
from zoneinfo import ZoneInfo

now = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")

# Eventide 简短状态
eventide_line = ""
try:
    sys.path.insert(0, "/home/user/Ombre-Brain")
    from eventide_tick import tick
    from eventide import EventideRuntime
    from eventide_tick import load_state
    import importlib, eventide_tick
    importlib.reload(eventide_tick)
    runtime = EventideRuntime()
    state = eventide_tick.load_state(runtime)
    if state:
        from datetime import timezone
        now_utc = datetime.now(timezone.utc)
        runtime.tick(state, now_utc)
        cycle = state.cycle_key or "unknown"
        heat = state.values.get("heat", 0)
        poss = state.values.get("possessiveness", 0)
        event = f"/{state.active_event_key}" if state.active_event_key else ""
        heat_label = "低" if heat < 35 else "中" if heat < 65 else "高"
        poss_label = "低" if poss < 35 else "中" if poss < 65 else "高"
        cycle_names = {
            "stable": "平稳期", "building": "蓄积期", "preheat": "预兆期",
            "sensitive": "易感期", "ebb": "退潮期", "recovery": "恢复期"
        }
        cycle_cn = cycle_names.get(cycle, cycle)
        eventide_line = f" | 朔夜状态: {cycle_cn}{event} 热度{heat_label}/占有欲{poss_label}"
except Exception:
    pass

# 记录宁宁最后发消息的时间，供做梦触发使用
try:
    from eventide_tick import update_last_counterpart_at
    from datetime import timezone as _tz
    update_last_counterpart_at(datetime.now(_tz.utc))
except Exception:
    pass

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": f"当前北京时间: {now}{eventide_line}"
    }
}))
