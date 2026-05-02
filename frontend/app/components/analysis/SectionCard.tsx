"use client";

import { ElementAnalysis } from "../../types";

const SIGNAL_CONFIG = {
  bullish: { label: "긍정",  bg: "bg-green-900/30",  border: "border-green-700",  text: "text-green-400",  bar: "bg-green-500"  },
  bearish: { label: "부정",  bg: "bg-red-900/30",    border: "border-red-700",    text: "text-red-400",    bar: "bg-red-500"    },
  neutral: { label: "중립",  bg: "bg-yellow-900/20", border: "border-yellow-700", text: "text-yellow-400", bar: "bg-yellow-500" },
};

interface Props {
  title: string;
  icon: string;
  element: string;
  data: ElementAnalysis;
  dartVerified?: boolean;
}

export default function SectionCard({ title, icon, element, data, dartVerified }: Props) {
  const cfg = SIGNAL_CONFIG[data.signal] || SIGNAL_CONFIG.neutral;

  return (
    <div className={`rounded-xl border p-5 ${cfg.bg} ${cfg.border} transition-all`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-xl">{icon}</span>
          <div>
            <p className="text-xs text-gray-400">{element}</p>
            <h3 className="font-semibold text-white text-sm">{title}</h3>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {dartVerified !== undefined && (
            <span className={`text-xs px-2 py-0.5 rounded-full border ${dartVerified ? "border-blue-500 text-blue-400" : "border-gray-600 text-gray-500"}`}>
              {dartVerified ? "DART확인" : "DART미확인"}
            </span>
          )}
          <span className={`text-xs font-medium px-2 py-1 rounded-full ${cfg.text} bg-black/30`}>
            {cfg.label}
          </span>
        </div>
      </div>

      {/* Score bar */}
      <div className="mb-4">
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>점수</span>
          <span className={`font-bold ${cfg.text}`}>{data.score}</span>
        </div>
        <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-700 ${cfg.bar}`}
            style={{ width: `${data.score}%` }}
          />
        </div>
      </div>

      {/* Summary */}
      <p className="text-sm text-gray-300 leading-relaxed mb-3">{data.summary}</p>

      {/* Key points */}
      {data.key_points?.length > 0 && (
        <ul className="space-y-1 mb-3">
          {data.key_points.map((pt, i) => (
            <li key={i} className="flex items-start gap-2 text-xs text-gray-400">
              <span className={`mt-0.5 flex-shrink-0 ${cfg.text}`}>▸</span>
              <span>{pt}</span>
            </li>
          ))}
        </ul>
      )}

      {/* Data basis */}
      {data.data_basis?.length > 0 && (
        <div className="mt-2 pt-2 border-t border-gray-700/50">
          <p className="text-xs text-gray-500 mb-1">근거 데이터</p>
          <div className="flex flex-wrap gap-1">
            {data.data_basis.map((b, i) => (
              <span key={i} className="text-xs bg-gray-700/50 text-gray-400 px-2 py-0.5 rounded">
                {b}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
