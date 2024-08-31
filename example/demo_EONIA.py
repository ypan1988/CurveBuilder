#####
##### Part 1: Bootstrapping EONIA-based OIS curve (No CurveBuilder)
##### https://quant.stackexchange.com/questions/58333/bootstrapping-ois-curve
#####

import QuantLib as ql
today = ql.Date(22, 9, 2020)
ql.Settings.instance().evaluationDate = today

tenors = [
    '1D', '1W', '2W', '1M', '2M', '3M', '4M', '5M', '6M', '7M', '8M', '9M', '10M', '11M', '1Y',
     '18M', '2Y', '30M', '3Y', '4Y', '5Y', '6Y', '7Y', '8Y', '9Y', '10Y',  '11Y', '12Y',
     '15Y', '20Y', '25Y', '30Y', '35Y', '40Y', '50Y']

rates = [
    -0.467, -0.472, -0.47, -0.46, -0.471, -0.47, -0.481, -0.487, -0.5, -0.495, -0.5, -0.506,
     -0.51, -0.515, -0.52, -0.541, -0.551, -0.556, -0.56, -0.551, -0.531, -0.5, -0.462, -0.426,
    -0.379, -0.337, -0.293, -0.251, -0.147, -0.068, -0.055, -0.09, -0.099, -0.134, -0.172]

eonia = ql.Eonia()
helpers = []
for tenor, rate in zip(tenors,rates):
    if tenor == '1D':
        helpers.append( ql.DepositRateHelper(rate / 100, eonia ) )
    else:
        helpers.append( ql.OISRateHelper(2, ql.Period(tenor), ql.QuoteHandle(ql.SimpleQuote(rate/100)), eonia) )
eonia_curve = ql.PiecewiseLogCubicDiscount(0, ql.TARGET(), helpers, ql.Actual365Fixed())
discount_curve = ql.YieldTermStructureHandle(eonia_curve)
swapEngine = ql.DiscountingSwapEngine(discount_curve)

# You can then create OIS Swap instruments to get their fair rate.
overnightIndex = ql.Eonia(discount_curve)
for tenor, rate in zip(tenors, rates):
    if tenor == '1D': continue
    ois_swap = ql.MakeOIS(ql.Period(tenor), overnightIndex, 0.01, pricingEngine=swapEngine)
    print(f"{tenor}\t{ois_swap.maturityDate().ISO()}\t{ois_swap.fairRate():.4%}\t{rate:.4f}%\t{ois_swap.NPV()}")

#####
##### Part 2: Bootstrapping EONIA-based OIS curve (using CurveBuilder)
#####

import CurveBuilder as cb
ql_date = ql.Date(22, 9, 2020)
ql_tenors = [ql.Period(t) for t in tenors]
instruments = ["Deposit"] + ["OIS"] * (len(ql_tenors)-1)
irdc = cb.IRDataCurve(ql_date,
                      ql_tenors,
                      rates,
                      instruments,
                      "EONIA",
                      rate_in_perc = True,
                      is_IBOR = False,
                      interpolation = 3,
                      calendar = ql.TARGET(),
                      day_count = ql.Actual365Fixed(),
                      debug = True)

irdc.get_zero_rates(ql.Date(1,10,2020))
irdc.get_zero_rates(ql.Date(8,10,2020))
irdc.get_zero_rates(ql.Date(24,9,2070))

irdc.get_curve_df()
