import yfinance as yf
import pandas as pd
import json
import os
import pandas_ta as ta
import numpy as np

# 銘柄リスト（シンボル : 表示名）
SYMBOLS = {
    "^N225": "日経225",
    "^DJI": "ダウ平均",
    "JPY=X": "ドル円",
    "GC=F": "ゴールド",
    "BTC-USD": "ビットコイン"
}

def fetch_history(symbol: str, days: int = 40) -> pd.DataFrame:
    """指定した日数の過去データを取得し、テクニカル指標を付与する"""
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=f"{days}d")
    
    if len(df) > 26:
        # MACD (12, 26, 9)
        df.ta.macd(fast=12, slow=26, signal=9, append=True)
        # RSI (14)
        df.ta.rsi(length=14, append=True)
        # SMA (5, 20)
        df.ta.sma(length=5, append=True)
        df.ta.sma(length=20, append=True)
    
    return df

def analyze_trend(df: pd.DataFrame) -> dict:
    """直近データをもとに簡単なテクニカル指標の計算とトレンド判定を行う"""
    if len(df) < 2:
        return {"current_price": 0.0, "change_pct": 0.0, "trend_summary": "Data insufficient"}

    current = df.iloc[-1]
    prev = df.iloc[-2]
    
    current_price = current['Close']
    prev_price = prev['Close']
    change_pct = ((current_price - prev_price) / prev_price) * 100
    
    # 簡易トレンド判定
    trend = "上昇" if change_pct > 0 else "下落" if change_pct < 0 else "横ばい"
    
    # NaNを安全に処理するヘルパー
    def safe_get(val):
        if pd.isna(val) or val is None:
            return None
        return round(float(val), 2)
    
    return {
        "current_price": round(current_price, 2),
        "prev_price": round(prev_price, 2),
        "change_value": round(current_price - prev_price, 2),
        "change_pct": round(change_pct, 2),
        "volume": int(current['Volume']) if 'Volume' in df.columns else 0,
        "trend_summary": f"前日比 {round(change_pct, 2)}% の{trend}",
        "technical": {
            "rsi_14": safe_get(current.get('RSI_14')),
            "macd": safe_get(current.get('MACD_12_26_9')),
            "macd_signal": safe_get(current.get('MACDs_12_26_9')),
            "macd_hist": safe_get(current.get('MACDh_12_26_9')),
            "sma_5": safe_get(current.get('SMA_5')),
            "sma_20": safe_get(current.get('SMA_20'))
        }
    }

def fetch_all() -> dict:
    """全指標のデータを取得し、JSONで出力可能な辞書を返す"""
    results = {}
    
    for symbol, name in SYMBOLS.items():
        try:
            print(f"{name} ({symbol}) のデータを取得中...")
            df = fetch_history(symbol, days=5)
            analysis = analyze_trend(df)
            
            # 各銘柄の直近終値をデバッグ用に表示
            print(f"  → 現在値: {analysis['current_price']} ({analysis['trend_summary']})")
            
            # チャート描画のための履歴データ作成
            history = df['Close'].tolist()
            dates = [d.strftime('%m/%d') for d in df.index]
            chart_data = [{"date": d, "price": p} for d, p in zip(dates, history)]
            
            results[name] = {
                "symbol": symbol,
                "analysis": analysis,
                "history": chart_data
            }
        except Exception as e:
            print(f"[{name}] データ取得失敗: {e}")
            results[name] = {"error": str(e)}

    return results

if __name__ == "__main__":
    print("=== マーケットデータ取得開始 ===")
    market_data = fetch_all()
    
    # 結果をJSONとして保存（Webアプリ直下）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "web-app", "public", "data", "market_data.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(market_data, f, ensure_ascii=False, indent=4)
        
    print(f"=== 取得完了: {output_path} に保存しました ===")

