#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通过 GitHub REST API 创建仓库、上传文件、启用 Pages（本机仅 api.github.com 可达）。"""
import base64, json, os, sys, time, urllib.request, urllib.error

TOKEN = (open(os.path.expanduser("~/.gh_resume_token")).read().strip()
         if os.path.exists(os.path.expanduser("~/.gh_resume_token"))
         else (os.environ.get("GH_TOKEN") or "").strip())
if not TOKEN:
    sys.exit("缺少 token：请把 PAT 写入 ~/.gh_resume_token 或设置 GH_TOKEN")

REPO = sys.argv[1] if len(sys.argv) > 1 else "resume"
SRC = "/Users/a1/简历/resume-site"

API = "https://api.github.com"
HDR = {
    "Authorization": "Bearer " + TOKEN,
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "resume-deploy",
}


def req(method, path, body=None, raw=False):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(API + path, data=data, headers=HDR, method=method)
    if body is not None:
        r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            txt = resp.read()
            return json.loads(txt) if txt and not raw else (txt if raw else {})
    except urllib.error.HTTPError as e:
        return {"__error__": e.code, "__body__": e.read().decode("utf8", "replace")[:600]}


me = req("GET", "/user")
if "__error__" in me:
    sys.exit("token 无效或无权限: %s %s" % (me["__error__"], me["__body__"]))
owner = me["login"]
print("GitHub 账号:", owner)

# 1. 创建仓库
info = req("GET", "/repos/%s/%s" % (owner, REPO))
if "__error__" not in info:
    print("仓库已存在，复用:", info["html_url"])
else:
    res = req("POST", "/user/repos", {
        "name": REPO,
        "description": "常亮 · AI 应用开发工程师 — 个人简历主页（GitHub Pages）",
        "homepage": "https://%s.github.io/%s/" % (owner, REPO),
        "public": True,
        "auto_init": False,
        "has_issues": False,
        "has_wiki": False,
        "has_projects": False,
    })
    if "__error__" in res:
        sys.exit("创建仓库失败: %s %s" % (res["__error__"], res["__body__"]))
    print("仓库已创建:", res["html_url"])

# 2. 上传文件
files = ["index.html", "changliang-resume.pdf", "README.md", ".gitignore"]
for name in files:
    p = os.path.join(SRC, name)
    if not os.path.exists(p):
        print("跳过（不存在）:", name); continue
    content = base64.b64encode(open(p, "rb").read()).decode()
    cur = req("GET", "/repos/%s/%s/contents/%s" % (owner, REPO, name))
    body = {"message": "add %s" % name, "content": content}
    if "__error__" not in cur and isinstance(cur, dict) and cur.get("sha"):
        body["sha"] = cur["sha"]
        body["message"] = "update %s" % name
    res = req("PUT", "/repos/%s/%s/contents/%s" % (owner, REPO, name), body)
    if "__error__" in res:
        print("上传失败 %s: %s %s" % (name, res["__error__"], res["__body__"]))
    else:
        print("已上传:", name, "(%d bytes)" % os.path.getsize(p))

# 3. 确认默认分支
info = req("GET", "/repos/%s/%s" % (owner, REPO))
branch = info.get("default_branch", "main")
print("默认分支:", branch)

# 4. 启用 Pages
pages = req("GET", "/repos/%s/%s/pages" % (owner, REPO))
if "__error__" not in pages and isinstance(pages, dict) and pages.get("html_url"):
    print("Pages 已启用:", pages["html_url"])
else:
    for attempt in range(6):
        res = req("POST", "/repos/%s/%s/pages" % (owner, REPO),
                  {"source": {"branch": branch, "path": "/"}})
        if "__error__" not in res:
            print("Pages 已启用:", (res.get("html_url") or ""), "status:", res.get("status"))
            break
        print("启用 Pages 第 %d 次失败: %s %s" % (attempt + 1, res["__error__"], res["__body__"]))
        time.sleep(5)
    else:
        print("!! Pages 未能自动启用，请到仓库 Settings → Pages 手动选择 Deploy from a branch → %s / / (root)" % branch)

url = "https://%s.github.io/%s/" % (owner, REPO)
print("\n站点地址:", url)

# 5. 探测是否可访问
for i in range(10):
    try:
        r = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(r, timeout=20) as resp:
            body = resp.read().decode("utf8", "replace")
            print("HTTP %s, %d bytes, 标题含『常亮』: %s" % (resp.status, len(body), "常亮" in body))
            break
    except Exception as e:
        print("等待生效... (%d/10) %s" % (i + 1, type(e).__name__))
        time.sleep(20)
