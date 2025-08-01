import akshare as ak
import backtrader as bt
import pandas as pd


def fetch_stock_data(stock_code="603777", start_date="20220101", end_date="20240101"):
    """
    从akshare获取股票历史数据
    """
    try:
        df = ak.stock_zh_a_hist(
            symbol=stock_code,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq"
        )
        if df.empty:
            raise ValueError("获取的数据为空")

        # 重命名列以符合backtrader要求
        df.rename(columns={
            "日期": "date",
            "开盘": "open",
            "最高": "high",
            "最低": "low",
            "收盘": "close",
            "成交量": "volume"
        }, inplace=True)

        # 转换日期格式
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        print("数据获取成功:")
        print(df.head())
        return df

    except Exception as e:
        print(f"获取数据失败: {e}")
        return None


class BOLLStrategy(bt.Strategy):
    params = (
        ('n', 14),  # 计算周期
        ('k', 2),  # 标准差乘数
        ('printlog', True)  # 是否打印交易日志
    )

    def __init__(self):
        # 初始化指标
        self.boll = bt.indicators.BollingerBands(
            self.data.close,
            period=self.params.n,
            devfactor=self.params.k
        )
        self.order = None
        self.final_value = None

    def next(self):
        # 有未完成的订单就跳过
        if self.order:
            return
        # 未持仓就买入
        if not self.position:
            if self.data.close < self.boll.lines.bot:  # 突破下轨，超卖区域，买入
                self.order_target_percent(target=0.95)
        else:
            if self.data.close > self.boll.lines.mid:  # 突破中轨，卖出
                self.close()

    # 添加stop方法记录最终价值
    def stop(self):
        self.log(f'周期为{self.params.n},乘数为{self.params.k}的最后收益为{self.broker.getvalue()}', doprint=True)
        self.final_value = self.broker.getvalue()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return  # 订单提交或完成，无需操作

        if order.status in [order.Completed]:
            # 记录
            if order.isbuy():
                self.log(
                    f'买入执行：价格{order.executed.price:.2f},'
                    f'成本{order.executed.value:.2f},'
                    f'手续费{order.executed.comm:.2f}'
                )
            else:
                self.log(
                    f'卖出执行：价格{order.executed.price:.2f},'
                    f'成本{order.executed.value:.2f},'
                    f'手续费{order.executed.comm:.2f}'
                )

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/被拒绝')
        self.order = None

    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()},{txt}')


if __name__ == '__main__':
    cerebro = bt.Cerebro(optreturn=False)

    strats = cerebro.optstrategy(
        BOLLStrategy,
        n=range(15, 30, 5),
        k=[1.8, 2.0, 2.2],
        printlog=False  # 优化时关闭日志
    )
    data_df = fetch_stock_data()

    # 添加数据
    data = bt.feeds.PandasData(dataname=data_df)
    cerebro.adddata(data)

    # 设置初始资金
    cerebro.broker.setcash(100000.0)

    # 设置交易手续费
    cerebro.broker.setcommission(
        commission=0.0003,
        margin=0,
        commtype=bt.CommInfoBase.COMM_PERC,
        stocklike=True
    )

    # 添加分析指标
    cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='_annual_return')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='_sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='_drawdown')


    print('初始资金: %.2f' % cerebro.broker.getvalue())

    # 运行优化
    # for run in
    optimized_runs = cerebro.run()
    print(len(optimized_runs))
    for run in optimized_runs:
        strategy = run[0]
        params = strategy.params
        value = strategy.final_value
        sharpe = strategy.analyzers._sharpe.get_analysis()['sharperatio']

        print('\n策略参数组合:')
        print('周期 n = %d, 标准差乘数 k = %.2f' % (params.n, params.k))
        print('最终资金: %.2f' % value)
        print('年化收益率: ', strategy.analyzers._annual_return.get_analysis())
        print('夏普比率: %.4f' % sharpe)
        print('最大回撤: %.2f%%' % strategy.analyzers._drawdown.get_analysis()['max']['drawdown'])
        print('-' * 50)


