# 桌宠-小旺

Windows + Python + PySide6 desktop pet scaffold based on `小旺桌宠-决策汇总.docx`.

这个版本先搭框架，不强行追求完整美术。真实 PNG 素材缺失时，窗口会用代码画占位图，让你先跑通 Stage 0-5 的事件、状态机和动画结构。

## 已搭好的核心

- 无边框、置顶、透明背景窗口骨架
- `idle/read/type/ball/sleep/walk/drag` 状态集中定义
- 端坐作为枢纽：端坐双击随机进入活动，活动双击回端坐
- 睡觉特殊规则：2 秒内连续两组双击才回端坐
- 拖动全局打断：任意状态拖动切 `drag`，松手回原状态
- 长时间无互动后，端坐状态低频触发 `walk`
- 单击延迟判定窗口，避免和双击冲突
- emote 数据驱动，睡觉单击只显示 `zzz`
- 图片路径和可调参数集中在 `config/defaults.json`
- 纯 Python 单元测试，不依赖 PySide6

## 目录结构

```text
xiaowang_desktop_pet/
  assets/
    body/            # idle_01.png, read_01.png 等身体帧
    transitions/     # t_idle_read_01.png 等转场帧
    emotes/          # bubble.png 可选
  config/
    defaults.json    # 时长、概率、窗口大小、素材目录等配置
  docs/
    state_diagram.md # 状态转移图草稿
  src/xiaowang_pet/
    state_machine.py # 核心状态机
    animations.py    # 帧序列和转场播放
    window.py        # PySide6 桌宠窗口
    main.py          # 启动入口
  tests/
    test_state_machine.py
```

## 运行前需要的软件

你本机需要：

- Python 3.10+
- PySide6

我检查了当前 Codex 自带 Python：还没有 PySide6。所以现在只做了框架和非 GUI 测试，没有启动桌宠窗口。

安装和运行：

```powershell
cd C:\Users\xiaowang\Documents\Codex\2026-06-24\new-chat\outputs\桌宠-小旺
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m xiaowang_pet
```

如果你只想装依赖：

```powershell
python -m pip install -r requirements.txt
```

## 先验证状态机

不装 PySide6 也可以先跑：

```powershell
cd C:\Users\xiaowang\Documents\Codex\2026-06-24\new-chat\outputs\桌宠-小旺
python -m unittest discover -s tests
```

## 放素材的命名

先按文档 Batch A 放这些 PNG：

- `assets/body/idle_01.png`
- `assets/body/idle_02.png`
- `assets/body/read_01.png`
- `assets/body/read_02.png`
- `assets/body/type_01.png`
- `assets/body/type_02.png`
- `assets/body/type_03.png`
- `assets/body/ball_01.png`
- `assets/body/ball_02.png`
- `assets/body/ball_03.png`
- `assets/body/ball_prop.png`
- `assets/body/sleep_01.png`
- `assets/body/sleep_02.png`
- `assets/body/walk_01.png`
- `assets/body/walk_02.png`
- `assets/body/drag.png`

转场帧以后放：

- `assets/transitions/t_idle_read_01.png`
- `assets/transitions/t_idle_read_02.png`
- `assets/transitions/t_idle_type_01.png`
- `assets/transitions/t_idle_type_02.png`
- `assets/transitions/t_idle_ball_01.png`
- `assets/transitions/t_idle_ball_02.png`
- `assets/transitions/t_idle_sleep_01.png`
- `assets/transitions/t_idle_sleep_02.png`
- `assets/transitions/t_idle_walk_01.png`
- `assets/transitions/t_idle_walk_02.png`

没有素材时不用急，程序会显示占位图。

## 下一步建议

先定文档里两个星号问题：

- 初始位置：当前默认 `bottom_right`
- Stage 5 前的临时退出口：当前默认 `Esc`

然后从 Stage 0 开始：先让窗口透明置顶出现，再接拖动，再接 idle 两帧呼吸。
