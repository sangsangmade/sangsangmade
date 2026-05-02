"use client";

import { useState, useEffect } from "react";
import StockSearch from "./components/StockSearch";
import WatchList from "./components/WatchList";
import AnalysisReport from "./components/analysis/AnalysisReport";
import { StockItem, AnalyzeResponse } from "./types";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const STORAGE_KEY = "stock_watchlist";

export default function Home() {
  const [watchlist, setWatchlist] = useState<StockItem[]>([]);
  const [selected, setSelected] = useState<StockItem | null>(null);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) setWatchlist(JSON.parse(saved));
  }, []);

  const saveList = (list: StockItem[]) => {
    setWatchlist(list);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
  };

  const addStock = (stock: StockItem) => {
    if (watchlist.find((s) => s.ticker === stock.ticker)) return;
    saveList([...watchlist, stock]);
  };

  const deleteStock = (ticker: string) => {
    saveList(watchlist.filter((s) => s.ticker !== ticker));
    if (selected?.ticker === ticker) {
      setSelected(null);
      setResult(null);
    }
  };

  const analyze = async (stock: StockItem) => {
    setSelected(stock);
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch(`${API}/api/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticker: stock.ticker, stock_name: stock.name }),
      });
      if (!res.ok) {
        const d = await res.json();
        throw new Error(d.detail || "분석 실패");
      }
      setResult(await res.json());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "알 수 없는 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-950 text-white">
      <header className="border-b border-gray-800 bg-gray-900/80 backdrop-blur sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center gap-3">
          <span className="text-2xl">📊</span>
          <div>
            <h1 className="text-lg font-bold leading-none">주식 8요소 분석기</h1>
            <p className="text-xs text-gray-400 mt-0.5">발롱 프레임워크 · DART 공시 검증</p>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-6">
          <aside className="space-y-4">
            <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
              <h2 className="text-sm font-semibold text-gray-300 mb-3">종목 등록</h2>
              <StockSearch onAdd={addStock} />
            </div>

            <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-semibold text-gray-300">등록 종목</h2>
                <span className="text-xs text-gray-500">{watchlist.length}개</span>
              </div>
              <WatchList
                stocks={watchlist}
                selected={selected}
                onSelect={analyze}
                onDelete={deleteStock}
              />
            </div>
          </aside>

          <section>
            {loading && (
              <div className="flex flex-col items-center justify-center py-32 gap-4">
                <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
                <div className="text-center">
                  <p className="text-white font-medium">{selected?.name} 분석 중...</p>
                  <p className="text-gray-400 text-sm mt-1">DART 공시 · 차트 · 뉴스 수집 중</p>
                </div>
              </div>
            )}

            {error && (
              <div className="bg-red-900/30 border border-red-700 rounded-xl p-6 text-center">
                <p className="text-red-400 font-medium">분석 실패</p>
                <p className="text-gray-400 text-sm mt-1">{error}</p>
                <button
                  onClick={() => selected && analyze(selected)}
                  className="mt-4 px-4 py-2 bg-red-800 hover:bg-red-700 rounded-lg text-sm transition-colors"
                >
                  다시 시도
                </button>
              </div>
            )}

            {result && !loading && <AnalysisReport data={result} />}

            {!loading && !result && !error && (
              <div className="flex flex-col items-center justify-center py-32 text-gray-600">
                <p className="text-6xl mb-4">📊</p>
                <p className="text-lg font-medium text-gray-500">종목을 선택해 분석을 시작하세요</p>
                <p className="text-sm mt-2 text-center max-w-sm">
                  좌측에서 종목을 등록하고 클릭하면<br />8요소 분석이 시작됩니다
                </p>
              </div>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}
