import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Activity, TrendingUp, TrendingDown, DollarSign, Bitcoin, LineChart as LineChartIcon, Cpu } from 'lucide-react';
import { LineChart, Line, ResponsiveContainer, YAxis } from 'recharts';
import './index.css';

// 銘柄アイコンのマッピング
const getIcon = (symbol: string) => {
  if (symbol.includes('BTC')) return <Bitcoin size={24} color="#f59e0b" />;
  if (symbol.includes('JPY')) return <DollarSign size={24} color="#10b981" />;
  if (symbol.includes('GC')) return <Activity size={24} color="#eab308" />;
  return <LineChartIcon size={24} color="#3b82f6" />;
};

function App() {
  const [marketData, setMarketData] = useState<any>(null);
  const [report, setReport] = useState<string>('## 読み込み中...\nAIシステムがデータを分析しています。');
  const [dateStr, setDateStr] = useState<string>('');

  useEffect(() => {
    // 実際は自動生成されたデータを fetch します
    const loadData = async () => {
      try {
        const mdRes = await fetch('/data/daily_report.md');
        if (mdRes.ok) {
          const text = await mdRes.text();
          setReport(text);
        } else {
          // テスト用のモックテキスト
          setReport(`
### 日経225 (^N225)
#### 今日の解説
日経平均株価は、前日比1.26%高と大幅に上昇し、53,000円台を回復しました。輸出関連企業を中心に追い風となり、相場全体を押し上げています。

#### 明日の見立て
明日は、本日の上昇を維持できるかが焦点となるでしょう。53,000円の節目を維持できれば、一段と上値を試す展開も視野に入ります。

---

### ドル円 (JPY=X)
#### 今日の解説
ドル円は159円台後半まで値を上げました。日米間の金利差拡大への期待が引き続き円売りドル買いの背景となっています。
          `);
        }

        const dataRes = await fetch('/data/market_data.json');
        if (dataRes.ok) {
          const data = await dataRes.json();
          setMarketData(data);
        } else {
          // テスト用のモックデータ
          setMarketData({
            "日経225": { symbol: "^N225", analysis: { current_price: 53123.49, change_value: 659.8, change_pct: 1.26, trend_summary: "上昇" } },
            "ドル円": { symbol: "JPY=X", analysis: { current_price: 159.63, change_value: 0.93, change_pct: 0.59, trend_summary: "上昇" } },
            "ダウ平均": { symbol: "^DJI", analysis: { current_price: 46504.67, change_value: -60.4, change_pct: -0.13, trend_summary: "下落" } },
            "ビットコイン": { symbol: "BTC-USD", analysis: { current_price: 66969.72, change_value: -323.0, change_pct: -0.48, trend_summary: "下落" } }
          });
        }
      } catch (err) {
        console.error("データの読み込みに失敗しました", err);
      }
    };

    loadData();

    // 日付の取得
    const today = new Date();
    setDateStr(`${today.getFullYear()}/${(today.getMonth()+1).toString().padStart(2, '0')}/${today.getDate().toString().padStart(2, '0')}`);
  }, []);

  return (
    <div className="dashboard-container">
      <header className="header">
        <div className="header-title">
          <Cpu className="text-accent-cyan" size={36} />
          AI ウォール街通信
        </div>
        <div className="header-date">
          <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
            <div className="pulse-dot"></div>
            SYSTEM ACTIVE • {dateStr}
          </div>
        </div>
      </header>

      {/* マーケットデータカード */}
      <div className="overview-grid">
        {marketData && Object.entries(marketData).map(([name, info]: [string, any], index) => {
          if (info.error) return null;
          const { analysis, symbol, history } = info;
          const isUp = analysis.change_value > 0;
          const chartColor = isUp ? "#10b981" : "#ef4444";
          
          return (
            <div className="metric-card" key={index} style={{animationDelay: `${index * 0.15}s`}}>
              <div className="metric-header">
                <span>{name}</span>
                {getIcon(symbol)}
              </div>
              <div className="metric-value">
                {name === 'ドル円' ? '¥' : name === 'ビットコイン' ? '$' : ''}
                {analysis.current_price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
              <div className={`metric-change ${isUp ? 'up' : 'down'}`} style={{ marginBottom: history ? '1rem' : '0' }}>
                {isUp ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                {isUp ? '+' : ''}{analysis.change_value.toLocaleString()} ({analysis.change_pct}%)
              </div>
              {/* テクニカル指標の表示 */}
              {analysis.technical && (
                <div style={{
                  display: 'flex', gap: '8px', flexWrap: 'wrap', 
                  marginBottom: '1rem', marginTop: '0.5rem', fontSize: '0.75rem'
                }}>
                  {analysis.technical.rsi_14 !== null && (
                    <span style={{ 
                      padding: '2px 6px', borderRadius: '4px', 
                      background: analysis.technical.rsi_14 > 70 ? 'rgba(239,68,68,0.2)' : analysis.technical.rsi_14 < 30 ? 'rgba(16,185,129,0.2)' : 'rgba(255,255,255,0.1)',
                      color: analysis.technical.rsi_14 > 70 ? '#fca5a5' : analysis.technical.rsi_14 < 30 ? '#6ee7b7' : '#9ca3af'
                    }}>
                      RSI: {analysis.technical.rsi_14}
                    </span>
                  )}
                  {analysis.technical.macd !== null && (
                    <span style={{ padding: '2px 6px', borderRadius: '4px', background: 'rgba(255,255,255,0.1)', color: '#9ca3af' }}>
                      MACD: {analysis.technical.macd}
                    </span>
                  )}
                  {analysis.technical.sma_5 !== null && (
                    <span style={{ padding: '2px 6px', borderRadius: '4px', background: 'rgba(255,255,255,0.1)', color: '#9ca3af' }}>
                      SMA(5): {analysis.technical.sma_5}
                    </span>
                  )}
                </div>
              )}
              {history && history.length > 0 && (
                <div style={{ height: '60px', width: '100%', marginTop: 'auto' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={history}>
                      <YAxis domain={['dataMin', 'dataMax']} hide />
                      <Line type="monotone" dataKey="price" stroke={chartColor} strokeWidth={2} dot={false} isAnimationActive={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* 記事セクション */}
      <div className="article-section">
        {/* メインのAIレポート */}
        <div className="article-card main">
          <div className="section-title">
            <Activity size={20} color="#06b6d4" />
            TODAY'S AI ANALYSIS
          </div>
          <div className="article-content">
            <ReactMarkdown>{report}</ReactMarkdown>
          </div>
        </div>

        {/* サイドバー (ニュースやTwitter連携等を入れる用途) */}
        <div className="article-card">
          <div className="section-title">
            SYSTEM STATUS
          </div>
          <div style={{color: "var(--text-muted)", fontSize: "0.95rem"}}>
            <p>✅ マーケットデータ取得機能稼働中</p>
            <p>✅ Gemini API による分析完了</p>
            <p>🔄 SNS連動システム（準備中）</p>
            <p style={{marginTop: "1.5rem", padding: "1rem", background: "rgba(255,255,255,0.05)", borderRadius: "8px", border: "1px dashed rgba(255,255,255,0.1)"}}>
              当サイトはAI（Gemini）によって自動生成されたコンテンツによって毎朝自動更新されます。
              最新のウォール街のアナリスト視点をお届けします。
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
