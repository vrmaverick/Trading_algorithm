#region imports
from AlgorithmImports import *
#endregion
from collections import deque

class AdaptableSkyBlueHornet(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2021, 1, 1)
        self.SetCash(100000)
        self.spy = self.AddEquity("SPY", Resolution.Daily).Symbol
        self.sma = CustomSimpleMovingAverage("CustomSMA", 30)
        self.RegisterIndicator(self.spy, self.sma, Resolution.Daily)

    
    def OnData(self, data):
        if not self.sma.IsReady:
            return
        # Save high, low, and current price
        hi = self.History(self.spy, timedelta(365), Resolution.Daily)
        l= min(hi["low"])
        h = max(hi["high"])
        price = self.Securities[self.spy].Price
        # Go long if near high and uptrending
        if price * 1.05 >= h and self.sma.Current.Value < price:
            if not self.Portfolio[self.spy].IsLong:
                self.SetHoldings(self.spy, 1)
        # Go short if near low and downtrending
        elif price * 0.95 <= l and self.sma.Current.Value > price:  
            if not self.Portfolio[self.spy].IsShort:
                self.SetHoldings(self.spy, -1)
        # Otherwise, go flat
        else:
            self.Liquidate()
        self.Plot("Benchmark", "52w-High", h)
        self.Plot("Benchmark", "52w-Low", l)
        self.Plot("Benchmark", "SMA", self.sma.Current.Value)
class CustomSimpleMovingAverage(PythonIndicator):
    def __init__(self, name, period):
        self.Name = name
        self.Time = datetime.min
        self.Value = 0
        self.queue = deque(maxlen=period)
    def Update(self, input):
        self.queue.appendleft(input.Close)
        self.Time = input.EndTime
        count = len(self.queue)
        self.Value = sum(self.queue) / count
        # returns true if ready
        return (count == self.queue.maxlen)
