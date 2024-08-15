#####
##### Part 1: Replicating Bloomberg Curves with QuantLib (No CurveBuilder)
##### https://xiar-fatah.github.io/2023/10/05/quantlib-bootstrapping.html
#####

import numpy as np
import QuantLib as ql
from datetime import datetime, date, timedelta

# Set the valuation date
ql_date = ql.Date("2023-01-11", "%Y-%m-%d")
ql.Settings.instance().evaluationDate = ql_date

# Create an empty array to store all the helpers as previously mentioned.
store_helpers = []

# Define all the properties of the instrument
stibor_rate = 3.21800
stibor_maturity= '6M'
stibor_fixing_day = 0
stibor_calendar = ql.TARGET()
stibor_convention = ql.ModifiedFollowing
stibor_day_counter= ql.Actual360()

# The underlying floating rate
stibor_6m = ql.IborIndex('STIBOR6M',            # Name
                         ql.Period('6M'),       # Maturity
                         0,                     # Fixing day
                         ql.SEKCurrency(),      # Currency
                         ql.TARGET(),           # Calendar
                         ql.ModifiedFollowing,  # Calendar convention
                         False,                 # End of month
                         ql.Actual360())        # Day count

# Create the DepositRateHelper
# stibor_helper = ql.DepositRateHelper(ql.QuoteHandle(ql.SimpleQuote(stibor_rate/100.0)),
#                     ql.Period(stibor_maturity),
#                     stibor_fixing_day,
#                     stibor_calendar,
#                     stibor_convention,
#                     False, # EOM convention
#                     stibor_day_counter)

stibor_helper = ql.DepositRateHelper(ql.QuoteHandle(ql.SimpleQuote(stibor_rate/100.0)),stibor_6m)

# Store the DepositRateHelper to the list of helpers
store_helpers.append(stibor_helper)

# Calculate the mid quotes
bid_list= [3.51270, 3.45697, 3.29768, 3.18463,
 3.10489, 3.06276, 3.03423, 3.00924,
 2.99359, 2.97369, 2.94015, 2.87215,
 2.76782, 2.54788]
ask_list = [3.53271, 3.48944, 3.33052, 3.21477,
 3.13611, 3.09204, 3.06377, 3.03876,
 3.01821, 3.00251, 2.96605, 2.90305,
 2.79838, 2.57832]
mid = [(bid + ask)/2 for bid, ask in zip(bid_list,ask_list)]

fixedFrequency = ql.Annual                           # Frequency of the fixed leg
fixedConvention = ql.ModifiedFollowing               # Fixed leg convention
fixedDayCount = ql.Thirty360(ql.Thirty360.BondBasis) # Daycount convention of the fixed leg
calendar = ql.TARGET()

tenors =['1Y', '2Y', '3Y', '4Y',
        '5Y', '6Y', '7Y', '8Y',
        '9Y', '10Y', '12Y','15Y',
        '20Y', '30Y']
#iborIndex = index
for r,m in zip(mid, tenors):
    rate = ql.QuoteHandle(ql.SimpleQuote(r/100.0))
    tenor = ql.Period(m)
    swap_helper = ql.SwapRateHelper(
    rate, tenor, calendar, fixedFrequency, fixedConvention, fixedDayCount, stibor_6m
    )

    # Append each swap to our store_helpers
    store_helpers.append(swap_helper)

curve = ql.PiecewiseLinearZero(0, ql.TARGET(), store_helpers, ql.Actual365Fixed())
[curve.zeroRate(ql.Date(11,7,2023), ql.Actual365Fixed(), ql.Continuous).rate(),
curve.zeroRate(ql.Date(11,1,2024), ql.Actual365Fixed(), ql.Continuous).rate(),
curve.zeroRate(ql.Date(13,1,2025), ql.Actual365Fixed(), ql.Continuous).rate(),
curve.zeroRate(ql.Date(12,1,2026), ql.Actual365Fixed(), ql.Continuous).rate(),
curve.zeroRate(ql.Date(11,1,2027), ql.Actual365Fixed(), ql.Continuous).rate(),
curve.zeroRate(ql.Date(11,1,2028), ql.Actual365Fixed(), ql.Continuous).rate(),
curve.zeroRate(ql.Date(11,1,2029), ql.Actual365Fixed(), ql.Continuous).rate(),
curve.zeroRate(ql.Date(11,1,2030), ql.Actual365Fixed(), ql.Continuous).rate(),
curve.zeroRate(ql.Date(13,1,2031), ql.Actual365Fixed(), ql.Continuous).rate(),
curve.zeroRate(ql.Date(12,1,2032), ql.Actual365Fixed(), ql.Continuous).rate(),
curve.zeroRate(ql.Date(11,1,2033), ql.Actual365Fixed(), ql.Continuous).rate(),
curve.zeroRate(ql.Date(11,1,2035), ql.Actual365Fixed(), ql.Continuous).rate(),
curve.zeroRate(ql.Date(11,1,2038), ql.Actual365Fixed(), ql.Continuous).rate(),
curve.zeroRate(ql.Date(12,1,2043), ql.Actual365Fixed(), ql.Continuous).rate(),
curve.zeroRate(ql.Date(13,1,2053), ql.Actual365Fixed(), ql.Continuous).rate(),]

date, df = zip(*curve.nodes())
date = [d.ISO() for d in date]
curve.referenceDate()


#####
##### Part 2: Replicating Bloomberg Curves with QuantLib (using CurveBuilder)
#####

import CurveBuilder as cb
ql_date = ql.Date("2023-01-11", "%Y-%m-%d")
ql_tenors = [ql.Period(t) for t in ['6M'] + tenors]
rates = [stibor_rate] + mid 
instruments = ["DEPOSIT"] + ["SWAP"] * len(mid)

irdc = cb.IRDataCurve(ql_date,
                      ql_tenors,
                      rates,
                      instruments,
                      "SEK_STIBOR_6M",
                      rate_in_perc = True,
                      is_IBOR = True, 
                      calendar = ql.TARGET(),
                      day_count = ql.Actual365Fixed(),
                      fixed_frequency = ql.Annual,
                      fixed_convention = ql.ModifiedFollowing,
                      fixed_day_count = ql.Thirty360(ql.Thirty360.BondBasis),
                      debug = True)
irdc.get_zero_rates(ql.Date(11,7,2023))
irdc.get_zero_rates(ql.Date(11,1,2024))