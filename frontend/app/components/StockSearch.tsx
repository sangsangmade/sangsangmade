"use client";

import { useState, useRef, useEffect } from "react";
import { StockItem } from "../types";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Props {
  onAdd: (stock: StockItem) => void;
}

export default function StockSearch({ onAdd }: Props) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<StockItem[]>([]);
  const [selected, setSelected] = useState<StockItem | null>(null);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handle = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handle);
    return () => document.removeEventListener("mousedown", handle);
  }, []);

  const search = (q: string) => {
    setQuery(q);
    setSelected(null);
    if (timer.current) clearTimeout(timer.current);
    if (q.trim().length < 1) { setResults([]); setOpen(false); return; }
    timer.current = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await fetch(`${API}/api/search?q=${encodeURIComponent(q)}`);
        const data = await res.json();
        setResults(data.results || []);
        setOpen(true);
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);
  };

  const pick = (item: StockItem) => {
    setSelected(item);
    setQuery(`${item.name} (${item.ticker})`);
    setOpen(false);
  };

  const add = () => {
    if (!selected) return;
    onAdd(selected);
    setSelected(null);
    setQuery("");
    setResults([]);
  };

  return (
    <div ref={ref} className="relative flex gap-2">
      <div className="flex-1 relative">
        <input
          value={query}
          onChange={(e) => search(e.target.value)}
          onFocus={() => results.length > 0 && setOpen(true)}
          placeholder="종목명 또는 코드 입력 (예: 삼성전자, 005930)"
          className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 transition-colors"
        />
        {loading && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </div>
        )}
        {open && results.length > 0 && (
          <ul className="absolute z-50 w-full mt-1 bg-gray-800 border border-gray-600 rounded-lg shadow-xl overflow-hidden">
            {results.map((item) => (
              <li
                key={item.ticker}
                onClick={() => pick(item)}
                className="px-4 py-3 hover:bg-gray-700 cursor-pointer flex items-center justify-between transition-colors"
              >
                <span className="text-white font-medium">{item.name}</span>
                <span className="text-gray-400 text-sm">
                  {item.ticker} · {item.market}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
      <button
        onClick={add}
        disabled={!selected}
        className="px-5 py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 text-white font-medium rounded-lg transition-colors whitespace-nowrap"
      >
        등록
      </button>
    </div>
  );
}
