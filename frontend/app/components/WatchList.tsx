"use client";

import { StockItem } from "../types";

interface Props {
  stocks: StockItem[];
  selected: StockItem | null;
  onSelect: (stock: StockItem) => void;
  onDelete: (ticker: string) => void;
}

export default function WatchList({ stocks, selected, onSelect, onDelete }: Props) {
  if (stocks.length === 0) {
    return (
      <div className="text-center py-10 text-gray-500">
        <p className="text-4xl mb-2">📋</p>
        <p className="text-sm">등록된 종목이 없습니다</p>
        <p className="text-xs mt-1 text-gray-600">위 검색창에서 종목을 추가하세요</p>
      </div>
    );
  }

  return (
    <ul className="space-y-2">
      {stocks.map((stock) => {
        const isActive = selected?.ticker === stock.ticker;
        return (
          <li
            key={stock.ticker}
            className={`flex items-center justify-between px-4 py-3 rounded-lg cursor-pointer transition-all border ${
              isActive
                ? "bg-blue-900/40 border-blue-500 text-white"
                : "bg-gray-800 border-gray-700 hover:border-gray-500 text-gray-200"
            }`}
            onClick={() => onSelect(stock)}
          >
            <div>
              <p className="font-medium">{stock.name}</p>
              <p className="text-xs text-gray-400">
                {stock.ticker} · {stock.market}
              </p>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(stock.ticker);
              }}
              className="text-gray-500 hover:text-red-400 transition-colors px-2 py-1 rounded text-sm"
              title="삭제"
            >
              삭제
            </button>
          </li>
        );
      })}
    </ul>
  );
}
