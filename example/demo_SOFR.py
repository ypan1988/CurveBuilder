#####
##### Part 1: Repricing SOFR Quotes and Non-Zero NPV (No CurveBuilder)
##### https://quant.stackexchange.com/questions/63105/repricing-sofr-quotes-and-non-zero-npv
#####

import QuantLib as ql

marketQuotes = [
('1W', 0.01982),
('2W', 0.02394),
('3W', 0.02503),
('1M', 0.02897),
('3M', 0.037),
('4M', 0.041),
('5M', 0.043),
('6M', 0.04597),
('7M', 0.04797),
('8M', 0.04997),
('9M', 0.05197),
('10M', 0.0535),
('11M', 0.055),
('1Y', 0.0565),
('15M', 0.06),
('18M', 0.069),
('21M', 0.083),
('2Y', 0.10403),
('3Y', 0.27409),
('4Y', 0.50109),
('5Y', 0.718),
('6Y', 0.90703),
('7Y', 1.066),
('8Y', 1.19203),
('9Y', 1.29306),
('10Y', 1.37903),
('12Y', 1.51294),
('15Y', 1.63591),
('20Y', 1.72494),
('25Y', 1.75318),
('30Y', 1.76979),
('40Y', 1.71094),
('50Y', 1.63649)]


import os
import pandas as pd
data_folder = ".\\example"
data1 = pd.read_excel(os.path.join(data_folder, "USDOIS_20240331.xlsx"), sheet_name="Sheet1")
tenors = data1["Tenor"].to_list()
rates = data1["Market Rate"].to_list()
marketQuotes = [(tenor, rate) for tenor, rate in zip(tenors, rates) ]

# Parameters
mktDate = ql.Date(8,3,2021)
mktDate = ql.Date(31,3,2024)

ql.Settings.instance().evaluationDate = mktDate
Settlement = 2
Calendar = ql.UnitedStates(ql.UnitedStates.Settlement)
DayCount = ql.Actual360()

# OIS Curve Helper
oisHelper = []
for quote in marketQuotes:
    oisHelper.append(ql.OISRateHelper(Settlement, ql.Period(quote[0]), 
        ql.QuoteHandle(ql.SimpleQuote(quote[1]/100)), ql.Sofr()))

# Curve Specification
sofrCurve = ql.PiecewiseLinearZero(Settlement, Calendar, oisHelper, DayCount)
valCurve = ql.YieldTermStructureHandle(sofrCurve)
sofrIndex = ql.Sofr(valCurve)
swapEngine = ql.DiscountingSwapEngine(valCurve)

# Reprice Quotes
for quote in marketQuotes:
    swapTenor = ql.Period(quote[0])
    fixedRate = quote[1]/100
    oisSwap = ql.MakeOIS(swapTenor, sofrIndex, fixedRate, nominal=1E6)
    print(quote, round(oisSwap.NPV(),3)) 

sofrCurve.nodes()