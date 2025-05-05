import numpy as np
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
import yfinance as yf
import datetime
from filterpy.kalman import KalmanFilter

# Enable yfinance override for pandas_datareader
yf.pdr_override()

# Set date range
start_date = datetime.datetime(2023, 1, 1)
end_date = datetime.datetime(2024, 1, 1)

data = yf.download('F', start=start_date, end=end_date)
prices = data['Close'].dropna().values

# Check
if len(prices) == 0:
    raise ValueError("No data was downloaded. Check ticker or date range.")

# Kalman Filter Setup
kf = KalmanFilter(dim_x=2, dim_z=1)
kf.x = np.array([prices[0], 0])  # initial price and trend
kf.F = np.array([[1, 1],
                 [0, 1]])         # constant velocity model
kf.H = np.array([[1, 0]])
kf.P *= 10
kf.R = 4
kf.Q = np.array([[0.001, 0.01],
                 [0.01, 0.1]])

# Storage for estimates
filtered_prices = []

for z in prices:
    kf.predict()
    kf.update([z])
    filtered_prices.append(kf.x[0])

# 5-step ahead Forecast
future_steps = 5
future_predictions = []
x_future = kf.x.copy()

for _ in range(future_steps):
    x_future = kf.F @ x_future
    future_predictions.append(x_future[0])

# Plot
plt.figure(figsize=(12,6))
plt.plot(prices, label='Observed Price', alpha=0.5)
plt.plot(filtered_prices, label='Kalman Filter Estimate', linewidth=2)
plt.plot(range(len(prices), len(prices) + future_steps), future_predictions, 'r--', label='5-Day Forecast')
plt.legend()
plt.xlabel('Time (days)')
plt.ylabel('Price (USD)')
plt.title('Kalman Filter Applied to AAPL Stock with 5-Day Forecast')
plt.grid()
plt.show()