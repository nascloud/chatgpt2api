"""测试 Sub2API 修复后的 token 获取逻辑（支持脱敏账号）"""
import json
from curl_cffi.requests import Session

BASE_URL = "http://192.168.50.100:38080"
EMAIL = "dthzara@gmail.com"
PASSWORD = "wang951357"


def login(base_url: str, email: str, password: str) -> str:
    url = f"{base_url.rstrip('/')}/api/v1/auth/login"
    resp = Session(verify=True).post(
        url,
        json={"email": email, "password": password},
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        timeout=30,
    )
    resp.raise_for_status()
    token = resp.json().get("data", {}).get("access_token")
    if not token:
        raise RuntimeError("login failed: no access_token")
    return token


def clean(value) -> str:
    return str(value or "").strip()


def extract_access_token(credentials) -> str:
    if not isinstance(credentials, dict):
        return ""
    for key in ("access_token", "accessToken", "token"):
        val = clean(credentials.get(key))
        if val:
            return val
    return ""


def unwrap_envelope(payload):
    if isinstance(payload, dict) and "data" in payload and "code" in payload:
        return payload.get("data")
    return payload


def list_accounts(session, base_url: str, headers: dict) -> list[dict]:
    """列出所有账号，打印每个账号的 credentials 和 credentials_status"""
    accounts = []
    page = 1
    while True:
        resp = session.get(
            f"{base_url.rstrip('/')}/api/v1/admin/accounts",
            headers=headers,
            params={"platform": "openai", "type": "oauth", "page": page, "page_size": 200},
            timeout=30,
        )
        resp.raise_for_status()
        data = unwrap_envelope(resp.json())
        items = data.get("items") if isinstance(data, dict) else None
        if not isinstance(items, list) or not items:
            break
        for acct in items:
            if not isinstance(acct, dict):
                continue
            accounts.append(acct)
        page += 1
        if len(items) < 200:
            break
    return accounts


def extract_data_accounts(payload) -> list[dict]:
    data = unwrap_envelope(payload)
    if isinstance(data, dict):
        raw = data.get("accounts")
        if isinstance(raw, list):
            return [a for a in raw if isinstance(a, dict)]
    return []


def fetch_from_data_export(session, base_url: str, headers: dict, account_id: str) -> dict | None:
    """优先走数据导出接口"""
    resp = session.get(
        f"{base_url.rstrip('/')}/api/v1/admin/accounts/data",
        headers=headers,
        params={"ids": account_id, "include_proxies": "false"},
        timeout=30,
    )
    if resp.status_code == 404:
        print("  [导出接口] 404 不存在，将回退")
        return None
    resp.raise_for_status()
    accounts = extract_data_accounts(resp.json())
    if accounts:
        return accounts[0]
    return None


def fetch_from_detail(session, base_url: str, headers: dict, account_id: str) -> dict | None:
    """回退到旧的详情接口"""
    resp = session.get(
        f"{base_url.rstrip('/')}/api/v1/admin/accounts/{account_id}",
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()
    account = unwrap_envelope(resp.json())
    if not isinstance(account, dict):
        account = resp.json() if isinstance(resp.json(), dict) else {}
    return account


def fetch_token_for_account(session, base_url: str, headers: dict, account_id: str) -> tuple[str, dict]:
    """使用修复后的逻辑：优先导出，回退详情"""
    account = fetch_from_data_export(session, base_url, headers, account_id)
    if account is None:
        account = fetch_from_detail(session, base_url, headers, account_id)
    credentials = account.get("credentials") if isinstance(account.get("credentials"), dict) else {}
    token = extract_access_token(credentials)
    if not token:
        raise RuntimeError("missing access_token")
    return token, {
        "email": clean(credentials.get("email")),
        "plan_type": clean(credentials.get("plan_type")),
    }


def main():
    print(f"=== 连接 Sub2API: {BASE_URL} ===\n")

    # 1. 登录
    print("1. 登录...")
    token = login(BASE_URL, EMAIL, PASSWORD)
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    print(f"   登录成功 (token: {token[:20]}...)\n")

    # 2. 列出账号
    print("2. 列出账号...")
    session = Session(verify=True)
    accounts = list_accounts(session, BASE_URL, headers)
    print(f"   共 {len(accounts)} 个账号\n")

    # 3. 检查每个账号的 credentials 和 credentials_status
    print("3. 检查每个账号的脱敏状态:")
    redacted_count = 0
    normal_count = 0
    for i, acct in enumerate(accounts):
        acct_id = acct.get("id")
        name = acct.get("name", "?")
        creds = acct.get("credentials") if isinstance(acct.get("credentials"), dict) else {}
        cred_status = acct.get("credentials_status") if isinstance(acct.get("credentials_status"), dict) else {}
        access_token = extract_access_token(creds)
        has_token_in_status = cred_status.get("has_access_token", False)
        has_rt_in_status = cred_status.get("has_refresh_token", False)
        has_at = bool(access_token)
        has_rt = bool(clean(creds.get("refresh_token")))

        if not has_at and has_token_in_status:
            redacted_count += 1
            marker = " [脱敏]"
        else:
            normal_count += 1
            marker = ""

        print(f"   [{i+1}] ID={acct_id}  name={name}{marker}")
        print(f"        credentials:          {json.dumps(creds, ensure_ascii=False)}")
        print(f"        credentials_status:   {json.dumps(cred_status, ensure_ascii=False)}")
        print(f"        直接提取 access_token: {'有' if has_at else '空'}")
        print(f"        status.has_access_token: {has_token_in_status}")

    print(f"\n   小结: 正常={normal_count}, 脱敏(credentials空但有标记)={redacted_count}")

    # 4. 对每个账号尝试获取 token，展示修复后的效果
    print("\n4. 测试获取每个账号的 token（修复后逻辑）:")
    for i, acct in enumerate(accounts):
        acct_id = acct.get("id")
        if acct_id is None:
            continue
        name = acct.get("name", "?")
        print(f"   [{i+1}] {name} (ID={acct_id})")
        try:
            at, meta = fetch_token_for_account(session, BASE_URL, headers, str(acct_id))
            print(f"       -> access_token: {at[:30]}...")
            print(f"       -> meta: {meta}")
        except Exception as e:
            print(f"       -> 失败: {e}")

    session.close()


if __name__ == "__main__":
    main()
