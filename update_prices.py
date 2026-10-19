"""Fetch 12 US stocks' adjusted-free regular-session closes and current market caps."""
import json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import yfinance as yf

TICKERS = ["JPM", "C", "BAC", "WFC", "GS", "MS", "BLK", "V", "MA", "AXP", "HOOD", "COIN"]
OUTPUT = Path(__file__).parent / "data" / "prices.json"


def gather(ticker):
    t = yf.Ticker(ticker)
    # auto_adjust=False: regular daily closing prices without dividend adjustment.
    hist = t.history(period="1mo", interval="1d", auto_adjust=False)
    closes = hist["Close"].dropna()
    if len(closes) < 2:
        raise ValueError("not enough daily closing prices")
    latest = closes.index[-1].date()
    current, previous = float(closes.iloc[-1]), float(closes.iloc[-2])
    # Previous week's last available close (Friday, or previous trading day on a market holiday).
    monday = latest.toordinal() - latest.weekday()
    old = [(dt.date(),float(price)) for dt, price in closes.items() if dt.date().toordinal() < monday]
    if not old:
        raise ValueError("previous week closing price missing")
    prev_week_date, prev_week_close = old[-1]
    cap = None
    try:
        cap = t.fast_info.get("market_cap")
    except Exception:
        pass
    if not cap:
        try:
            cap = t.info.get("marketCap")
        except Exception:
            pass
    return {"daily":round((current / previous - 1)*100, 4),
            "weekly":round((current / prev_week_close - 1)*100, 4),
            "market_cap":int(cap) if cap else None,
            "close":round(current,4), "date":latest.isoformat(),
            "previous_week_date":prev_week_date.isoformat()}


def main():
    previous = {}
    if OUTPUT.exists():
        try:
            previous = json.loads(OUTPUT.read_text()).get("stocks", {})
        except Exception:
            pass
    result = {}
    for symbol in TICKERS:
        try:
            result[symbol] = gather(symbol)
            print(symbol, result[symbol]["date"], result[symbol]["daily"])
        except Exception as exc:
            # Never show fabricated values, and never retain stale prices after failed fetching.
            print("FAILED", symbol, str(exc))
            result[symbol] = {"daily":None, "weekly":None,"market_cap":None}
    dates = [s["date"] for s in result.values() if s.get("date")]
    # If some quotes lag, hide them rather than mix return dates in one heatmap.
    date = max(dates, default="")
    for symbol,r in result.items():
        if r.get("date")!=date:
            result[symbol] = {"daily":None,"weekly":None,"market_cap":None}
    data={"as_of":date,"generated_at_utc":datetime.now(timezone.utc).isoformat(),"stocks":result}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
    if not date:
        raise RuntimeError("All stock price downloads failed")

if __name__ == "__main__":
    main()
