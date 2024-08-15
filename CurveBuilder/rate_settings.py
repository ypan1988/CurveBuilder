import QuantLib as ql

# Rate Settings (ON)

# Rate Settings (IBOR)
rate_settings_ibor = {
"SEK_STIBOR_1W": ('STIBOR1W', ql.Period('1W'), 0, ql.SEKCurrency(), ql.TARGET(), ql.ModifiedFollowing, False, ql.Actual360()),
"SEK_STIBOR_1M": ('STIBOR1M', ql.Period('1M'), 0, ql.SEKCurrency(), ql.TARGET(), ql.ModifiedFollowing, False, ql.Actual360()),
"SEK_STIBOR_2M": ('STIBOR2M', ql.Period('2M'), 0, ql.SEKCurrency(), ql.TARGET(), ql.ModifiedFollowing, False, ql.Actual360()),
"SEK_STIBOR_3M": ('STIBOR3M', ql.Period('3M'), 0, ql.SEKCurrency(), ql.TARGET(), ql.ModifiedFollowing, False, ql.Actual360()),
"SEK_STIBOR_6M": ('STIBOR6M', ql.Period('6M'), 0, ql.SEKCurrency(), ql.TARGET(), ql.ModifiedFollowing, False, ql.Actual360()),
}
