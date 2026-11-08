#!/usr/bin/env python3
"""查询 New API / One API 类站点的【账户余额】（非密钥余额）。

环境变量：
  BASE_URL      站点地址，如 https://wish.sillydream.top
  ACCESS_TOKEN  个人设置里生成的「访问令牌」
  USER_ID       你的用户 ID（个人设置页可见）
  QUOTA_PER_UNIT  可选，额度换算，默认 500000（即 500000 = $1）
"""
import json
import os
import sys
import urllib.request
import urllib.error


def main():
    base = os.environ.get("BASE_URL", "").rstrip("/")
    token = os.environ.get("ACCESS_TOKEN", "")
    user_id = os.environ.get("USER_ID", "")
    unit = float(os.environ.get("QUOTA_PER_UNIT", "500000"))

    if not (base and token and user_id):
        sys.exit("请设置 BASE_URL / ACCESS_TOKEN / USER_ID")

    req = urllib.request.Request(
        f"{base}/api/user/self",
        headers={
            "Authorization": f"Bearer {token}",
            "New-Api-User": user_id,
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 balance-checker",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode('utf-8', 'ignore')[:300]}")
    except Exception as e:
        sys.exit(f"请求失败: {e}")

    if "--raw" in sys.argv:
        print(json.dumps(body, ensure_ascii=False, indent=2))

    if not body.get("success", True):
        sys.exit(f"接口返回失败: {body.get('message')}")

    d = body.get("data", {})
    quota = d.get("quota", 0)
    used = d.get("used_quota", 0)
    lines = [
        f"用户: {d.get('username', '-')}",
        f"剩余额度: ${quota / unit:,.2f}",
        f"历史消耗: ${used / unit:,.2f}",
        f"请求次数: {d.get('request_count', '-')}",
    ]
    out = "\n".join(lines)
    print(out)

    # GitHub Actions 摘要
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write("### 账户余额\n```\n" + out + "\n```\n")


if __name__ == "__main__":
    main()
