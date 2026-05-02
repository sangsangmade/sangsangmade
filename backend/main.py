import os
import asyncio
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

from services.stock_service import StockService
from services.dart_service import DartService
from services.news_service import NewsService
from services.analysis_service import AnalysisService

load_dotenv()

app = FastAPI(title="주식 8요소 분석기", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

stock_svc    = StockService()
dart_svc     = DartService(api_key=os.getenv("DART_API_KEY", ""))
news_svc     = NewsService()
analysis_svc = AnalysisService(api_key=os.getenv("ANTHROPIC_API_KEY", ""))


class AnalyzeRequest(BaseModel):
    ticker: str
    stock_name: str
    corp_code: Optional[str] = None


@app.get("/api/search")
async def search(q: str = Query(..., min_length=1)):
    try:
        results = await stock_svc.search(q)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market")
async def market():
    try:
        return await stock_svc.get_market_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest):
    try:
        # DART corp_code 자동 탐색 (없으면)
        corp_code = req.corp_code
        if not corp_code:
            corp_code = await dart_svc.find_corp_code(req.stock_name)

        # 병렬 데이터 수집
        stock_task  = stock_svc.get_detailed_data(req.ticker)
        dart_task   = dart_svc.get_company_data(corp_code)
        news_task   = news_svc.get_news(req.ticker, req.stock_name)
        market_task = stock_svc.get_market_data()

        results = await asyncio.gather(
            stock_task, dart_task, news_task, market_task,
            return_exceptions=True,
        )
        stock_data, dart_data, news_data, market_data = results

        if isinstance(stock_data, Exception):
            raise stock_data

        dart_data   = dart_data   if not isinstance(dart_data,   Exception) else {"available": False}
        news_data   = news_data   if not isinstance(news_data,   Exception) else []
        market_data = market_data if not isinstance(market_data, Exception) else {}

        analysis = await analysis_svc.analyze(
            stock_name=req.stock_name,
            ticker=req.ticker,
            stock_data=stock_data,
            dart_data=dart_data,
            news_data=news_data,
            market_data=market_data,
        )

        return {
            "stock": {
                "ticker": req.ticker,
                "name": req.stock_name,
                "current_price": stock_data.get("current_price"),
                "change_pct_1d": stock_data.get("change_pct_1d"),
                "market_cap": stock_data.get("market_cap"),
            },
            "analysis": analysis,
            "dart": dart_data,
            "news": news_data,
            "market": market_data,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}
