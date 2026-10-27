# 常亮 · AI 应用开发工程师 — 个人简历主页

在线地址：https://cl9428.github.io/resume/

一个零依赖的单文件简历网页：改 `index.html` → push → GitHub Pages 自动更新（通常 1 分钟内生效）。

## 文件

| 文件 | 说明 |
| --- | --- |
| `index.html` | 简历主页，样式/脚本全部内联，无外部依赖 |
| `changliang-resume.pdf` | A4 简历 PDF，网页「下载 PDF」按钮指向它 |
| `deploy.py` | 可选：本地改动后用脚本重新导出 PDF |

## 本地预览

```bash
python3 -m http.server 8000
# 打开 http://localhost:8000
```

## 更新内容

直接改 `index.html` 里的文案，然后：

```bash
git add -A && git commit -m "update resume" && git push
```

## 更新 PDF

用 Chrome / Edge 打开 `index.html`，`⌘P` → 目标另存为 PDF → 覆盖 `changliang-resume.pdf`。
网页在打印时会自动展开所有折叠项，并隐藏导航与按钮，直接出 A4 版式。

## GitHub Pages

仓库 Settings → Pages → Build and deployment → Source: **Deploy from a branch** → Branch: **main** / **/ (root)**。

---

联系方式：clinux134@163.com · github.com/cl9428 · 北京
