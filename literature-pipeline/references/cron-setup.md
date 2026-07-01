# 2026-05-09 一次性文献推送未触发：排查与补跑记录

## 症状

大哥反馈：早上快 9 点仍未收到前一晚设置的 08:30 一次性文献推送。

原 job 信息：

- job_id: `a20ff6e2672d`
- name: `一次性文献推送-5篇-明早`
- scheduled: `2026-05-09T08:30:00+08:00`
- repeat: once

## 排查结果

- `cronjob(action="list")` 返回 `count=0`，没有任何 jobs。
- `cronjob(action="run", job_id="a20ff6e2672d")` 返回 `Job with ID ... not found`。
- `send_message(action="list")` 显示 `feishu:your-group-name` 可用。
- shell 中 `hermes` CLI 不可见：`bash: hermes: command not found`，无法用 CLI 侧进一步核查。
- 当前容器无 `~/.hermes/logs/gateway.log`。

结论：不是飞书不可达，而是一次性 cron job 没有保留在当前 cron 存储/profile，或当前 scheduler 未接管。可能与重启、profile/runtime 变化、WSL/Docker/gateway/scheduler 停止有关。

## 补救动作

立即手动补跑小规模检索，使用 OpenAlex API，关键词包括：

- `keyword1 keyword2 compound1 compound2`
- `keyword3 keyword4 method1`
- `keyword5 compound3 method2`
- `keyword6 method3 method4`
- `institution keyword1 keyword2 author1 author2`

筛出并推送 5 篇：

1. Author A 2022 — impurity monitoring method for compound system，A 类。
2. Author A 2022 — purified compound at 700 °C / alloy class，A 类。
3. Author B 2024 — continuous purification method，A 类。
4. Author C 2021 — dual electrode electrolytic purification，A 类。
5. Hao 2025 — Ni 基合金在 NaCl-KCl-MgCl2 中的 CA 腐蚀模拟，B 类。

飞书补发成功：

- target: `feishu:your-group-name`
- chat_id: `oc_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- message_id: `om_x100b50dc2a1a40a8c108780f4171def`

## 归档结果

写入 Obsidian raw 文献库：

- `/vault/raw/literature/A_core/笔记/author2022_topic_monitoring.md`
- `/vault/raw/literature/A_core/笔记/author2022_purified_compound_alloys_temp.md`
- `/vault/raw/literature/A_core/笔记/author2024_continuous_purification.md`
- `/vault/raw/literature/A_core/笔记/author2021_electrolytic_purification.md`
- `/vault/raw/literature/B_supporting/笔记/author2025_alloy_system.md`

并尝试更新：

- `/vault/raw/literature/A_core/references.ris`
- `/vault/raw/literature/B_supporting/references.ris`

## Lessons

- 创建 cron 后必须立即 `cronjob(action="list")` 验证当前 profile 可见；只看到 create success 不够。
- 对一次性、次日早晨任务，必须说明 Hermes cron 是本机/profile 调度，不是云端闹钟。
- 到点未收到时，优先补发，不要长时间排查；飞书和 Obsidian 链路可手动跑通。
- 若需要长期每日任务，应单独部署并做：list 验证、manual run 验证、飞书投递验证、Obsidian 归档验证、失败提醒。