import gradio as gr

def create_tab():
    with gr.TabItem("Welcome"):
        greeting_text = gr.Markdown("## Welcome to Wanderer!")  # Use Markdown for a heading
        with gr.Row():
            with gr.Column(scale=2):
                wanderer_text = gr.Markdown(
                    greeting,
                    label="What is Wanderer?"
                )
            with gr.Column(scale=1):
                updates_text = gr.Markdown(
                    updates,
                    label="Latest Updates"
                )
updates ="""
## Latest Updates

* **2025-03-02:** Database Migration/Evaluation Script
* **2025-02-23:** Set-up Identify triggers in github
* **2025-02-23:** Improve DB management
* **2025-02-16:** Langsmith tracing set up and templates moved
* **2025-02-09:** Gradio UI
* **2025-02-07:** Store data in sqllite 
* **2025-02-02:** Initial re-design in notebooks

We're constantly working to improve Wanderer!
"""

greeting = """
## What is Wanderer?

Wanderer is a platform designed to identify potentially valuable stocks for intraday trading.  We believe in providing data-driven insights to help traders make informed decisions.

**IMPORTANT WARNING:** Wanderer AI is a highly experimental project.  Trading stocks involves significant risk, and you could lose money.  **Never invest money you cannot afford to lose.**  We are not certified financial advisors.  The insights provided by Wanderer AI are for educational and entertainment purposes only.  **Use at your own risk.**

Wanderer AI is an experimental process focused on identifying stocks suitable for a "buy at open, sell before close" strategy.  We aim to identify opportunities for short-term gains, never holding positions overnight.

Here's how it works:

1. **Data Collection:** We gather real-time data from multiple sources, including Yahoo Finance, Advantage API, and News Data API. This comprehensive dataset provides a rich foundation for our analysis.

2. **LLM Analysis:** This data is then processed by a powerful Large Language Model (LLM), currently DeepSeek-r1-distill-llama-70b, hosted by Groq.  The LLM analyzes the data to identify potential trading opportunities.

3. **Stock Selection:**  Based on the LLM's analysis, Wanderer identifies a selection of stocks that may be suitable for intraday trading.

4. **How to use:**  Simple. If the LLM Action is "Buy", the purchase the stock. If the LLM Action is "HOLD", then don't take any action.
    * Suggestion:  Set as daily limit (lets say $50), distribute that amount evenly amongst stocks LLM suggests to "BUY". Sell before close.

5. **Definition of "WIN":**  A "WIN" is considered any time a BUY performs better than the S&P500 or a HOLD performs worse than the S&P500

* **Key Principles:**
    * Intraday Focus:  All positions are closed before the end of the trading day.
    * Data-Driven:  Our analysis relies on real-time market data and advanced LLM processing.
    * Experimental:  Wanderer AI is an ongoing experiment, and its performance is subject to change.  Use with caution and at your own risk.

**Disclaimer:**  Wanderer AI is a project developed by enthusiasts exploring the use of LLMs in financial analysis.  We make no guarantees about the accuracy or effectiveness of our stock selections.  Past performance is not indicative of future results.  Consult with a qualified financial advisor before making any investment decisions.
"""