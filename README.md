# Backtester

Backtester is a Python application for testing trading strategies against historical data. Backtester is heavily reliant on the [Backtrader](https://github.com/mementum/backtrader) framework

## Architecture

## Data

The data is OHLCV with the an example shown below:

| date       | open      | high      | low       | close     | volume | ticker |
|------------|-----------|-----------|-----------|-----------|--------|--------|
| 2000-01-21 | 554.73761 | 554.73761 | 508.50955 | 554.73761 | 26     | ZNT    |

Data was obtained from [Premium Data](https://www.premiumdata.net/products/premiumdata/asxhistorical.php) at a point in time. The data covers 2,628 stocks listed on the ASX between 1992-05-29 and 2018-05-04.

## Results

Multiple algorithmic trading strategies have been tested below.

A key challenge is determining which of the indicators for 2,628 stocks to consider, and the amount of capital that should be deployed when taking a position. In a simple OHLCV dataset there is likely insufficient information to be too creative. For example, to only consider the largest stocks in the index you would need historical market cap data.

### Assumptions

The following assumptions or decisions have been made:

1. The brokerage commission fee is 2.9%.
2. The relative sizing of any order is 2% of the available cash.

### Trend-Following Strategies

These are the most common algorithmic trading strategies which follow trends in moving averages, channel breakouts, price level movements, and related technical indicators.

An implementation of a 50-day and 200-day moving average cross-over strategy is available in [CrossoverStrategy](CrossoverStrategy.py). This strategy when run for all data (2,172 stocks with 456 discarded) returns a CAGR of -59.2%. This underperforms the XJO benchmark for this period by 64.25%.

### Arbitrage Opportunities

These strategies intend to profit from differences in prices for dual-listed stocks between exchanges, or between stocks and futures.

### Index Fund Rebalancing

These strategies aim to profit from index funds which are required to periodically rebalance their holdings according to their respective benchmark.

### Mathematical Model-based Strategies

These strategies use mathematical models such as the delta-neutral trading strategy. Delta neutral is a portfolio strategy consisting of multiple positions with offsetting positive and negative deltas. Delta is the ratio that compares the change in the price of an asset, to the corresponding change in the price of its derivative. 

### Mean Reversion

These strategies are based on the concept that the high and low prices of an asset are a temporary phenomenon that revert to their mean value periodically.

### Volume-weighted Average Price (VWAP)

This strategy breaks up a large order and releases dynamically determined smaller chunks of the order to the market using stock-specific historical volume profiles. The aim is to execute the order close to the volume-weighted average price (VWAP).

### Time Weighted Average Price (TWAP)

This strategy breaks up a large order and releases dynamically determined smaller chunks of the order to the market using evenly divided time slots between a start and end time. The aim is to execute the order close to the average price between the start and end times thereby minimising market impact.

### Percentage of Volume (POV)

This strategy executes the order quantity as a percentage of the trade volume of the stock. This is is typically used for large orders to minimise the impact to the market price.

### Implementation Shortfall

This strategy aims to minimise the execution cost of an order by trading off the real-time market. Slippage is the difference in price between the cost at the point of entry or exit from a trade and the actual price at the exchange.

### Advanced

Front-running strategies can be used by a sell-side market maker to profit from large orders on the buy side. Generally, the practice of front-running is considered illegal.

## Getting Started

### Pre-requisites

The following pre-requisites are required:

1. Python 3.9.7
1. [Anaconda](https://www.anaconda.com/products/individual)

### Installation

To install Backtester:

1. Create the virtual environment:
    ```bash
    conda env create -f environment.yml
    ```

2. Activate the virtual environment:
    ```bash
    conda activate backtester
    ```

To uninstall Backtester:

1. Remove the virtual environment:
    ```bash
    conda env remove -n backtester
    ```

To update the Backtester dependencies (FYI only):

1. Create the virtual environment:
    ```bash
    conda update --all
    ```

1. Create an updated environment.yml based on the current environment:
    ```bash
    conda env export > environment.yml
    ```
