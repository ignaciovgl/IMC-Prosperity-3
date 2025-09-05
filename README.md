# IMC-Prosperity-3
This repository contains the Python code for our algorithmic trading solutions developed for the IMC Prosperity Challenge. The code implements various strategies for trading different virtual commodities in a simulated market environment, with the goal of maximizing our team's profit.

### 🎯 Project Goals

-Develop and implement diverse trading strategies tailored to the unique market behaviors of different commodities in the IMC Prosperity Challenge.
-Integrate statistical analysis methods, such as Z-scores for mean reversion, and linear regression for price prediction.
-Manage risk and position limits through careful order sizing and failsafe mechanisms.
-Employ different trading techniques, including market making, market taking, and conversion arbitrage.

---
### 🔍 Overview
Our trading solution is split across two main Python files, each handling a different set of products and strategies.
trategies.

KIR.py
This file handles the trading logic for RAINFOREST_RESIN, KELP, and SQUID_INK.

-KELP Strategy: A linear regression model is used to predict the future price of Kelp. The bot places buy and sell orders based on a spread around this predicted price. A failsafe mechanism is included to prevent large losses from sudden price drops.
-SQUID_INK Strategy: A Z-score mean-reversion strategy is employed. The bot calculates a Z-score based on the recent historical prices and places orders when the price deviates significantly from the mean, expecting it to revert back to its average.
-RAINFOREST_RESIN Strategy: A simple market making strategy is used, placing buy and sell orders around a stable price.

M.py
This file focuses on the MAGNIFICENT_MACARONS product.

-Z-score Mean-Reversion: Similar to the Squid Ink strategy, this bot tracks recent prices and uses a Z-score to identify overbought or oversold conditions, executing trades to profit from mean reversion.
-Conversion Arbitrage: The bot looks for arbitrage opportunities by comparing the market price of macarons to the cost of importing (askPrice + tariffs/fees) and the revenue from exporting (bidPrice - tariffs/fees). It executes trades to profit from mispricings between the internal conversion market and the public order book.

### 🛠️ Tech Stack
-Python (NumPy, Statistics)
-The datamodel library provided by the IMC Prosperity Challenge.
-Jupyter Notebook for Data Analysis and back testing strategies

--- 📊 Competition Results
Final Profit & Loss (PnL): 300,000+

Final Ranking: 4th in Spain

