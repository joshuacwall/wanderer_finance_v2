# 🏃 Wanderer Finance v2

An experimental AI-powered intraday stock analysis platform that uses Large Language Models to identify potentially valuable stocks for day trading.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Gradio](https://img.shields.io/badge/Interface-Gradio-orange.svg)](https://gradio.app/)

## ⚠️ Important Disclaimer

**Wanderer AI is a highly experimental project. Trading stocks involves significant risk, and you could lose money. Never invest money you cannot afford to lose. We are not certified financial advisors. The insights provided by Wanderer AI are for educational and entertainment purposes only. Use at your own risk.**

## 🎯 What is Wanderer Finance?

Wanderer Finance is an experimental platform that combines real-time financial data with AI analysis to identify stocks suitable for intraday trading. The system follows a "buy at open, sell before close" strategy, never holding positions overnight.

### Key Features

- **🤖 AI-Powered Analysis**: Uses DeepSeek-r1-distill-llama-70b LLM for stock analysis
- **📊 Multi-Source Data**: Integrates Yahoo Finance, Alpha Vantage, and News Data APIs
- **📈 Real-Time Tracking**: Live price updates and performance monitoring
- **🎯 Performance Evaluation**: Compares recommendations against S&P 500 benchmark
- **🖥️ Web Interface**: Clean Gradio-based UI for easy interaction
- **📱 Responsive Design**: Works on desktop and mobile devices

## 🏗️ Architecture

```
wanderer_finance_v2/
├── src/                    # Core application code
│   ├── agents/            # LLM agents and workflows
│   ├── clients/           # External API clients
│   ├── config/            # Configuration management
│   ├── llm/               # LLM integration
│   ├── utils/             # Utility functions
│   └── workflows/         # Analysis workflows
├── app/                   # Gradio UI components
├── logs/                  # Application logs
├── main.db               # SQLite database
├── identify.py           # Stock identification script
├── evaluate.py           # Performance evaluation script
└── app.py               # Main Gradio application
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- API keys for:
  - Alpha Vantage (for stock data and insider trading)
  - News Data API (for news sentiment analysis)
  - Groq (for LLM access)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/joshuacwall/wanderer_finance_v2.git
   cd wanderer_finance_v2
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Initialize the database**
   ```bash
   python db_management.py
   ```

5. **Run stock analysis** (during market hours)
   ```bash
   python identify.py
   ```

6. **Launch the web interface**
   ```bash
   python app.py
   ```

## 📋 Usage

### Daily Workflow

1. **Morning Analysis**: Run `identify.py` during market hours to analyze active stocks
2. **View Recommendations**: Use the web interface to see current picks
3. **Evening Evaluation**: Run `evaluate.py` after market close to assess performance

### Web Interface Tabs

- **Welcome**: Overview and latest updates
- **Current Picks**: View AI recommendations with real-time prices
- **Current Passes**: Stocks the AI decided to pass on
- **Evaluation**: Performance tracking and analytics

## 🔧 Configuration

The application uses a centralized configuration system in `src/config/settings.py`:

```python
# Example configuration
config.llm.model = "groq/deepseek-r1-distill-llama-70b"
config.llm.temperature = 0.1
config.trading.max_articles_per_stock = 2
config.database.path = "main.db"
```

## 📊 How It Works

1. **Data Collection**: Gathers data from multiple sources including stock metrics, news articles, and insider trading information

2. **Sentiment Analysis**: Uses LLM to analyze news sentiment for each stock

3. **AI Analysis**: Processes all data through a financial analysis LLM agent to generate recommendations

4. **Performance Tracking**: Compares actual stock performance against S&P 500 benchmark

5. **Evaluation Metrics**:
   - **WIN**: BUY performs better than S&P 500, or HOLD performs worse than S&P 500
   - **LOSS**: BUY performs worse than S&P 500, or HOLD performs better than S&P 500

## 🛠️ Development

### Code Quality

The codebase follows modern Python best practices:

- **Type Hints**: Comprehensive type annotations throughout
- **Logging**: Structured logging with configurable levels
- **Error Handling**: Robust exception handling and recovery
- **Configuration**: Centralized configuration management
- **Documentation**: Comprehensive docstrings and comments

### Testing

```bash
# Run tests (when available)
python -m pytest tests/

# Run linting
flake8 src/ app/
black src/ app/
mypy src/ app/
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📈 Performance Metrics

The system tracks several key metrics:

- **Win Rate**: Percentage of successful recommendations
- **Average Return**: Mean performance vs S&P 500
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Largest peak-to-trough decline

## 🔍 API Reference

### Core Classes

- `SQLiteClient`: Database operations with connection pooling
- `AlphaVantageClient`: Stock data and insider trading information
- `NewsDataClient`: News article retrieval and processing
- `AnalysisResult`: Structured LLM analysis output

### Configuration

All configuration is managed through `src/config/settings.py`:

```python
from src.config import config

# Access configuration
model = config.llm.model
db_path = config.database.absolute_path
```

## 🚨 Known Limitations

- **Market Hours Only**: Analysis only runs during US market hours
- **Experimental**: This is research software, not production-ready
- **API Dependencies**: Requires multiple external API services
- **No Backtesting**: Historical performance testing not implemented
- **Limited Assets**: Currently only supports US stocks

## 📝 Changelog

### v2.0.0 (Current)
- ✅ Improved code structure and maintainability
- ✅ Added comprehensive logging and error handling
- ✅ Centralized configuration management
- ✅ Enhanced type safety with type hints
- ✅ Better separation of concerns
- ✅ Improved documentation

### v1.0.0
- Initial release with basic functionality

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/joshuacwall/wanderer_finance_v2/issues)
- **Discussions**: [GitHub Discussions](https://github.com/joshuacwall/wanderer_finance_v2/discussions)

## 🙏 Acknowledgments

- **LangChain**: For LLM orchestration framework
- **Gradio**: For the web interface framework
- **Yahoo Finance**: For real-time stock data
- **Alpha Vantage**: For comprehensive financial data
- **Groq**: For fast LLM inference

---

**Remember**: This is experimental software for educational purposes. Never risk money you cannot afford to lose, and always do your own research before making investment decisions.
