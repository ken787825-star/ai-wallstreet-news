@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ==================================================
echo   AIウォール街通信 - 自動更新プロセス開始
echo   実行日時: %date% %time%
echo ==================================================
echo.

echo [1/2] 最新マーケットデータの取得とテクニカル分析を実行中...
python fetch_market_data.py
if %ERRORLEVEL% neq 0 (
    echo [エラー] データ取得に失敗しました。処理を中断します。
    pause
    exit /b 1
)
echo.

echo [2/2] AIアナリスト(Gemini)による記事を生成中...
python generate_articles.py
if %ERRORLEVEL% neq 0 (
    echo [エラー] 記事の生成に失敗しました。処理を中断します。
    pause
    exit /b 1
)
echo.

echo ==================================================
echo   生成プロセスがすべて正常に完了しました！
echo ==================================================

:: ----------------------------------------------------------------------
:: 【ステップ2用】GitHubとVercelの設定が終わったら以下の「::」を消して有効化します
:: ----------------------------------------------------------------------
:: echo [3/3] GitHubへ最新データをプッシュし、Vercelへ自動デプロイ中...
:: git add web-app/public/data/*
:: git commit -m "Auto-update market data and report: %date%"
:: git push origin main
:: echo 完了しました！

timeout /t 5
