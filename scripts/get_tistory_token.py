"""
티스토리 액세스 토큰 발급 스크립트 (최초 1회만 실행)
로컬 PC에서 실행하여 액세스 토큰을 발급받으세요.

실행 방법: python scripts/get_tistory_token.py
"""
import requests
import sys


def main():
    print("=" * 55)
    print("  티스토리 액세스 토큰 발급")
    print("=" * 55)
    print("\n티스토리 앱이 등록되어 있어야 합니다.")
    print("앱 등록: https://www.tistory.com/guide/api/manage/register\n")

    client_id = input("1. App ID (Client ID)를 입력하세요: ").strip()
    client_secret = input("2. Secret Key를 입력하세요: ").strip()
    redirect_uri = "https://woong38.tistory.com"

    auth_url = (
        f"https://www.tistory.com/oauth/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
    )

    print("\n" + "=" * 55)
    print("  아래 URL을 브라우저에 복사해서 열어주세요")
    print("=" * 55)
    print(f"\n{auth_url}\n")
    print("→ '허용' 클릭 후 주소창 URL 확인")
    print("→ code= 뒤의 값 복사")
    print("   예) https://woong38.tistory.com?code=여기값복사\n")

    code = input("3. code 값을 입력하세요: ").strip()

    token_url = "https://www.tistory.com/oauth/access_token"
    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "code": code,
        "grant_type": "authorization_code",
    }

    response = requests.get(token_url, params=params)

    if "access_token" in response.text:
        token = response.text.split("access_token=")[1].split("&")[0]
        print("\n" + "=" * 55)
        print("  ✅ 액세스 토큰 발급 성공!")
        print("=" * 55)
        print(f"\n액세스 토큰:\n{token}")
        print("\n" + "=" * 55)
        print("  GitHub Secrets 등록 방법")
        print("=" * 55)
        print("1. GitHub 저장소 → Settings")
        print("2. Secrets and variables → Actions")
        print("3. New repository secret 클릭")
        print("4. Name: TISTORY_ACCESS_TOKEN")
        print(f"5. Value: {token}")
        print("\nANTHROPIC_API_KEY도 같은 방법으로 등록하세요.")
    else:
        print(f"\n❌ 토큰 발급 실패: {response.text}")
        print("App ID와 Secret Key를 다시 확인해주세요.")
        sys.exit(1)


if __name__ == '__main__':
    main()
