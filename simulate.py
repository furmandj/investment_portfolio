from portfolio import Portfolio


capital = 100000
starting_year = 2022
monthly_investment = 0
portfolio = Portfolio(capital, starting_year, monthly_investment=monthly_investment)

house_price = 150000
closing_costs = 10000
loan_apr = 7
monthly_fees = 600
monthly_rent_collected = 1200
down_payment_fraction = 0.20
years_on_loan = 30
portfolio.buy_a_house(
    house_price,
    closing_costs,
    loan_apr,
    monthly_fees,
    monthly_rent_collected,
    down_payment_fraction=down_payment_fraction,
    years_on_loan=years_on_loan,
)
net_worth_history = [capital]
for month in range(years_on_loan * 12):
    portfolio.increment_one_month()
    net_worth_history.append(portfolio.get_net_worth(after_capital_gains_tax=True))

print(f'Final net worth: {net_worth_history[-1]}')
print(f'Average yearly return: {(net_worth_history[-1] / net_worth_history[0]) ** (1 / years_on_loan)}')
