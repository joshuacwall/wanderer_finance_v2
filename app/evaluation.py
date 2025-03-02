from src.clients.sqllite import SQLiteClient
import gradio as gr
import pandas as pd
import plotly.express as px
import yfinance as yf
from datetime import datetime, timedelta

# Example query - replace with your actual query
quadrant_query = """
SELECT
    ticker,
    evaluation,
    percent_change,
    current_date as date,
    count(ticker) as value
FROM
    data
WHERE
    (evaluation is not NULL OR percent_change is not NULL)
GROUP BY
    ticker;
"""

client = SQLiteClient("main.db")

def get_sp500_return(start_date, end_date):
    """
    Get S&P 500 return between two dates by only fetching those specific dates.
    Includes retry logic for market closed days, looking backwards.
    """
    try:
        # Convert strings to datetime objects
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        # Download start date (try up to 5 business days before)
        for i in range(5):
            start_check = start - timedelta(days=i)
            start_data = yf.download(
                "^GSPC",
                start=start_check.strftime('%Y-%m-%d'),
                end=(start_check + timedelta(days=1)).strftime('%Y-%m-%d'),
                progress=False,
                auto_adjust=True
            )
            if not start_data.empty:
                start_price = float(start_data['Close'].iloc[0])
                break
        else:
            return "No start date data available"

        # Download end date (try up to 5 business days before)
        for i in range(5):
            end_check = end - timedelta(days=i)
            end_data = yf.download(
                "^GSPC",
                start=end_check.strftime('%Y-%m-%d'),
                end=(end_check + timedelta(days=1)).strftime('%Y-%m-%d'),
                progress=False,
                auto_adjust=True
            )
            if not end_data.empty:
                end_price = float(end_data['Close'].iloc[0])
                break
        else:
            return "No end date data available"

        # Calculate return
        sp500_change = ((end_price - start_price) / start_price) * 100
        return f"{sp500_change:.2f}%"

    except Exception as e:
        print(f"S&P 500 Error details: {e}")
        return "Error fetching S&P 500 data"

def create_tab():
    with gr.TabItem("Evaluation"):
        with gr.Row():
            refresh_button = gr.Button("Refresh Data")
        with gr.Row():
            output_table = gr.DataFrame()
            plot_output = gr.Plot()
        with gr.Row():
            percent_change_display = gr.Textbox(label="Wanderer AI Return")
            sp500_change_display = gr.Textbox(label="S&P 500 Return")

        def refresh_data():
            try:
                results = client.query(quadrant_query)
                df = pd.DataFrame(results) if isinstance(results, list) else results
                
                # Calculate total percent change
                total_percent_change = df['percent_change'].astype(float).sum()
                
                # Create pie chart
                fig = px.pie(df, values='value', names='evaluation', title='Distribution by evaluation')
                
                # Prepare table data
                table_df = df.drop('value', axis=1)

                # Get date range
                dates = pd.to_datetime(df['date'])
                min_date = dates.min().strftime('%Y-%m-%d')
                max_date = dates.max().strftime('%Y-%m-%d')
                
                # Update plot title
                fig.update_layout(title_text=f'Distribution by evaluation ({min_date} to {max_date})')
                
                # Get S&P 500 return using optimized function
                sp500_change_str = get_sp500_return(min_date, max_date)
                
                return (
                    table_df,
                    fig,
                    f"{total_percent_change:.2f}%",
                    sp500_change_str
                )
                
            except Exception as e:
                print(f"Error: {e}")
                return pd.DataFrame({"Error": [str(e)]}), None, "Error", "Error"

        # Initialize the display
        initial_df, initial_plot, initial_percent_change, initial_sp500_change = refresh_data()
        output_table.value = initial_df
        plot_output.value = initial_plot
        percent_change_display.value = initial_percent_change
        sp500_change_display.value = initial_sp500_change

        # Set up refresh button callback
        refresh_button.click(
            fn=refresh_data,
            outputs=[output_table, plot_output, percent_change_display, sp500_change_display]
        )