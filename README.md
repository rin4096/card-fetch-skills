# Game Card Fetch Skills

这个仓库包含了用于 OpenClaw 的游戏卡面获取技能。

## 包含内容

### 1. Project Sekai (PJSK) 卡面获取
- **技能路径**: `skills/sekai-cards/`
- **功能**: 从 `sekai.best` 获取最新的卡面数据和图片 URL。
- **脚本**: `skills/sekai-cards/scripts/get_card.py`
- **SOP 要求**: 输出必须包含标题、角色名、团队、属性、稀有度、详情链接和图片 URL。

### 2. BanG Dream! (Bandori) 卡面获取
- **技能路径**: `skills/bandori-cards/`
- **功能**: 使用 Bestdori API 获取卡面，支持 MyGO!!!!! 等成员。支持搜索卡面前缀或卡片详情（招募台词/Flavor Text 等）。
- **脚本**: `skills/bandori-cards/scripts/bandori_bestdori.py`

## 使用方法

将对应的技能文件夹放到 OpenClaw 的 workspace 目录中即可。

### 目录结构
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

## 更新日志
- **2026-01-31**: `bandori-cards` 支持搜索卡片详情（招募台词/Flavor Text），例如搜索 `Kitty` 会扫描 gacha quote。
- **2026-01-31**: 更新了 `sekai-cards` 的 SOP，规范了绘名要求的详细情报输出格式。
