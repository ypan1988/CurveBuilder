import math
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt

import QuantLib as ql

def to_datetime(arg):
  return datetime(day=arg.dayOfMonth(), month=arg.month(), year=arg.year())

def get_overnight_index(index_name, yts):
  index_dict = {
    "ESTR": ql.Estr(yts),
    "SOFR": ql.Sofr(yts),
    "SONIA": ql.Sonia(yts)
  }
  return index_dict[index_name]

class IRDataCurve:

  def __init__(self, valuation_date, tenors, rates, instruments, index_name, interpolation = 0, settlement_day = 2):
    ql.Settings.instance().evaluationDate = valuation_date

    self.valuation_date = valuation_date
    self.tenors = tenors.copy()
    self.rates = rates.copy()
    
    print("tenors = ", tenors)
    print("rates = ", rates)
    
    self.yts = ql.RelinkableYieldTermStructureHandle()
    self.index = get_overnight_index(index_name, self.yts)

    helpers = [ ql.OISRateHelper(settlement_day, tenor, ql.QuoteHandle(ql.SimpleQuote(rate/100)), self.index)
               for tenor, rate in zip(tenors, rates)]

    if (interpolation == 0):
      self.curve = ql.PiecewiseLinearZero(0, ql.TARGET(), helpers, ql.Actual365Fixed())
    elif (interpolation == 2):
      # C++: PiecewiseYieldCurve<ForwardRate, BackwardFlat>
      self.curve = ql.PiecewiseFlatForward(0, ql.TARGET(), helpers, ql.Actual360())

    self.yts.linkTo(self.curve)
    self.engine = ql.DiscountingSwapEngine(self.yts)

    #self.curve.enableExtrapolation()

    print("IRDataCurve created")

  def get_curve_df(self, settlement_day = 2, day_counter = ql.Actual365Fixed(), compounding = ql.Continuous):

    end_dates = []
    zeros     = []
    dfs       = []
    for tenor, rate in zip(self.tenors, self.rates):
      ois_swap = ql.MakeOIS(tenor, self.index, rate/100, settlementDays=settlement_day)
      #pv = ois_swap.NPV() 
      #fair_rate = ois_swap.fairRate()
      end_date = ois_swap.maturityDate()
      discount_factor = self.curve.discount(end_date)
      zero_rate = self.curve.zeroRate(end_date, day_counter, compounding).rate()
      #zero_rate = -math.log(discount_factor) * 365.0/(maturity_date-self.valuation_date)
      
      end_dates.append(ois_swap.maturityDate().ISO())
      zeros.append(zero_rate*100)
      dfs.append(discount_factor)

    df = pd.DataFrame({"End Date": end_dates,
                       "Market Rate": self.rates,
                       "Zero Rate": zeros,
                       "Discount": dfs} )
    return df

  def get_zero_rates(self, dates, day_counter = ql.Actual365Fixed(), compounding = ql.Continuous):
    if type(dates) is not list: dates = [dates]
    return [self.curve.zeroRate(date, day_counter, compounding).rate() for date in dates]
  
  def get_discounting_factors(self, dates):
    if type(dates) is not list: dates = [dates]
    return [self.curve.discount(date) for date in dates]

  def plot_curve(self, mode=1):
    start = self.curve.referenceDate()
    end = self.curve.dates()[-1]
    dates = [ql.Date(serial) for serial in range(start.serialNumber(), end.serialNumber()+1)]
    if (mode == 1):
      rates = self.get_zero_rates(dates)
    elif (mode == 2):
      rates = self.get_discounting_factors(dates)
    plt.plot([to_datetime(d) for d in dates], rates)
    plt.show()

    """
    helpers = ql.RateHelperVector()
    for tenor, rate, instrument in zip(Tenors, Rates, Instruments):
      rate /= 100
      if instrument == "DEPOSIT":
        helpers.append(ql.DepositRateHelper(rate, index))
      if instrument == "FRA":
        monthsToStart = ql.Period(tenor).length()
        helpers.append(ql.FraRateHelper(rate, monthsToStart, index))
      if instrument == "SWAP":
        helpers.append(ql.SwapRateHelper(rate,ql.Period(tenor), ql.TARGET(), ql.Annual, ql.Following, ql.Thirty360(), index))
    """
