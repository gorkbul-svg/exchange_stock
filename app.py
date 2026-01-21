
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)

# Store analysis results
analysis_cache = {}

@app.route('/', methods=['GET'])
def index():
    """Serve the main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/analysis', methods=['POST'])
def analyze_stock():
    """Analyze stock with mock data"""
    try:
        data = request.json
        ticker = data.get('ticker', 'UNKNOWN').upper()
        
        # Generate mock analysis data
        analysis = generate_mock_analysis(ticker)
        
        # Store in cache
        analysis_cache[ticker] = {
            'data': analysis,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(analysis), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/analyses', methods=['GET'])
def list_analyses():
    """List all saved analyses"""
    analyses = []
    for ticker, data in analysis_cache.items():
        analyses.append({
            'ticker': ticker,
            'timestamp': data['timestamp'],
            'recommendation': data['data'].get('recommendation', 'N/A'),
            'confidence': data['data'].get('confidence_percent', 0)
        })
    return jsonify({'analyses': analyses, 'total': len(analyses)}), 200

@app.route('/api/export/<ticker>', methods=['GET'])
def export_analysis(ticker):
    """Export analysis as JSON"""
    if ticker.upper() in analysis_cache:
        data = analysis_cache[ticker.upper()]['data']
        return jsonify(data), 200
    return jsonify({'status': 'error', 'message': 'Analysis not found'}), 404

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'cached_analyses': len(analysis_cache),
        'version': '1.0.0'
    }), 200

def generate_mock_analysis(ticker):
    """Generate mock stock analysis data"""
    current_price = round(random.uniform(10, 100), 2)
    price_change = round(random.uniform(-5, 5), 2)
    price_change_pct = round((price_change / current_price) * 100, 2)
    
    rsi = round(random.uniform(20, 80), 2)
    macd = round(random.uniform(-2, 2), 4)
    macd_signal = round(random.uniform(-2, 2), 4)
    sma = round(random.uniform(current_price - 5, current_price + 5), 2)
    ema = round(random.uniform(current_price - 5, current_price + 5), 2)
    
    support = round(current_price - random.uniform(2, 5), 2)
    resistance = round(current_price + random.uniform(2, 5), 2)
    
    signals = []
    signal_scores = []
    
    if rsi > 70:
        signals.append(f"RSI Overbought ({rsi:.2f} > 70) - SELL Signal")
        signal_scores.append(-1)
    elif rsi < 30:
        signals.append(f"RSI Oversold ({rsi:.2f} < 30) - BUY Signal")
        signal_scores.append(1)
    else:
        signals.append(f"RSI Neutral ({rsi:.2f})")
        signal_scores.append(0)
    
    if macd > macd_signal:
        signals.append("MACD above Signal - BUY Signal")
        signal_scores.append(1)
    else:
        signals.append("MACD below Signal - SELL Signal")
        signal_scores.append(-1)
    
    if current_price > sma:
        signals.append(f"Price above SMA ({current_price:.2f} > {sma:.2f}) - BUY Signal")
        signal_scores.append(1)
    else:
        signals.append(f"Price below SMA ({current_price:.2f} < {sma:.2f}) - SELL Signal")
        signal_scores.append(-1)
    
    if current_price > ema:
        signals.append(f"Price above EMA ({current_price:.2f} > {ema:.2f}) - BUY Signal")
        signal_scores.append(1)
    else:
        signals.append(f"Price below EMA ({current_price:.2f} < {ema:.2f}) - SELL Signal")
        signal_scores.append(-1)
    
    avg_score = sum(signal_scores) / len(signal_scores) if signal_scores else 0
    confidence = abs(avg_score) * 100
    
    if avg_score > 0.3:
        recommendation = "BUY"
    elif avg_score < -0.3:
        recommendation = "SELL"
    else:
        recommendation = "HOLD"
    
    volatility = round(((resistance - support) / current_price) * 100, 2)
    risk_level = "HIGH" if volatility > 5 else "MEDIUM" if volatility > 2 else "LOW"
    
    return {
        "stock_ticker": ticker,
        "current_price": current_price,
        "price_change": price_change,
        "price_change_percent": price_change_pct,
        "intraday_high": round(current_price + random.uniform(1, 3), 2),
        "intraday_low": round(current_price - random.uniform(1, 3), 2),
        "volume": random.randint(1000000, 10000000),
        "volatility_percent": volatility,
        "technical_indicators": {
            "rsi": rsi,
            "macd": macd,
            "macd_signal": macd_signal,
            "sma": sma,
            "ema": ema
        },
        "support_level": support,
        "resistance_level": resistance,
        "mid_level": round((support + resistance) / 2, 2),
        "recommendation": recommendation,
        "confidence_percent": confidence,
        "risk_level": risk_level,
        "trading_signals": signals,
        "analysis_timestamp": datetime.now().isoformat(),
        "disclaimer": "This analysis is for informational purposes only."
    }

@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
