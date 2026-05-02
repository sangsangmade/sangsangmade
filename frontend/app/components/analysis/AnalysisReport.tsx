"use client";

import { AnalyzeResponse } from "../../types";
import SectionCard from "./SectionCard";

const ELEMENTS = [
  { key: "market",         title: "시장",       icon: "🌐", element: "제1요소" },
  { key: "trend",          title: "트렌드",      icon: "📈", element: "제2요소" },
  { key: "company",        title: "회사·공시",   icon: "🏢", element: "제3요소" },
  { key: "news",           title: "뉴스·재료",   icon: "📰", element: "제4요소" },
  { key: "candlestick",    title: "캔들",        icon: "🕯️", element: "제5요소" },
  { key: "moving_average", title: "이동평균선",   icon: "📉", element: "제6요소" },
  { key: "volume",         title: "거래량",      icon: "📊", element: "제7요소" },
  { key: "supply_zone",    title: "매물대",      icon: "🧱", element: "제8요소" },
] as const;

const REC_CONFIG: Record<string, { color: string; bg: string }> = {
  "매수검토": { color: "text-green-400",  bg: "bg-green-900/30 border-green-600"  },
  "관망":     { color: "text-yellow-400", bg: "bg-yellow-900/20 border-yellow-600" },
  "매도검토": { color: "text-red-400",    bg: "bg-red-900/30 border-red-600"      },
  "위험":     { color: "text-red-300",    bg: "bg-red-950/40 border-red-500"      },
};

interface Props {
  data: AnalyzeResponse;
}

export default function AnalysisReport({ data }: Props) {
  const { stock, analysis, news, market } = data;
  const overall = analysis.overall;
  const raw     = analysis.raw_data;
  const rec     = REC_CONFIG[overall.recommendation] || REC_CONFIG["관망"];

  const fmt = (n?: number | null) =>
    n == null ? "-" : n >= 1e12 ? `${(n / 1e12).toFixed(1)}조` : n >= 1e8 ? `${(n / 1e8).toFixed(0)}억` : n.toLocaleString();

  return (
    <div className="space-y-6">
      {/* 종목 헤더 */}
      <div className="bg-gray-800 rounded-xl p-5 border border-gray-700">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold text-white">{stock.name}</h2>
            <p className="text-gray-400 text-sm mt-0.5">{stock.ticker} · {raw.dart_available ? "DART 연동됨" : "DART 미연동"}</p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-white">{stock.current_price?.toLocaleString()}원</p>
            <p className={`text-sm font-medium ${(stock.change_pct_1d ?? 0) >= 0 ? "text-green-400" : "text-red-400"}`}>
              {(stock.change_pct_1d ?? 0) >= 0 ? "▲" : "▼"} {Math.abs(stock.change_pct_1d ?? 0).toFixed(2)}%
            </p>
          </div>
        </div>

        {/* 빠른 지표 */}
        <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: "52주 위치",    value: `${raw.position_52w?.toFixed(1)}%` },
            { label: "거래량 비율",  value: `${raw.volume_ratio?.toFixed(2)}x` },
            { label: "정배열",       value: raw.ma_aligned ? "✅ 정배열" : "❌ 역배열" },
            { label: "뉴스 수집",    value: `${raw.news_count}건` },
          ].map((item) => (
            <div key={item.label} className="bg-gray-700/50 rounded-lg p-3">
              <p className="text-xs text-gray-400">{item.label}</p>
              <p className="text-sm font-medium text-white mt-0.5">{item.value}</p>
            </div>
          ))}
        </div>
      </div>

      {/* 종합 판정 */}
      <div className={`rounded-xl border p-5 ${rec.bg}`}>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-bold text-white">종합 판정</h3>
          <div className="flex items-center gap-3">
            <span className="text-3xl font-bold text-white">{overall.score}</span>
            <span className={`text-lg font-bold px-3 py-1 rounded-full bg-black/30 ${rec.color}`}>
              {overall.recommendation}
            </span>
          </div>
        </div>
        <div className="h-2 bg-gray-700 rounded-full mb-4 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-1000 ${
              overall.score >= 65 ? "bg-green-500" : overall.score >= 45 ? "bg-yellow-500" : "bg-red-500"
            }`}
            style={{ width: `${overall.score}%` }}
          />
        </div>
        <p className="text-sm text-gray-300 leading-relaxed mb-4">{overall.summary}</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {overall.positive_factors?.length > 0 && (
            <div>
              <p className="text-xs text-green-400 mb-1 font-medium">긍정 요소</p>
              <ul className="space-y-1">
                {overall.positive_factors.map((f, i) => (
                  <li key={i} className="text-xs text-gray-300 flex gap-1.5"><span className="text-green-500">+</span>{f}</li>
                ))}
              </ul>
            </div>
          )}
          {overall.risk_factors?.length > 0 && (
            <div>
              <p className="text-xs text-red-400 mb-1 font-medium">리스크 요소</p>
              <ul className="space-y-1">
                {overall.risk_factors.map((f, i) => (
                  <li key={i} className="text-xs text-gray-300 flex gap-1.5"><span className="text-red-500">-</span>{f}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* 8요소 그리드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {ELEMENTS.map(({ key, title, icon, element }) => {
          const el = analysis.elements[key as keyof typeof analysis.elements];
          if (!el) return null;
          return (
            <SectionCard
              key={key}
              title={title}
              icon={icon}
              element={element}
              data={el}
              dartVerified={key === "company" ? el.dart_verified : undefined}
            />
          );
        })}
      </div>

      {/* 시장 현황 */}
      {Object.keys(market).length > 0 && (
        <div className="bg-gray-800 rounded-xl p-5 border border-gray-700">
          <h3 className="text-sm font-semibold text-gray-300 mb-3">시장 현황</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {Object.entries(market).map(([name, val]) => (
              <div key={name} className="bg-gray-700/50 rounded-lg p-3">
                <p className="text-xs text-gray-400">{name}</p>
                <p className="text-sm font-medium text-white mt-0.5">
                  {val.value?.toLocaleString()}
                </p>
                <p className={`text-xs ${val.signal === "up" ? "text-green-400" : val.signal === "down" ? "text-red-400" : "text-gray-400"}`}>
                  {val.signal === "up" ? "▲" : val.signal === "down" ? "▼" : "—"} {Math.abs(val.change_pct).toFixed(2)}%
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 최근 뉴스 */}
      {news?.length > 0 && (
        <div className="bg-gray-800 rounded-xl p-5 border border-gray-700">
          <h3 className="text-sm font-semibold text-gray-300 mb-3">수집된 뉴스 ({news.length}건)</h3>
          <ul className="space-y-2">
            {news.map((n, i) => (
              <li key={i} className="flex items-start justify-between gap-4 py-2 border-b border-gray-700/50 last:border-0">
                <a
                  href={n.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-gray-300 hover:text-blue-400 transition-colors line-clamp-2 flex-1"
                >
                  {n.title}
                </a>
                <span className="text-xs text-gray-500 whitespace-nowrap flex-shrink-0">{n.date}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <p className="text-xs text-gray-600 text-center">
        분석 시각: {new Date(raw.analyzed_at).toLocaleString("ko-KR")} · DART 공시 기반 할루시네이션 검증 적용
      </p>
    </div>
  );
}
