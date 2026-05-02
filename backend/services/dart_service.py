import httpx
import zipfile
import io
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional
import asyncio

DART_BASE = "https://opendart.fss.or.kr/api"


class DartService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._corp_map: dict[str, str] = {}   # name → corp_code
        self._loaded = False

    async def _load_corp_codes(self):
        if self._loaded or not self.api_key:
            return
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                res = await client.get(
                    f"{DART_BASE}/corpCode.xml",
                    params={"crtfc_key": self.api_key},
                )
            if res.status_code != 200:
                return
            with zipfile.ZipFile(io.BytesIO(res.content)) as z:
                with z.open("CORPCODE.xml") as f:
                    root = ET.parse(f).getroot()
            for item in root.findall(".//list"):
                name = item.findtext("corp_name", "")
                code = item.findtext("corp_code", "")
                if name and code:
                    self._corp_map[name] = code
            self._loaded = True
        except Exception as e:
            print(f"[DART] corp code load error: {e}")

    async def find_corp_code(self, stock_name: str) -> Optional[str]:
        await self._load_corp_codes()
        if stock_name in self._corp_map:
            return self._corp_map[stock_name]
        for name, code in self._corp_map.items():
            if stock_name in name:
                return code
        return None

    async def get_company_data(self, corp_code: Optional[str]) -> dict:
        if not self.api_key or not corp_code:
            return {"available": False, "reason": "API 키 또는 기업 코드 없음"}

        year = str(datetime.now().year - 1)
        async with httpx.AsyncClient(timeout=20) as client:
            tasks = {
                "company": client.get(f"{DART_BASE}/company.json",
                    params={"crtfc_key": self.api_key, "corp_code": corp_code}),
                "finance": client.get(f"{DART_BASE}/fnlttSinglAcnt.json",
                    params={"crtfc_key": self.api_key, "corp_code": corp_code,
                            "bsns_year": year, "reprt_code": "11011"}),
                "shareholders": client.get(f"{DART_BASE}/majorstock.json",
                    params={"crtfc_key": self.api_key, "corp_code": corp_code}),
                "disclosures": client.get(f"{DART_BASE}/list.json",
                    params={"crtfc_key": self.api_key, "corp_code": corp_code,
                            "bgn_de": "20230101", "page_count": "20"}),
            }
            responses = {}
            for key, task in tasks.items():
                try:
                    responses[key] = await task
                except Exception as e:
                    responses[key] = None

        result: dict = {"available": True}

        # 기업 기본정보
        if responses.get("company"):
            d = responses["company"].json()
            if d.get("status") == "000":
                result["company"] = {
                    "name": d.get("corp_name"),
                    "ceo": d.get("ceo_nm"),
                    "listing_date": d.get("est_dt"),
                    "homepage": d.get("hm_url"),
                    "industry_code": d.get("induty_code"),
                }

        # 재무정보
        if responses.get("finance"):
            d = responses["finance"].json()
            if d.get("status") == "000" and d.get("list"):
                fin: dict = {}
                for item in d["list"]:
                    acc = item.get("account_nm", "")
                    amt = item.get("thstrm_amount", "0").replace(",", "")
                    if "자본총계" in acc:
                        fin["total_equity"] = amt
                    elif "부채총계" in acc:
                        fin["total_liabilities"] = amt
                    elif "당기순이익" in acc:
                        fin["net_income"] = amt
                    elif "매출액" in acc:
                        fin["revenue"] = amt
                    elif "유보율" in acc or "이익잉여금" in acc:
                        fin["retained_earnings"] = amt
                # 부채비율 계산
                try:
                    eq = int(fin.get("total_equity", 0))
                    li = int(fin.get("total_liabilities", 0))
                    if eq > 0:
                        fin["debt_ratio"] = round(li / eq * 100, 1)
                except Exception:
                    pass
                result["financials"] = fin

        # 주요주주
        if responses.get("shareholders"):
            d = responses["shareholders"].json()
            if d.get("status") == "000" and d.get("list"):
                result["shareholders"] = [
                    {
                        "name": s.get("nm"),
                        "relation": s.get("relate"),
                        "shares": s.get("stock_co"),
                        "ratio": s.get("stock_ratio"),
                    }
                    for s in d["list"][:5]
                ]

        # 공시목록
        if responses.get("disclosures"):
            d = responses["disclosures"].json()
            if d.get("status") == "000" and d.get("list"):
                result["disclosures"] = [
                    {
                        "title": x.get("report_nm"),
                        "date": x.get("rcept_dt"),
                        "submitter": x.get("flr_nm"),
                        "url": f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={x.get('rcept_no', '')}",
                    }
                    for x in d["list"][:10]
                ]

                # CB / 유상증자 감지
                cb_list, rights_list = [], []
                for x in d["list"]:
                    title = x.get("report_nm", "")
                    if "전환사채" in title:
                        cb_list.append(title)
                    elif "유상증자" in title:
                        rights_list.append(title)
                result["cb_count"] = len(cb_list)
                result["rights_offering_count"] = len(rights_list)

        return result
