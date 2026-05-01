import anthropic
import requests
import os
from datetime import datetime

VENUE_INFO = """
[랑데뷰 강남논현본점 기본 정보]
- 상호: 랑데뷰 (Rangdv) 강남논현본점
- 주소: 서울 강남구 논현동 198-8
- 교통: 7호선/신분당선 논현역 도보, 신논현역 인근
- 수용 인원: 20명~50명 (최대 50명)
- 대관비: 무료 (시설 이용료 포함 전액 무료)
- 운영 방식: 프라이빗 통대관 (한 팀만 단독 이용)

[보유 장비 - 모두 무료]
- 빔프로젝터 + 대형 스크린 (영상 시청 가능)
- 노트북 (발표, 영상 재생 가능)
- 음향 시스템

[메뉴]
- 총 30여 가지 메뉴 보유
- 인기 메뉴: 11가지 단체 세트 코스 (순차 제공)
  · 메인: 오리바베큐, 통삼겹바베큐, 광어&연어 사시미
  · 탕/찌개: 해물짬뽕탕, 부대전골, 백합조개탕
  · 기타: 골뱅이소면, 로제떡볶이, 가라아게 등
- 예산에 따라 메뉴 구성 협의 가능
- 외부 음식 반입 협의 가능 (케이크 등)

[추천 모임 유형]
동창회, 송년회, 결혼식 피로연, 기업 회식, 워크숍 뒤풀이,
생일파티, 신입생 환영회, 개강/종강파티, 동호회 정모

[예약 및 문의]
- 전화: 010-7763-1981
- 카카오톡: '랑데뷰' 채널 검색
- 홈페이지: www.rangdv.com
"""

TOPICS = [
    ("강남 동창회 장소 추천", "오랜만에 만나는 친구들과 프라이빗한 동창회를 위한 최고의 공간"),
    ("논현역 회식 장소 추천", "직장인 회식을 특별하게 만들어주는 강남 프라이빗 공간"),
    ("강남 피로연 장소 추천", "결혼식 피로연을 완벽하게 즐길 수 있는 프라이빗 공간"),
    ("강남 생일파티 장소 추천", "세상에 하나밖에 없는 나만의 생일 파티를 위한 공간"),
    ("논현동 대관 파티룸 추천", "강남 최고의 프라이빗 통대관 술집 랑데뷰"),
    ("강남 단체모임 장소 추천", "20~50명 단체모임을 완벽하게 해결하는 공간"),
    ("신논현역 근처 회식 장소", "신논현역 인근 최고의 단체 회식 및 모임 공간"),
    ("강남 기업 워크숍 뒤풀이 장소", "세미나와 회식을 한 번에 해결하는 스마트한 공간"),
    ("논현역 종강파티 장소 추천", "학생들의 종강파티 필수 코스, 랑데뷰 강남논현본점"),
    ("강남 송년회 장소 추천", "한 해를 마무리하는 특별한 송년회 공간"),
    ("강남 신입사원 환영회 장소", "신입사원이 놀랄 만한 환영회를 위한 프라이빗 공간"),
    ("논현동 프라이빗 술집 추천", "강남 유일 대관비 무료, 프라이빗 통대관 술집"),
]

HASHTAGS = "#강남단체술집 #논현역회식장소 #신논현역회식 #논현동대관술집 #강남피로연장소 #랑데뷰강남논현본점 #강남모임장소 #강남통대관 #논현동맛집 #강남가성비술집"


def generate_blog_post(topic_title, topic_angle):
    client = anthropic.Anthropic()

    today = datetime.now().strftime("%Y년 %m월 %d일")

    prompt = f"""당신은 '랑데뷰 강남논현본점' 업장의 블로그 마케터입니다.
아래 업장 정보를 바탕으로 실제 방문자에게 도움이 되는 티스토리 블로그 포스팅을 작성해주세요.

[업장 정보]
{VENUE_INFO}

[오늘의 주제] {topic_title}
[접근 각도] {topic_angle}
[작성일] {today}

[요구사항]
1. SEO 최적화 제목 (핵심 키워드: 논현역, 강남, 랑데뷰 포함)
2. 2000자 이상의 충실한 본문 (HTML 형식)
3. 친근하고 자연스러운 말투
4. 실제 방문자가 궁금해할 내용 (위치, 주차, 인원, 비용, 음식 등) 상세 설명
5. 마지막에 예약 유도 문구 + 연락처 명시
6. HTML 포맷:
   - 소제목: <h2>, <h3>
   - 강조: <strong>
   - 문단: <p>
   - 목록: <ul><li>

[응답 형식 - 반드시 아래 형식 준수]
TITLE: [제목]
CONTENT:
[HTML 본문]"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    response = message.content[0].text

    title_line = next(line for line in response.split('\n') if line.startswith('TITLE:'))
    title = title_line.replace('TITLE:', '').strip()

    content_start = response.find('CONTENT:') + len('CONTENT:')
    content = response[content_start:].strip()
    content += f"\n\n<p>{HASHTAGS}</p>"

    return title, content


def post_to_tistory(title, content):
    access_token = os.environ['TISTORY_ACCESS_TOKEN']
    blog_name = os.environ.get('TISTORY_BLOG_NAME', 'woong38')

    url = 'https://www.tistory.com/apis/post/write'
    data = {
        'access_token': access_token,
        'output': 'json',
        'blogName': blog_name,
        'title': title,
        'content': content,
        'visibility': '3',  # 공개 발행
        'tag': '강남단체술집,논현역회식,강남피로연,랑데뷰,강남모임장소',
        'acceptComment': '1',
    }

    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()


def main():
    today = datetime.now()
    # 날짜 기반으로 주제 순환 (매번 다른 주제)
    topic_index = (today.year * 366 + today.timetuple().tm_yday) % len(TOPICS)
    topic_title, topic_angle = TOPICS[topic_index]

    print(f"[발행 시작] {today.strftime('%Y-%m-%d %H:%M')}")
    print(f"[주제] {topic_title}")

    title, content = generate_blog_post(topic_title, topic_angle)
    print(f"[생성된 제목] {title}")

    result = post_to_tistory(title, content)
    post_url = result.get('tistory', {}).get('item', {}).get('url', '확인 불가')
    print(f"[발행 완료] {post_url}")


if __name__ == '__main__':
    main()
