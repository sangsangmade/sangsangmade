# 티스토리 블로그 자동 발행 설정 가이드

## 개요
월·수·금 오전 10시, Claude AI가 랑데뷰 관련 블로그 글을 자동으로 작성하여 티스토리에 발행합니다.

---

## 1단계: 티스토리 앱 등록

1. https://www.tistory.com/guide/api/manage/register 접속
2. 다음과 같이 입력:
   - **서비스명**: 랑데뷰 블로그 자동화
   - **설명**: 블로그 자동 포스팅
   - **서비스 URL**: `https://woong38.tistory.com`
   - **CallBack**: `https://woong38.tistory.com`
3. 등록 후 **App ID**와 **Secret Key** 메모

---

## 2단계: 티스토리 액세스 토큰 발급

로컬 PC에서 아래 명령어 실행:

```bash
pip install requests
python scripts/get_tistory_token.py
```

스크립트 안내에 따라 진행하면 액세스 토큰이 발급됩니다.

---

## 3단계: GitHub Secrets 등록

GitHub 저장소 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Name | Value |
|------|-------|
| `TISTORY_ACCESS_TOKEN` | 2단계에서 발급받은 토큰 |
| `ANTHROPIC_API_KEY` | Anthropic API 키 (https://console.anthropic.com) |

---

## 4단계: 동작 확인

GitHub 저장소 → **Actions** 탭 → **티스토리 블로그 자동 발행** → **Run workflow** 클릭

정상 실행되면 자동 발행이 완료된 것입니다.

---

## 발행 스케줄

| 요일 | 발행 시간 |
|------|----------|
| 월요일 | 오전 10:00 |
| 수요일 | 오전 10:00 |
| 금요일 | 오전 10:00 |

---

## 주제 목록 (자동 순환)

1. 강남 동창회 장소 추천
2. 논현역 회식 장소 추천
3. 강남 피로연 장소 추천
4. 강남 생일파티 장소 추천
5. 논현동 대관 파티룸 추천
6. 강남 단체모임 장소 추천
7. 신논현역 근처 회식 장소
8. 강남 기업 워크숍 뒤풀이 장소
9. 논현역 종강파티 장소 추천
10. 강남 송년회 장소 추천
11. 강남 신입사원 환영회 장소
12. 논현동 프라이빗 술집 추천
