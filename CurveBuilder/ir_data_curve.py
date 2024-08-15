import math
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt

import QuantLib as ql
from .rate_settings import rate_settings_ibor

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

  def __init__(self,
               valuation_date: ql.Date,
               tenors, 
               rates,
               instruments,
               index_name,
               rate_in_perc = False,
               is_IBOR = False,
               interpolation = 0,
               calendar = ql.TARGET(),
               day_count = ql.Actual360(),
               # parameters for Overnight rate index
               settlement_day = 2,
               # parameters for IBOR rate index
               fixed_frequency = ql.Annual,
               fixed_convention = ql.ModifiedFollowing,
               fixed_day_count = ql.Thirty360(ql.Thirty360.BondBasis),
               debug = True):
    assert len(tenors) == len(rates) == len(instruments), "tenors / rates / instruments doesn't have the same length"

    # Set the evaluation date 
    ql.Settings.instance().evaluationDate = valuation_date

    # Set the curve information
    self.n_nodes = len(tenors)
    self.valuation_date = valuation_date
    self.tenors = tenors.copy()
    self.rates = rates.copy()
    self.instruments = instruments.copy()

    # Convert rates from percent to decimal
    if rate_in_perc:
      self.rates = [r / 100 for r in self.rates]

    # Generate curve helpers
    self.yts = ql.RelinkableYieldTermStructureHandle()

    if is_IBOR:
      index_para = rate_settings_ibor[index_name]
      self.index = ql.IborIndex(*index_para, self.yts)
      helpers = self.init_ibor_helpers(calendar, fixed_frequency, fixed_convention, fixed_day_count)
    else:
      self.index = get_overnight_index(index_name, self.yts)
      helpers = [ ql.OISRateHelper(settlement_day, tenor, ql.QuoteHandle(ql.SimpleQuote(rate)), self.index)
                  for tenor, rate in zip(self.tenors, self.rates)]

    if (interpolation == 0):  
      self.curve = ql.PiecewiseLinearZero(0, calendar, helpers, day_count)
    elif (interpolation == 2):
      # C++: PiecewiseYieldCurve<ForwardRate, BackwardFlat>
      self.curve = ql.PiecewiseFlatForward(0, calendar, helpers, day_count)

    # Link the built curve to the relinkable yield term structure handle 
    # and build a swap pricing engine
    self.yts.linkTo(self.curve)
    self.engine = ql.DiscountingSwapEngine(self.yts)

    # Enable extrapolation
    self.curve.enableExtrapolation()

    # Print debug information
    if debug:
      print("tenors = ", self.tenors)
      print("rates = ", self.rates)
      print("IRDataCurve Created...")

  def init_ibor_helpers(self, calendar, fixed_frequency, fixed_convention, fixed_day_count):
    helpers = ql.RateHelperVector()
    for tenor, rate, instrument in zip(self.tenors, self.rates, self.instruments):
      if instrument == "DEPOSIT":
        helpers.append(ql.DepositRateHelper(rate, self.index))
      if instrument == "FRA":
        months_to_start = tenor.length()
        helpers.append(ql.FraRateHelper(rate, months_to_start, self.index))
      if instrument == "SWAP":
        helpers.append(ql.SwapRateHelper(rate, tenor, calendar, fixed_frequency,
                                         fixed_convention, fixed_day_count, self.index))
    return helpers
    
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