import json
import datetime

tz = datetime.timezone(datetime.timedelta(hours=8))
now = datetime.datetime.now(tz)

output = {
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": f"当前北京时间: {now.strftime('%Y-%m-%d %H:%M:%S')}"
    }
}
print(json.dumps(output, ensure_ascii=False))
