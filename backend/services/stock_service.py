import yfinance as yf
import pandas as pd
import numpy as np
from pykrx import stock as pykrx_stock
from datetime import datetime, timedelta
from typing import Optional


class StockService:
    async def search(self, query: str) -> list[dict]:
        results = []
        query_lower = query.lower()

        for market, suffix in [("KOSPI", ".KS"), ("KOSDAQ", ".KQ")]:
            try:
                tickers = pykrx_stock.get_market_ticker_list(market=market)
                for ticker in tickers:
                    name = pykrx_stock.get_market_ticker_name(ticker)
                    if query_lower in name.lower() or query in ticker:
                        results.append({
                            "ticker": ticker,
                            "name": name,
                            "market": market,
                            "yf_ticker": f"{ticker}{suffix}",
                        })
                        if len(results) >= 10:
                            return results
            except Exception:
                pass

        return results

    async def get_detailed_data(self, ticker_kr: str) -> dict:
        yf_ticker = f"{ticker_kr}.KS"
        yf_stock = yf.Ticker(yf_ticker)
        hist = yf_stock.history(period="1y")

        if hist.empty:
            yf_ticker = f"{ticker_kr}.KQ"
            yf_stock = yf.Ticker(yf_ticker)
            hist = yf_stock.history(period="1y")

        if hist.empty:
            raise ValueError(f"종목 데이터를 찾을 수 없습니다: {ticker_kr}")

        close = hist["Close"]
        volume = hist["Volume"]
        high = hist["High"]
        low = hist["Low"]
        open_ = hist["Open"]

        ma5   = close.rolling(5).mean()
        ma10  = close.rolling(10).mean()
        ma20  = close.rolling(20).mean()
        ma60  = close.rolling(60).mean()
        ma120 = close.rolling(120).mean()
        ma240 = close.rolling(240).mean()

        current_price = float(close.iloc[-1])

        def safe_float(s):
            v = s.iloc[-1]
            return float(v) if not pd.isna(v) else None

        # 정배열 체크
        ma_aligned = False
        if safe_float(ma5) and safe_float(ma10) and safe_float(ma20) and safe_float(ma60):
            ma_aligned = safe_float(ma5) > safe_float(ma10) > safe_float(ma20) > safe_float(ma60)

        # 골든/데드크로스
        golden_cross = False
        dead_cross = False
        if len(ma5) > 1 and len(ma20) > 1 and safe_float(ma5) and safe_float(ma20):
            golden_cross = bool(ma5.iloc[-1] > ma20.iloc[-1] and ma5.iloc[-2] <= ma20.iloc[-2])
            dead_cross   = bool(ma5.iloc[-1] < ma20.iloc[-1] and ma5.iloc[-2] >= ma20.iloc[-2])

        # 52주 위치
        high_52w = float(high.rolling(252).max().iloc[-1])
        low_52w  = float(low.rolling(252).min().iloc[-1])
        position_52w = round((current_price - low_52w) / (high_52w - low_52w) * 100, 1) if high_52w > low_52w else 50.0

        # 거래량 비율
        avg_vol_20 = float(volume.rolling(20).mean().iloc[-1])
        vol_ratio  = round(float(volume.iloc[-1]) / avg_vol_20, 2) if avg_vol_20 > 0 else 0.0

        # 최근 5일 캔들
        recent_candles = []
        for i in range(min(5, len(hist))):
            idx = -(i + 1)
            row = hist.iloc[idx]
            rng = float(row["High"]) - float(row["Low"])
            body = abs(float(row["Close"]) - float(row["Open"]))
            upper = float(row["High"]) - max(float(row["Open"]), float(row["Close"]))
            lower = min(float(row["Open"]), float(row["Close"])) - float(row["Low"])
            recent_candles.append({
                "date": hist.index[idx].strftime("%Y-%m-%d"),
                "open": round(float(row["Open"]), 0),
                "high": round(float(row["High"]), 0),
                "low":  round(float(row["Low"]), 0),
                "close": round(float(row["Close"]), 0),
                "volume": int(row["Volume"]),
                "type": "양봉" if row["Close"] > row["Open"] else "음봉",
                "body_ratio": round(body / rng, 2) if rng > 0 else 0,
                "upper_wick_ratio": round(upper / rng, 2) if rng > 0 else 0,
                "lower_wick_ratio": round(lower / rng, 2) if rng > 0 else 0,
            })

        # 발행/유통주식수 추정
        try:
            info = yf_stock.info
            shares_outstanding = info.get("sharesOutstanding")
            float_shares = info.get("floatShares")
            market_cap = info.get("marketCap")
        except Exception:
            info, shares_outstanding, float_shares, market_cap = {}, None, None, None

        # 유통주식수 대비 회전율
        turnover_rate = None
        if float_shares and float_shares > 0:
            turnover_rate = round(float(volume.iloc[-1]) / float_shares * 100, 2)

        return {
            "ticker": ticker_kr,
            "yf_ticker": yf_ticker,
            "current_price": current_price,
            "change_1d": round(float(close.iloc[-1] - close.iloc[-2]), 0) if len(close) > 1 else 0,
            "change_pct_1d": round(float((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100), 2) if len(close) > 1 else 0,
            "high_52w": high_52w,
            "low_52w": low_52w,
            "position_52w": position_52w,
            "moving_averages": {
                "ma5": safe_float(ma5),
                "ma10": safe_float(ma10),
                "ma20": safe_float(ma20),
                "ma60": safe_float(ma60),
                "ma120": safe_float(ma120),
                "ma240": safe_float(ma240),
            },
            "ma_aligned": ma_aligned,
            "golden_cross": golden_cross,
            "dead_cross": dead_cross,
            "volume_current": int(volume.iloc[-1]),
            "volume_avg_20d": round(avg_vol_20, 0),
            "volume_ratio": vol_ratio,
            "turnover_rate": turnover_rate,
            "recent_candles": recent_candles,
            "shares_outstanding": shares_outstanding,
            "float_shares": float_shares,
            "market_cap": market_cap,
            "pe_ratio": info.get("trailingPE"),
            "pb_ratio": info.get("priceToBook"),
            "debt_to_equity": info.get("debtToEquity"),
        }

    async def get_market_data(self) -> dict:
        indices = {
            "KOSPI": "^KS11",
            "KOSDAQ": "^KQ11",
            "S&P500": "^GSPC",
            "NASDAQ": "^IXIC",
            "다우존스": "^DJI",
            "USD/KRW": "KRW=X",
            "국고채10년": "KR10YT=RR",
        }
        result = {}
        for name, sym in indices.items():
            try:
                data = yf.Ticker(sym).history(period="5d")
                if not data.empty:
                    cur  = float(data["Close"].iloc[-1])
                    prev = float(data["Close"].iloc[-2]) if len(data) >= 2 else cur
                    chg  = round((cur - prev) / prev * 100, 2) if prev else 0
                    result[name] = {
                        "value": round(cur, 2),
                        "change_pct": chg,
                        "signal": "up" if chg > 0 else "down" if chg < 0 else "flat",
                    }
            except Exception:
                pass
        return result
