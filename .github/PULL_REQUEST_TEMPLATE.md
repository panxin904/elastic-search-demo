# PR Title

> 用 Conventional Commits：`feat(<scope>): <title>` / `fix(scope): ...` / `docs: ...` / `chore(scope): ...`
>
> scope 例子：`c2`（C 任务编号）/ `es-html`（子站名）/ `glossary`（数据层）/ `audit` / `tools`

## 改了什么

<!-- 简述变更内容 -->

## 为什么改

<!-- 背景 / 关联 issue -->

## 影响范围

<!-- 勾选所有适用的 -->

- [ ] 子站：`<site>-html/docs/<path>`
- [ ] 共享：`shared-assets/`
- [ ] 数据：`shared-assets/glossary/keywords.json`
- [ ] 脚本：`sites-hub/scripts/`
- [ ] 配置：`.github/workflows/`
- [ ] 文档：`sites-hub/OPTIMIZATION*.md`

## 本地验证

<!-- 必填 -->

- [ ] `npm run docs:build` 在 `<site>-html` 跑通（如改动 build 链）
- [ ] `bash sites-hub/scripts/build-with-pagefind.sh` 全 28 站跑通（如改 .vue / config.mts）
- [ ] `python3 sites-hub/scripts/audit-content.py` 无新增错误
- [ ] `bash sites-hub/scripts/spell-check.sh` 无新增错别字
- [ ] CI：3 jobs 全绿（check / build-all / release）

## 截图 / 录屏（如适用）

<!-- UI / 渲染相关改动必填 -->

## 关联 Issue / 任务

<!-- 关联 GitHub Issue / 内部任务编号 -->

---

**Reviewer 注意**：详见 [PR Review Checklist](../docs/PR-REVIEW-CHECKLIST.md)
