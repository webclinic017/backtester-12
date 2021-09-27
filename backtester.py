import os
import warnings
import time
import numpy as np
import pandas as pd
import seaborn as sns
import backtrader as bt
import configparser
import quantstats as qs

from TickerData import TickerData
from CrossoverStrategy import CrossoverStrategy
from Benchmark import Benchmark
from FixedCommissionScheme import FixedCommissionScheme


class Backtester:
    """
    TBC

    Attributes
    ----------
    leagueID : sequence
        The unique identifier for the league.

    Methods
    -------
    parse_input()
        Parse the user input.
    """

    @staticmethod
    def format_time(t):
        """Format the time in hh:mm:ss.

        Parameters
        ----------
        t : float
            A length of time in seconds.

        Raises
        ------

        """
        m_, s = divmod(t, 60)
        h, m = divmod(m_, 60)
        return f'{h:>02.0f}:{m:>02.0f}:{s:>02.0f}'

    @staticmethod
    def global_settings():
        """Format the time in hh:mm:ss.

        Parameters
        ----------

        Raises
        ------

        """
        warnings.filterwarnings('ignore')
        pd.set_option('display.expand_frame_repr', False)
        np.random.seed(42)
        sns.set_style('darkgrid')

    def add_benchmark_data(self):
        """Format the time in hh:mm:ss.

        Parameters
        ----------

        Raises
        ------

        """
        print("Adding ticker: " + 'XJO')
        self.cerebro_benchmark.adddata(
            TickerData(dataname=self.benchmark_data.loc[self.benchmark_data['ticker'] == 'XJO']), name='XJO')

    def add_strategy_data(self):
        """Format the time in hh:mm:ss.

        Parameters
        ----------

        Raises
        ------

        """
        tickers = self.tickers.split(',')
        # tickers = self.tickers
        index = 0
        for i, ticker in enumerate(tickers):
            ticker_data = self.data.loc[self.data['ticker'] == ticker]  # .sort_values(by='date')
            if ticker_data['date'].size > 200:
                print("Adding ticker: " + ticker)
                self.cerebro.adddata(TickerData(dataname=ticker_data), name=ticker)
                # self.cerebro.datas[index].plotinfo.plot = False
                index = index + 1
            else:
                print("Ignoring ticker: " + ticker)


    def run_strategy_reports(self):
        self.returns.index = self.returns.index.tz_convert(None)
        qs.reports.html(self.returns, output='strategy-stats-' + time.strftime("%Y%d%m-%H%M%S") + '.html',
                        title='Strategy Performance')

    def run_benchmark_reports(self):
        self.benchmark_returns.index = self.benchmark_returns.index.tz_convert(None)
        qs.reports.html(self.benchmark_returns, output='benchmark-stats-' + time.strftime("%Y%d%m-%H%M%S") + '.html',
                        title='Benchmark Performance')

    def run_benchmark(self):
        """Format the time in hh:mm:ss.

        Parameters
        ----------

        Raises
        ------

        """
        self.cerebro_benchmark.broker.addcommissioninfo(self.benchmark_comminfo)
        self.cerebro_benchmark.broker.setcash(self.cash)
        self.add_benchmark_data()
        self.cerebro_benchmark.addobservermulti(bt.observers.BuySell, barplot=True, bardist=0.0025)
        self.cerebro_benchmark.addobserver(bt.observers.Broker)
        self.cerebro_benchmark.addobserver(bt.observers.Trades)
        self.cerebro_benchmark.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
        self.cerebro_benchmark.addstrategy(Benchmark, verbose=True, log_file='benchmark_log.csv')
        # self.cerebro_benchmark.addsizer(bt.sizers.PercentSizer, percents=100)
        results = self.cerebro_benchmark.run()  # runonce=False
        if self.config['options']['plot'] == 'true':
            self.cerebro_benchmark.plot(volume=False)
        return results

    def run_strategy(self):
        """Format the time in hh:mm:ss.

        Parameters
        ----------

        Raises
        ------

        """
        self.cerebro.broker.addcommissioninfo(self.comminfo)
        self.cerebro.broker.setcash(self.cash)
        self.add_strategy_data()
        self.cerebro.addobservermulti(bt.observers.BuySell, barplot=True, bardist=0.0025)
        self.cerebro.addobserver(bt.observers.Broker)
        self.cerebro.addobserver(bt.observers.Trades)
        self.cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
        self.cerebro.addstrategy(CrossoverStrategy, verbose=True, log_file='strategy_log.csv')
        self.cerebro.addsizer(bt.sizers.PercentSizer, percents=2)
        results = self.cerebro.run()  # runonce=False
        if self.config['options']['plot'] == 'true':
            self.cerebro.plot(volume=False)
        return results

    @staticmethod
    def prepare_log():
        """Format the time in hh:mm:ss.

        Parameters
        ----------

        Raises
        ------

        """
        try:
            os.remove('backtest_log.csv')
            os.remove('strategy_log.csv')
        except OSError:
            pass

    def import_data(self):
        """Format the time in hh:mm:ss.

        Parameters
        ----------

        Raises
        ------

        """
        data = pd.read_hdf(self.config['data']['path'], 'table').sort_values(by='date', ascending=True)
        benchmark_data = pd.read_csv(self.config['data']['benchmark'], parse_dates=['date'],
                                     dayfirst=True).sort_values(by='date', ascending=True)
        comparison_start = max(data['date'].min(), benchmark_data['date'].min())
        comparison_end = min(data['date'].max(), benchmark_data['date'].max())

        data = data[(data['date'] > comparison_start) & (data['date'] < comparison_end)]
        benchmark_data = benchmark_data[
            (benchmark_data['date'] > comparison_start) & (benchmark_data['date'] < comparison_end)]
        print("Discarding data before " + str(comparison_start) + " and after " + str(comparison_end))
        return data, benchmark_data

    def __init__(self):
        # Set initial configuration
        self.config = configparser.RawConfigParser()
        self.config.read('config.properties')
        self.global_settings()
        self.cash = float(self.config['broker']['cash'])
        self.tickers = self.config['data']['tickers']


        # Import data
        self.data, self.benchmark_data = self.import_data()
        # self.tickers = self.data['ticker'].unique()

        # Run the strategy
        self.cerebro = bt.Cerebro(stdstats=False)  # stdstats=False
        self.comminfo = FixedCommissionScheme()
        self.cerebro.broker.set_coc(True)
        self.strategy_results = self.run_strategy()
        self.portfolio_stats = self.strategy_results[0].analyzers.getbyname('pyfolio')
        self.returns, self.positions, self.transactions, self.gross_lev = self.portfolio_stats.get_pf_items()
        self.run_strategy_reports()
        self.ending_value = self.cerebro.broker.getvalue()

        # Run the benchmark
        self.cerebro_benchmark = bt.Cerebro(stdstats=False)  # stdstats=False
        self.benchmark_comminfo = FixedCommissionScheme()
        self.cerebro_benchmark.broker.set_coc(True)
        self.benchmark_results = self.run_benchmark()
        self.benchmark_stats = self.benchmark_results[0].analyzers.getbyname('pyfolio')
        self.benchmark_returns, self.benchmark_positions, self.benchmark_transactions, self.benchmark_gross_lev = self.benchmark_stats.get_pf_items()
        self.run_benchmark_reports()
        self.benchmark_ending_value = self.cerebro_benchmark.broker.getvalue()


def main():
    start = time.time()
    backtester = Backtester()
    duration = time.time() - start
    print(f'Runtime: {backtester.format_time(duration)}')


if __name__ == "__main__":
    main()
