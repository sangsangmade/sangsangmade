import httpx
from bs4 import BeautifulSoup


class NewsService:
    _headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    async def get_news(self, ticker: str, stock_name: str) -> list[dict]:
        news = []
        try:
            async with httpx.AsyncClient(timeout=15, headers=self._headers) as client:
                res = await client.get(
                    "https://finance.naver.com/item/news_news.naver",
                    params={"code": ticker, "page": 1},
                )
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                table = soup.find("table", class_="type5")
                if table:
                    for row in table.find_all("tr"):
                        title_td = row.find("td", class_="title")
                        date_td  = row.find("td", class_="date")
                        if not title_td or not date_td:
                            continue
                        a = title_td.find("a")
                        title = a.get_text(strip=True) if a else ""
                        href  = a.get("href", "") if a else ""
                        date  = date_td.get_text(strip=True)
                        if title:
                            news.append({
                                "title": title,
                                "date": date,
                                "url": (
                                    f"https://finance.naver.com{href}"
                                    if href.startswith("/")
                                    else href
                                ),
                                "source": "네이버 금융",
                            })
                        if len(news) >= 10:
                            break
        except Exception as e:
            print(f"[News] fetch error: {e}")
        return news
