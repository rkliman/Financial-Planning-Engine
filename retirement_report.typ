#align(center)[
    = Retirement Analysis Summary
]

#let info_data = json("info.json")

== Assumptions and Inputs
#columns(2)[
- Investment Period: #calc.round(info_data.invest_period, digits: 2) years
- Retirement Period: #calc.round(info_data.retire_period, digits: 2) years
- Expected Return: #calc.round(info_data.expected_return, digits: 2)%
- Inflation Rate: #calc.round(info_data.inflation_rate, digits: 2)%
#colbreak()
- Pre-Tax Income: \$#calc.round(info_data.pre_tax, digits: 2)/yr (2024 dollars)
- Post-Tax Income: \$#calc.round(info_data.post_tax, digits: 2)/yr (2024 dollars)
- Retirement Income: \$#calc.round(info_data.retirement, digits: 2)/yr (2024 dollars)
]
=== Financial Goals
1. Supplemented (#info_data.financial_goals.supplemented%): #info_data.financial_goals.supplemented% of income comes from retirement account
2. Sustainable Retirement: Retirement account will be empty at the end of retirement
3. Generational Wealth: Can perpetually pull from account without loss of value
4. Nobility (+#info_data.financial_goals.nobility%/yr): Pulling from account doesn't stop account growth

=== Account Types
- *Brokerage Account:* A taxable account with no restrictions on withdrawals. It allows individuals to buy, sell, and hold various investment assets, such as stocks, bonds, mutual funds, and ETFs.
- *Traditional IRA:* A tax-deferred retirement account where contributions may be tax-deductible, but withdrawals in retirement are taxed as income. Early withdrawals may incur penalties.
- *Roth IRA:* A tax-free retirement account where contributions are made with after-tax dollars, and qualified withdrawals in retirement are tax-free. Early withdrawals may have restrictions.
- *Traditional 401k:* A tax-deferred employer-sponsored retirement account where contributions are made pre-tax, reducing taxable income. Withdrawals in retirement are taxed as income.
- *Roth 401k:* A tax-free employer-sponsored retirement account where contributions are made with after-tax dollars, and qualified withdrawals in retirement are tax-free.

#figure(
    image("figs/required_principal.png", width: 100%),
    // caption: [Required Principal by Financial Goal]
)

#figure(
    image("figs/yearly_contribution.png", width: 100%),
    // caption: [Yearly Contribution by Financial Goal]
)
    