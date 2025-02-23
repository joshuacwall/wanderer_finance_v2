from src.utils.market_status import is_us_market_open
from dotenv import load_dotenv
from src.clients.sqllite import SQLiteClient
from src.workflows.analze_active_stocks import analyze_active_stocks

load_dotenv() 

MODEL = "groq/deepseek-r1-distill-llama-70b"
TEMPERATURE = 0.1
DATABASE="analysis_results.db"
TABLE="raw_data"

if __name__ == "__main__":
    if is_us_market_open():
        results_df = analyze_active_stocks()

        if not results_df.empty:
            client = SQLiteClient(DATABASE)
            client.append_df(results_df, TABLE)

            print("\nAnalysis Summary:")
            print(f"Total stocks analyzed: {len(results_df)}")
            print("\nAction Distribution:")
            print(results_df['action'].value_counts())

    else:
        print("Markets are closed today")


