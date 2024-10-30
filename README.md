# mc-qqbot-next

<div align="center">

![](https://wakapi.xyqyear.com/api/badge/xyqyear/interval:any/project:mc-qqbot-next) ![](https://img.shields.io/github/v/release/xyqyear/mc-qqbot-next)

</div>

## 概述

`mc-qqbot-next` 是我之前的项目 [minecraft-qqbot](https://github.com/xyqyear/minecraft-qqbot) 的现代重构版本。

## 功能

- 列出服务器和玩家 (/list or /ping)
  - 船新的返回格式
  - 默认获取全部服务器的信息
- 发送消息到服务器 (/s or /say)
  - 玩家自行绑定游戏账号
- 通过回复消息自动确定发送消息到哪个服务器
- 白名单管理 (/whitelist)
- 封禁管理 (/ban, /banlist, /unban)

## 技术亮点

- 使用nonebot2，作为插件开发。耦合更小。
- 数据库使用nonebot-plugin-orm。
- 通过读取log获取和刷新玩家uuid和名称的映射。减少了网络请求，也可以较为实时地追踪名称变化。
- 使用[minecraft-docker-manager-lib](https://github.com/xyqyear/minecraft-docker-manager-lib)，更方便适配我自己的MC服务器管理框架。
- 完整的测试（计划中）

## 使用 & 贡献

该项目为个人项目，暂时不提供教程，也暂时不接受贡献。

## 致谢

- [nonebot2](https://github.com/nonebot/nonebot2)
- [minecraft-docker-manager-lib](https://github.com/xyqyear/minecraft-docker-manager-lib)
