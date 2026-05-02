import anthropic
import json
import re
from datetime import datetime


class AnalysisService:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else None

    async def analyze(
        self,
        stock_name: str,
        ticker: str,
        stock_data: dict,
        dart_data: dict,
        news_data: list,
        market_data: dict,
    ) -> dict:
        payload = {
            "종목명": stock_name,
            "티커": ticker,
            "시장데이터": market_data,
            "주가및기술지표": {
                "현재가": stock_data.get("current_price"),
                "전일대비(%)": stock_data.get("change_pct_1d"),
                "52주_최고": stock_data.get("high_52w"),
                "52주_최저": stock_data.get("low_52w"),
                "52주_위치(%)": stock_data.get("position_52w"),
                "이동평균선": stock_data.get("moving_averages"),
                "정배열여부": stock_data.get("ma_aligned"),
                "골든크로스": stock_data.get("golden_cross"),
                "데드크로스": stock_data.get("dead_cross"),
                "거래량_비율(20일평균대비)": stock_data.get("volume_ratio"),
                "유통주식수_회전율(%)": stock_data.get("turnover_rate"),
                "최근5일캔들": stock_data.get("recent_candles", []),
                "PER": stock_data.get("pe_ratio"),
                "PBR": stock_data.get("pb_ratio"),
                "부채비율_yf": stock_data.get("debt_to_equity"),
            },
            "DART공시데이터": {
                "기업정보": dart_data.get("company"),
                "재무정보": dart_data.get("financials"),
                "주요주주": dart_data.get("shareholders"),
                "최근공시": dart_data.get("disclosures", [])[:5],
                "전환사채_발행건수": dart_data.get("cb_count", 0),
                "유상증자_발행건수": dart_data.get("rights_offering_count", 0),
                "DART_연동여부": dart_data.get("available", False),
            },
            "최근뉴스": [n["title"] for n in news_data[:8]],
        }

        prompt = f"""당신은 발롱의 '주식 8요소 검증' 프레임워크를 기반으로 분석하는 한국 주식 전문 애널리스트입니다.
아래의 **실제 데이터**를 바탕으로 8요소를 분석하고, 데이터에 없는 내용은 절대 추측하지 마세요.

## 실제 데이터
```json
{json.dumps(payload, ensure_ascii=False, indent=2)}
```

## 출력 형식 (JSON만 출력, 설명 금지)
```json
{{
  "elements": {{
    "market": {{
      "signal": "bullish|bearish|neutral",
      "score": 0~100,
      "summary": "2~3문장 한국어 분석",
      "key_points": ["포인트1", "포인트2", "포인트3"],
      "data_basis": ["근거데이터1", "근거데이터2"]
    }},
    "trend": {{
      "signal": "bullish|bearish|neutral",
      "score": 0~100,
      "summary": "2~3문장 한국어 분석",
      "key_points": ["포인트1", "포인트2"],
      "data_basis": ["근거데이터1"]
    }},
    "company": {{
      "signal": "bullish|bearish|neutral",
      "score": 0~100,
      "summary": "2~3문장 한국어 분석 (DART 데이터 기반)",
      "key_points": ["포인트1", "포인트2", "포인트3"],
      "data_basis": ["근거데이터1", "근거데이터2"],
      "dart_verified": true|false
    }},
    "news": {{
      "signal": "bullish|bearish|neutral",
      "score": 0~100,
      "summary": "2~3문장 한국어 분석",
      "key_points": ["포인트1", "포인트2"],
      "data_basis": ["근거데이터1"]
    }},
    "candlestick": {{
      "signal": "bullish|bearish|neutral",
      "score": 0~100,
      "summary": "2~3문장 한국어 분석",
      "key_points": ["포인트1", "포인트2"],
      "data_basis": ["근거데이터1"]
    }},
    "moving_average": {{
      "signal": "bullish|bearish|neutral",
      "score": 0~100,
      "summary": "2~3문장 한국어 분석",
      "key_points": ["포인트1", "포인트2"],
      "data_basis": ["근거데이터1"]
    }},
    "volume": {{
      "signal": "bullish|bearish|neutral",
      "score": 0~100,
      "summary": "2~3문장 한국어 분석",
      "key_points": ["포인트1", "포인트2"],
      "data_basis": ["근거데이터1"]
    }},
    "supply_zone": {{
      "signal": "bullish|bearish|neutral",
      "score": 0~100,
      "summary": "2~3문장 한국어 분석",
      "key_points": ["포인트1", "포인트2"],
      "data_basis": ["근거데이터1"]
    }}
  }},
  "overall": {{
    "score": 0~100,
    "recommendation": "매수검토|관망|매도검토|위험",
    "summary": "3~5문장 종합 한국어 분석",
    "positive_factors": ["긍정요소1", "긍정요소2"],
    "risk_factors": ["리스크1", "리스크2"]
  }}
}}
```

각 요소 분석 기준:
1. **시장(market)**: KOSPI/KOSDAQ/미국지수/환율 흐름 → 매크로 우호적인지 판단
2. **트렌드(trend)**: 뉴스 신선도, 섹터 이슈 단계(선점/상승/확신매수/하락), 52주 위치
3. **회사(company)**: DART 재무(부채비율100%이하, 유보율200%내외), CB/유증 빈도, 주요주주 지분율
4. **뉴스(news)**: 팩트기반(공시/정책) vs 추측성, 첫 이슈인지 재탕인지, 규모·독점여부
5. **캔들(candlestick)**: 최근캔들 위치(바닥/고점), 장대양봉/음봉 의미, 몸통·꼬리 비율
6. **이평선(moving_average)**: 정배열/역배열, 밀집→분산 신뢰도, 240일선과의 거리
7. **거래량(volume)**: 바닥권 급증(매집신호) vs 고점 대량(세력이탈), 회전율(100%이상=세력개입)
8. **매물대(supply_zone)**: 52주 위치 기반 저항/지지 추정, 쌍고점 위험성"""

        if not self.client:
            return self._fallback_analysis(stock_data, dart_data, news_data, market_data, stock_name)

        try:
            msg = self.client.messages.create(
                model="claude-opus-4-7",
                max_tokens=4096,
                system="주어진 실제 데이터만 근거로 분석하세요. 데이터가 없으면 '데이터 없음'으로 표기하고 추측하지 마세요.",
                messages=[{"role": "user", "content": prompt}],
            )
            raw = msg.content[0].text
            m = re.search(r"```json\s*(.*?)\s*```", raw, re.DOTALL)
            analysis = json.loads(m.group(1) if m else raw.strip())
        except Exception as e:
            print(f"[AI] analysis error: {e}")
            analysis = self._fallback_analysis(stock_data, dart_data, news_data, market_data, stock_name)

        analysis["raw_data"] = {
            "current_price": stock_data.get("current_price"),
            "change_pct_1d": stock_data.get("change_pct_1d"),
            "position_52w": stock_data.get("position_52w"),
            "ma_aligned": stock_data.get("ma_aligned"),
            "volume_ratio": stock_data.get("volume_ratio"),
            "dart_available": dart_data.get("available", False),
            "news_count": len(news_data),
            "analyzed_at": datetime.now().isoformat(),
        }
        return analysis

    def _fallback_analysis(self, stock_data, dart_data, news_data, market_data, stock_name) -> dict:
        pos = stock_data.get("position_52w", 50) or 50
        vol = stock_data.get("volume_ratio", 1) or 1
        ma  = stock_data.get("ma_aligned", False)

        def sig(score):
            if score >= 60: return "bullish"
            if score <= 40: return "bearish"
            return "neutral"

        market_score = 50
        for v in market_data.values():
            if isinstance(v, dict):
                if v.get("signal") == "up":   market_score += 3
                if v.get("signal") == "down":  market_score -= 3
        market_score = max(0, min(100, market_score))

        company_score = 50
        if dart_data.get("available"):
            fin = dart_data.get("financials", {})
            dr = fin.get("debt_ratio") if fin else None
            if dr is not None:
                company_score = 70 if dr < 100 else 40 if dr > 200 else 55
            cb = dart_data.get("cb_count", 0)
            ri = dart_data.get("rights_offering_count", 0)
            company_score -= cb * 5 + ri * 3
            company_score = max(0, min(100, company_score))

        ma_score = 75 if ma else 40
        if stock_data.get("golden_cross"): ma_score += 10
        if stock_data.get("dead_cross"):   ma_score -= 15
        ma_score = max(0, min(100, ma_score))

        vol_score = 55
        if 1.5 < vol <= 3:   vol_score = 70
        elif vol > 3:         vol_score = 60 if pos < 30 else 40
        elif vol < 0.5:       vol_score = 35

        supply_score = 50
        if pos < 20:   supply_score = 75
        elif pos > 80: supply_score = 30
        elif pos < 40: supply_score = 62

        overall = round((market_score*0.1 + 50*0.15 + company_score*0.2 +
                         50*0.15 + 55*0.1 + ma_score*0.1 + vol_score*0.1 + supply_score*0.1), 0)

        rec = "매수검토" if overall >= 65 else "관망" if overall >= 45 else "매도검토"

        return {
            "elements": {
                "market":         {"signal": sig(market_score),  "score": market_score,  "summary": "시장 데이터 기반 자동 분석", "key_points": [], "data_basis": []},
                "trend":          {"signal": "neutral",           "score": 50,             "summary": "트렌드 데이터 분석 대기 중", "key_points": [], "data_basis": []},
                "company":        {"signal": sig(company_score),  "score": company_score,  "summary": "DART 기반 자동 분석", "key_points": [], "data_basis": [], "dart_verified": dart_data.get("available", False)},
                "news":           {"signal": "neutral",           "score": 50,             "summary": f"{len(news_data)}건 뉴스 수집됨", "key_points": [], "data_basis": []},
                "candlestick":    {"signal": "neutral",           "score": 55,             "summary": "캔들 자동 분석", "key_points": [], "data_basis": []},
                "moving_average": {"signal": sig(ma_score),       "score": ma_score,       "summary": "이평선 자동 분석", "key_points": [], "data_basis": []},
                "volume":         {"signal": sig(vol_score),      "score": vol_score,      "summary": "거래량 자동 분석", "key_points": [], "data_basis": []},
                "supply_zone":    {"signal": sig(supply_score),   "score": supply_score,   "summary": "52주 위치 기반 자동 분석", "key_points": [], "data_basis": []},
            },
            "overall": {
                "score": int(overall),
                "recommendation": rec,
                "summary": f"{stock_name} AI 분석 키 미설정 — 자동 계산 결과입니다.",
                "positive_factors": [],
                "risk_factors": [],
            },
        }
