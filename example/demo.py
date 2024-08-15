import os
import pandas as pd
import QuantLib as ql
import CurveBuilder as cb

data_folder = ".\\example"

data1 = pd.read_excel(os.path.join(data_folder, "USDOIS_20240331.xlsx"), sheet_name="Sheet1")
date = [ql.Date(d.day, d.month, d.year) for d in data1["Date"]]
tenor = [ql.Period(t) for t in data1["Tenor"]]
rate = [r/100 for r in data1["Market Rate"]]
instrument = ["OIS"] * len(rate)

rates_BBG = [r/100 for r in data1["Zero Rate"]]

irdc1 = cb.IRDataCurve(ql.Date(31,3,2024),
                       tenors=tenor,
                       rates=rate,
                       instruments=instrument,
                       index_name="SOFR",
                       rate_in_perc=False,
                       is_IBOR=False,
                       interpolation=0,
                       calendar=ql.UnitedStates(ql.UnitedStates.Settlement),
                       day_count=ql.Actual360())

rates_CB = []
for date, rate in irdc1.curve.nodes():
    print(date.ISO(), rate)
    rates_CB.append(rate*100)
rates_CB = rates_CB[1:]
for i in range(len(rates_CB)):
    print(rates_BBG[i]-rates_CB[i])

irdc1.get_zero_rates(ql.Date(9,4,2024))
irdc1.get_zero_rates(ql.Date(3,4,2074))
irdc1.get_discounting_factors(ql.Date(9,4,2024))