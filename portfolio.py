import pandas as pd


def get_monthly_housing_growth_rate(year: int):
    house_prices = pd.read_csv('US_median_housing_prices.csv')
    population = pd.read_csv('US_population.csv')

    house_prices['year'] = house_prices.DATE.str.slice(0, 4)
    house_prices = house_prices[['MSPUS', 'year']].groupby('year').mean().reset_index()
    house_prices['change'] = 0
    house_prices['change'].iloc[1:] = house_prices.MSPUS.values[1:] / house_prices.MSPUS.values[:-1] - 1
    population['year'] = population.year.str.slice(0, 4)

    population = population.astype(float)
    house_prices = house_prices.astype(float)

    start_year = 1983
    end_year = 2022
    n_years = end_year - start_year
    average_age_to_buy_house = 33  # source: Google
    starting_population = population[population.year == start_year - average_age_to_buy_house].Population
    ending_population = population[population.year == end_year - average_age_to_buy_house].Population
    starting_house_price = house_prices[house_prices.year == start_year].MSPUS
    ending_house_price = house_prices[house_prices.year == end_year].MSPUS

    historical_population_growth_rate = (ending_population / starting_population) ** (1 / n_years)
    historical_house_price_growth_rate = (ending_house_price / starting_house_price) ** (1 / n_years)

    current_population_growth_rate = population[
        population.year == year - average_age_to_buy_house
    ][' Annual % Change']
    current_estimated_house_price_growth_rate = historical_house_price_growth_rate \
                                                + current_population_growth_rate \
                                                - historical_population_growth_rate
    return current_estimated_house_price_growth_rate ** (1 / 12) - 1


class House:
    def __init__(
            self,
            equity: float,
            principal: float,
            loan_apr: float,
            min_monthly_payment: float,
            monthly_fees: float,
    ):
        self.equity = equity
        self.principal = principal
        self.monthly_interest_rate = loan_apr / 100 / 12
        self.min_monthly_payment = min_monthly_payment
        self.monthly_fees = monthly_fees

        self.house_value = equity + principal

    def wait_one_month(self, year: int):
        increase_in_value = self.house_value * get_monthly_housing_growth_rate(year)
        self.equity += increase_in_value
        self.house_value += increase_in_value

    def make_a_payment(self, payment_amount: float = None):
        if payment_amount is None:
            payment_amount = self.min_monthly_payment
        assert payment_amount >= self.min_monthly_payment, \
            "Payment cannot be less than the minimum monthly payment"
        interest_paid = self.principal * self.monthly_interest_rate
        if self.principal + interest_paid + self.monthly_fees < payment_amount:
            if self.principal > 0:
                print(f'You paid off the remaining principal of {self.principal}.')
            payment_amount = self.principal + interest_paid + self.monthly_fees
        principal_paid = payment_amount - interest_paid - self.monthly_fees
        self.equity += principal_paid
        self.principal -= principal_paid


class Stocks:
    def __init__(
            self,
            initial_investment: float = 0,
            yearly_growth_factor: float = 1.09,
    ):
        self.amount_invested = initial_investment
        self.yearly_growth_factor = yearly_growth_factor

    def add_to_investment(self, amount: float):
        self.amount_invested += amount
        assert self.amount_invested >= 0, "Amount invested cannot be negative"

    def wait(self, years: float):
        growth_factor = self.yearly_growth_factor ** years
        self.amount_invested *= growth_factor


class Portfolio:
    def __init__(
            self,
            capital: float = 0,
    ):
        self.houses = []
        self.stocks = Stocks(initial_investment=capital)

    def add_to_stocks(self, amount: float):
        self.stocks.amount_invested += amount
        assert self.stocks.amount_invested >= 0, "Amount invested cannot be negative"

    @staticmethod
    def get_min_monthly_payment(
            loan_amount: float,
            loan_apr: float,
            years_on_loan: float,
    ):
        r = loan_apr / 100 / 12  # monthly_interest_rate
        n = years_on_loan * 12  # months on loan
        return loan_amount * (r * (1 + r) ** n) / ((1 + r) ** n - 1)

    def buy_a_house(
            self,
            price: float,
            closing_costs: float,
            loan_apr: float,
            monthly_fees: float,
            down_payment_fraction: float = 0.20,
            years_on_loan: float = 30,
    ):
        down_payment = price * down_payment_fraction
        total_paid_upfront = down_payment + closing_costs
        if self.stocks.amount_invested < total_paid_upfront:
            print('You do not have enough capital to buy this house.')
            return
        self.stocks.amount_invested -= total_paid_upfront
        loan_amount = price - down_payment
        min_monthly_payment = self.get_min_monthly_payment(
            loan_amount=loan_amount,
            loan_apr=loan_apr,
            years_on_loan=years_on_loan,
        )
        self.houses.append(House(
            equity=down_payment,
            principal=loan_amount,
            loan_apr=loan_apr,
            min_monthly_payment=min_monthly_payment,
            monthly_fees=monthly_fees,
        ))

    def get_net_worth(self):
        net_worth = self.stocks.amount_invested
        for house in self.houses:
            net_worth += house.equity
        return net_worth
