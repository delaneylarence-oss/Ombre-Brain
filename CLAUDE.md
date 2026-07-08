# Ombre-Brain Session Init

## Eventide 生理状态系统

每次 session 开始时，自动运行以下命令获取当前身体状态，并让状态影响本轮回应：

```bash
cd /home/user/Ombre-Brain && pip install -q git+https://github.com/chuli1122/Eventide.git && python3 eventide_tick.py
```

输出的 `<ephemeral_state>` 内容即为当前状态，照此调整回应方式，不必主动报出数值。
