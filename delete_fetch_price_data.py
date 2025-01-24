import yfinance as yf
import pandas as pd
import os

# Configure parameters
ticker_symbol = "AAPL"
start_date = "1970-01-01"  # Apple's IPO was in 1980, but this ensures full history
output_folder = "stock_prices"
output_filename = "AAPL_full_history_adjusted.csv"

try:
    # Create output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Fetch data with auto-adjustment for splits and dividends
    stock = yf.Ticker(ticker_symbol)
    
    # Get full history (auto_adjust=True handles splits/dividends)
    df = stock.history(
        period="max",
        interval="1d",
        start=start_date,
        auto_adjust=False,  # Automatically adjusts prices for splits and dividends
        actions=True       # Includes dividend/split events in the DataFrame
    )
    
    # Rename columns for clarity
    df = df.rename(columns={
        'Open': 'open',
        'High': 'high', 
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume',
        'Dividends': 'dividend',
        'Stock Splits': 'split_ratio'
    })

    output_path = os.path.join("data", output_folder, output_filename)

    # Save to CSV
    df.to_csv(output_path, index=True)
    print(f"Successfully saved {len(df)} rows to {output_path}")
    
except Exception as e:
    print(f"Error fetching data: {str(e)}")