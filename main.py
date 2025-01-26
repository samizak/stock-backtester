import os
import sqlite3
from fastapi import FastAPI, Query
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, "data", "stock_prices")
DB_PATH = os.path.join(DATA_FOLDER, "stock_prices.db")

def initialize_database():
    """Initialize database and create tables if they don't exist"""
    os.makedirs(DATA_FOLDER, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS stock_prices
                 (date TEXT PRIMARY KEY,
                  open REAL,
                  high REAL,
                  low REAL,
                  close REAL,
                  volume REAL,
                  dividend REAL,
                  split_ratio REAL,
                  ticker TEXT)''')
    conn.commit()
    conn.close()

def fetch_and_save_stock_data(ticker: str):
    """Fetch stock data from Yahoo Finance and save to SQLite database"""
    try:
        print(f"⏳ Fetching data for {ticker} from Yahoo Finance...")
        
        # Fetch data
        stock = yf.Ticker(ticker)
        df = stock.history(
            period="max",
            interval="1d",
            auto_adjust=True,
            actions=True
        ).reset_index()

        # Clean and format data
        df = df.rename(columns={
            'Open': 'open',
            'High': 'high', 
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume',
            'Dividends': 'dividend',
            'Stock Splits': 'split_ratio',
            'Date': 'date'
        })
        
        # Add ticker column and convert dates
        df['ticker'] = ticker
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

        # Save to database
        conn = sqlite3.connect(DB_PATH)
        df.to_sql('stock_prices', conn, if_exists='append', index=False)
        conn.close()
        
        print(f"✅ Successfully saved {len(df)} rows for {ticker}")
        return True

    except Exception as e:
        print(f"❌ Failed to fetch data for {ticker}: {str(e)}")
        return False

def get_db_data(ticker: str):
    """Retrieve data from SQLite database for specific ticker"""
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(
            "SELECT * FROM stock_prices WHERE ticker = ?",
            conn,
            params=(ticker,)
        )
        conn.close()
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        return df
    
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        return pd.DataFrame()
    
def check_ticker_exists(ticker: str) -> bool:
    """Check if data exists for a given ticker in the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM stock_prices WHERE ticker = ?",
            (ticker,)
        )
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        return False

@app.on_event("startup")
def startup_event():
    """Initialize database on startup"""
    initialize_database()


@app.get("/api/tickers")
async def get_all_tickers():
    """Get list of all unique tickers available in the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get distinct tickers from database
        cursor.execute("SELECT DISTINCT ticker FROM stock_prices ORDER BY ticker")
        tickers = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        tickers.append("Synthetic_Prices")

        return {"tickers": tickers}
    
    except sqlite3.Error as e:
        print(f"❌ Database error: {str(e)}")
        return {"error": "Failed to fetch tickers from database"}
    
    except Exception as e:
        print(f"⚠️ Unexpected error: {str(e)}")
        return {"error": "Unexpected error occurred"}
    



import numpy as np
import pandas as pd

def generate_gbm(start_price, mu, sigma, n_periods):
    dt = 1
    prices = np.zeros(n_periods)
    prices[0] = start_price
    for t in range(1, n_periods):
        drift = (mu - 0.5 * sigma ** 2) * dt
        shock = sigma * np.sqrt(dt) * np.random.normal()
        prices[t] = prices[t - 1] * np.exp(drift + shock)
    return prices

def generate_intra_prices(open_price, close_price, n_steps, sigma):
    if n_steps < 2:
        return [open_price, close_price]
    returns = np.random.normal(0, sigma / np.sqrt(n_steps), n_steps - 1)
    prices = [open_price]
    current_price = open_price
    for r in returns:
        current_price *= np.exp(r)
        prices.append(current_price)
    required_log_return = np.log(close_price / prices[-1])
    adjustment = required_log_return / (n_steps - 1)
    adjusted_returns = returns + adjustment
    prices = [open_price]
    current_price = open_price
    for r in adjusted_returns:
        current_price *= np.exp(r)
        prices.append(current_price)
    return prices

def generate_ohlc_data(
    start_price=100.0,
    mu=0.01,
    sigma=0.1,
    n_periods=252*10,
    n_intra_steps=100,
    start_date='2020-01-01'
):
    close_prices = generate_gbm(start_price, mu, sigma, n_periods)
    date_range = pd.date_range(start=start_date, periods=n_periods, freq='B')
    df = pd.DataFrame(index=date_range, columns=['Open', 'High', 'Low', 'Close'])
    df['Close'] = close_prices
    df['Open'] = df['Close'].shift(1)
    df.loc[df.index[0], 'Open'] = start_price

    for i in range(len(df)):
        open_p = df.iloc[i]['Open']
        close_p = df.iloc[i]['Close']
        intra_prices = generate_intra_prices(open_p, close_p, n_intra_steps, sigma)
        df.iloc[i, df.columns.get_loc('High')] = np.max(intra_prices)
        df.iloc[i, df.columns.get_loc('Low')] = np.min(intra_prices)

    # Convert index to date column and reset index
    df = df.reset_index().rename(columns={'index': 'date'})
    
    # Reorder columns to make date first
    df = df[['date', 'Open', 'High', 'Low', 'Close']]
    
    return df.astype({'Open': float, 'High': float, 'Low': float, 'Close': float})

@app.get("/api/prices")
async def get_prices(
    ticker: str = Query(...,  # Makes parameter required
                        description="Stock ticker symbol",
                        min_length=1)
):
    
    if ticker == "Synthetic_Prices":
        test = (generate_ohlc_data())
        # df = test.history(
        #     period="max",
        #     interval="1d",
        #     auto_adjust=True,
        #     actions=True
        # ).reset_index()


        print(test.head())

        # Clean and format data
        df = test.rename(columns={
            'Open': 'open',
            'High': 'high', 
            'Low': 'low',
            'Close': 'close',
            'Date': 'date'
        })
        
        # # Add ticker column and convert dates
        df['ticker'] = ticker
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

        # print(df)

        try:
            processed_df = df.copy()
            return {
                "ticker": ticker,
                "prices": processed_df.assign(
                    date=processed_df['date']#.dt.strftime('%Y-%m-%d')
                ).to_dict(orient='records'),
                "rsi": calculate_rsi(processed_df['close'].tolist()),
            }
            
        except Exception as e:
            print(f"⚠️ Processing error: {str(e)}")
            return {"error": f"Data processing failed: {str(e)}"}

    # Check if data exists for the ticker
    if not check_ticker_exists(ticker):
        print(f"⚠️ No data found for {ticker}, fetching from Yahoo Finance...")
        if not fetch_and_save_stock_data(ticker):
            return {"error": f"Failed to fetch data for {ticker}"}

    df = get_db_data(ticker)
    
    if df.empty:
        return {"error": f"No data available for {ticker}"}
    
    try:
        processed_df = df.copy()
        return {
            "ticker": ticker,
            "prices": processed_df.assign(
                date=processed_df['date'].dt.strftime('%Y-%m-%d')
            ).to_dict(orient='records'),
            "rsi": calculate_rsi(processed_df['close'].tolist()),
            "splits": processed_df[processed_df['split_ratio'] > 0]
                .assign(date=lambda x: x['date'].dt.strftime('%Y-%m-%d'))
                [['date', 'split_ratio']]
                .to_dict(orient='records')
        }
        
    except Exception as e:
        print(f"⚠️ Processing error: {str(e)}")
        return {"error": f"Data processing failed: {str(e)}"}

# Keep the calculate_rsi function the same
def calculate_rsi(closes: list[float], period: int = 14) -> list[float]:
    """Calculate Relative Strength Index"""
    deltas = pd.Series(closes).diff()
    gains = deltas.clip(lower=0)
    losses = -deltas.clip(upper=0)
    
    avg_gain = gains.rolling(period, min_periods=1).mean()
    avg_loss = losses.rolling(period, min_periods=1).mean()
    
    rs = avg_gain / avg_loss.replace(0, 0.0001)
    return (100 - (100 / (1 + rs))).fillna(50).tolist()