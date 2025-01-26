import numpy as np
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
from numba import njit, prange

# --------------------------
# Data Generation Functions 
# --------------------------
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

# ---------------------
# Main Visualization
# ---------------------
fig = plt.figure(figsize=(14, 8))
ax_ohlc = plt.axes([0.1, 0.35, 0.8, 0.6])  # Main chart area
ax_mu = plt.axes([0.1, 0.25, 0.35, 0.03])  # Mu slider
ax_sigma = plt.axes([0.1, 0.20, 0.35, 0.03])  # Sigma slider
ax_steps = plt.axes([0.1, 0.15, 0.35, 0.03])  # Intra steps slider
ax_generate = plt.axes([0.1, 0.05, 0.15, 0.075])  # Generate button
ax_log = plt.axes([0.3, 0.05, 0.15, 0.075])  # Log scale button

# Create controls
mu_slider = Slider(ax_mu, 'Drift (μ)', 0.0, 0.1, valinit=0.01, valfmt='%1.3f')
sigma_slider = Slider(ax_sigma, 'Volatility (σ)', 0.05, 0.5, valinit=0.1, valfmt='%1.2f')
steps_slider = Slider(ax_steps, 'Intra Steps', 10, 200, valinit=100, valfmt='%d')
button_generate = Button(ax_generate, 'Generate New Data')
button_log = Button(ax_log, 'Log Scale')

# Style configuration
style = mpf.make_mpf_style(
    base_mpf_style='yahoo',
    marketcolors=mpf.make_marketcolors(up='g', down='r')
)

# Global state
current_df = None
current_scale = 'linear'
params = {
    'n_periods': 252*1,
    'start_price': 100.0,
    'mu': mu_slider.val,
    'sigma': sigma_slider.val,
    'n_intra_steps': int(steps_slider.val)
}

def generate_new_ohlc():
    """Generate fresh OHLC data using current parameters"""
    close_prices = generate_gbm(params['start_price'], params['mu'], 
                               params['sigma'], params['n_periods'])
    date_range = pd.date_range(end='2025-01-01', 
                              periods=params['n_periods'], 
                              freq='B')
    df = pd.DataFrame(index=date_range, 
                     columns=['Open', 'High', 'Low', 'Close'])
    df['Close'] = close_prices
    df['Open'] = df['Close'].shift(1)
    df.loc[df.index[0], 'Open'] = params['start_price']

    for i in range(len(df)):
        open_p = df.iloc[i]['Open']
        close_p = df.iloc[i]['Close']
        intra_prices = generate_intra_prices(open_p, close_p, 
                                            params['n_intra_steps'], 
                                            params['sigma'])
        df.iloc[i, df.columns.get_loc('High')] = np.max(intra_prices)
        df.iloc[i, df.columns.get_loc('Low')] = np.min(intra_prices)
    

    # monthly_df = df.resample('M').agg({
    #     'Open': 'first',
    #     'High': 'max',
    #     'Low': 'min',
    #     'Close': 'last'
    # }).dropna()
    
    # return monthly_df.astype(float)

    return df.astype(float)

def redraw_plot():
    """Redraw the chart with current data and settings"""
    ax_ohlc.clear()
    mpf.plot(current_df, type='candle', mav=(20), ax=ax_ohlc, style=style, ylabel='Price')
    ax_ohlc.set_title('Synthetic OHLC Data', fontsize=14, pad=20)
    ax_ohlc.set_yscale(current_scale)
    plt.draw()

def update_params(val):
    """Update parameters from sliders"""
    params['mu'] = mu_slider.val
    params['sigma'] = sigma_slider.val
    params['n_intra_steps'] = int(steps_slider.val)  # Convert to integer
    generate_new_data(None)

def generate_new_data(event):
    """Generate new data and redraw"""
    global current_df
    current_df = generate_new_ohlc()
    redraw_plot()

def toggle_scale(event):
    """Toggle between log and linear scale"""
    global current_scale
    current_scale = 'log' if current_scale == 'linear' else 'linear'
    button_log.label.set_text(f'{current_scale.title()} Scale')
    redraw_plot()

# Connect controls
mu_slider.on_changed(update_params)
sigma_slider.on_changed(update_params)
steps_slider.on_changed(update_params)
button_generate.on_clicked(generate_new_data)
button_log.on_clicked(toggle_scale)

# Initial generation and plot
current_df = generate_new_ohlc()
redraw_plot()
plt.show()