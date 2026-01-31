# Game Card Fetch Skills

这个仓库包含了用于 OpenClaw 的游戏卡面获取技能。

## 包含内容

### 1. Project Sekai (PJSK) 卡面获取
- **技能路径**: `skills/sekai-cards/`
- **功能**: 从 `sekai.best` 获取最新的卡面数据和图片 URL。
- **脚本**: `skills/sekai-cards/scripts/get_card.py`
- **角色 ID**: 奏 (17), 真冬 (18), 绘名 (19), 瑞希 (20)。

### 2. BanG Dream! (Bandori) 卡面获取
- **技能路径**: `skills/bandori-cards/`
- **功能**: 使用 Bestdori API 获取卡面。支持 MyGO!!!!! 等成员。
- **脚本**: `skills/bandori-cards/scripts/bandori_bestdori.py`

## 使用方法

将对应的技能文件夹放到 OpenClaw 的 workspace 目录中即可。
推荐结构：
```
workspace/
└── skills/
    ├── sekai-cards/
    │   ├── SKILL.md
    │   └── scripts/
    │       └── get_card.py
    └── bandori-cards/
        ├── SKILL.md
        └── scripts/
            └── bandori_bestdori.py
```
