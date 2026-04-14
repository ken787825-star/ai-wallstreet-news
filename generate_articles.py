import os
import json
import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# .envファイルの読み込み（作業用フォルダ または HP運用フォルダ）
env_paths = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "作業用", ".env")
]

for ep in env_paths:
    if os.path.exists(ep):
        load_dotenv(ep)
        break

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY が環境変数に設定されていません。.envファイルを確認してください。")

genai.configure(api_key=api_key)

# プロンプトテンプレート
SYSTEM_PROMPT = """
あなたは非常に優秀なAIアナリストです。
以下のマーケットデータおよび「テクニカル指標（RSI、MACD、移動平均線など）」を元に、プロフェッショナルで説得力のある相場解説を作成してください。
あなたの分析は、あたかも超高機能チャート（TradingView等）を見て詳細なテクニカル分析を行っているかのような、プロフェッショナルな視点を提供する必要があります。

【ルール】
1. 冒頭の挨拶は「AIアナリストがお届けする『AIウォール街通信』です。」等とし、実在の証券会社名や誇張した肩書きは出さないこと。
2. 各銘柄ごとに、提供されたRSI（買われすぎ・売られすぎ水準）やMACD（クロスやヒストグラム）、移動平均線の位置関係を駆使して、現状のトレンドを論理的に解説すること。
3. 今日の「ファンダメンタルとテクニカルを融合した解説」と、「明日のシナリオ（上値メドや下値サポートなど）」を明確に提示すること。
4. 文字数は1銘柄あたり250〜350文字程度で、要点を絞ってプロらしく簡潔にわかりやすく解説すること。
5. 見出しはMarkdownを使用し、読みやすい体裁にすること。
"""

def generate_market_report(market_data: dict) -> str:
    """Geminiを使ってマーケットレポートを生成する"""
    
    # モデルの準備
    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=SYSTEM_PROMPT)
    
    today_str = datetime.date.today().strftime("%Y年%m月%d日")
    
    # データをプロンプトに組み込む
    data_text = f"【{today_str}のマーケットデータ】\n"
    for name, info in market_data.items():
        if "error" in info:
            data_text += f"・{name}: データ取得エラー\n"
            continue
        
        analysis = info.get("analysis", {})
        tech = analysis.get("technical", {})
        
        data_text += f"""
・{name} ({info.get('symbol')})
  現在値: {analysis.get('current_price')}
  前日比: {analysis.get('change_value')} ({analysis.get('change_pct')}%)
  トレンド: {analysis.get('trend_summary')}
  テクニカル指標:
    RSI(14): {tech.get('rsi_14')}
    MACD: {tech.get('macd')} (シグナル: {tech.get('macd_signal')}, ヒストグラム: {tech.get('macd_hist')})
    SMA(5日): {tech.get('sma_5')}
    SMA(20日): {tech.get('sma_20')}
"""

    prompt = f"""
以下の最新データを元に、本日の「AIウォール街通信」のレポート原稿を作成してください。
対象: 日経225、ダウ平均、ドル円、ゴールド、ビットコイン

{data_text}
"""
    
    print("Gemini APIにリクエストを送信中...")
    response = model.generate_content(prompt)
    return response.text

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "web-app", "public", "data")
    os.makedirs(data_dir, exist_ok=True)
    
    data_path = os.path.join(data_dir, "market_data.json")
    
    # データが存在しない場合は新規取得を実行（簡易対応）
    if not os.path.exists(data_path):
        import fetch_market_data
        market_data = fetch_market_data.fetch_all()
    else:
        with open(data_path, "r", encoding="utf-8") as f:
            market_data = json.load(f)
            
    # レポート生成
    report_text = generate_market_report(market_data)
    
    # 免責事項を追加
    footer = "\n\n---\n*※本コンテンツはAIが生成した情報提供のみを目的としており、投資勧誘や助言を意図するものではありません。投資判断はご自身の責任でお願いいたします。*"
    full_report = report_text + footer
    
    # ファイルに保存
    output_path = os.path.join(data_dir, "daily_report.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_report)
        
    print(f"=== 記事の生成完了: {output_path} に保存しました ===")
    
if __name__ == "__main__":
    main()
