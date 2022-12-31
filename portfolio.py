import pandas as pd


def get_monthly_housing_growth_rate(year: int) -> float:
    house_prices = pd.read_csv('US_median_housing_prices.csv')
    population = pd.read_csv('US_population.csv')

    house_prices['year'] = house_prices.DATE.str.slice(0, 4)
    house_prices = house_prices[['MSPUS', 'year']].groupby('year').mean().reset_index()
    population['year'] = population.date.str.slice(0, 4)

    population['year'] = population['year'].astype(float)
    house_prices['year'] = house_prices['year'].astype(float)

    start_year = 1983
    end_year = 2022
    n_years = end_year - start_year
    average_age_to_buy_house = 33  # source: Google
    starting_population = population[population.year == start_year - average_age_to_buy_house].population.item()
    ending_population = population[population.year == end_year - average_age_to_buy_house].population.item()
    starting_house_price = house_prices[house_prices.year == start_year].MSPUS.item()
    ending_house_price = house_prices[house_prices.year == end_year].MSPUS.item()

    historical_population_growth_rate = (ending_population / starting_population) ** (1 / n_years)
    historical_house_price_growth_rate = (ending_house_price / starting_house_price) ** (1 / n_years)

    current_population_growth_rate = population[
        population.year == year - average_age_to_buy_house
    ]['Annual % Change'].item() / 100 + 1
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
            monthly_rent_collected: float,
    ) -> None:
        self.equity = equity
        self.principal = principal
        self.monthly_interest_rate = loan_apr / 100 / 12
        self.min_monthly_payment = min_monthly_payment + monthly_fees
        self.monthly_fees = monthly_fees
        self.monthly_rent_collected = monthly_rent_collected
        self.cash = 0
        self.capital_gains = 0
        self.income = 0

        self.house_value = equity + principal

    def wait_one_month(self, year: int) -> None:
        monthly_housing_growth_rate = get_monthly_housing_growth_rate(year)
        increase_in_value = self.house_value * monthly_housing_growth_rate
        self.capital_gains += increase_in_value
        self.equity += increase_in_value
        self.house_value += increase_in_value
        self.cash += self.monthly_rent_collected
        self.income += self.monthly_rent_collected
        self.monthly_rent_collected *= 1 + monthly_housing_growth_rate

    def make_a_payment(self, payment_amount: float = None) -> None:
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
        self.cash -= payment_amount
        self.income -= interest_paid + self.monthly_fees


class Stocks:
    def __init__(
            self,
            initial_investment: float = 0,
            yearly_growth_factor: float = 1.09,
    ) -> None:
        self.amount_invested = initial_investment
        self.yearly_growth_factor = yearly_growth_factor
        self.capital_gains = 0

    def add_to_investment(self, amount: float) -> None:
        self.amount_invested += amount
        assert self.amount_invested >= 0, "Amount invested cannot be negative"

    def wait(self, years: float) -> None:
        growth_fraction = self.yearly_growth_factor ** years - 1
        increase_in_value = self.amount_invested * growth_fraction
        self.amount_invested += increase_in_value
        self.capital_gains += increase_in_value


class Portfolio:
    def __init__(
            self,
            capital: float,
            starting_year: float,
            monthly_investment: float = 0,
            income_tax_rate: float = 0.30,
            capital_gains_tax_rate: float = 0.15,
    ) -> None:
        self.houses = []
        self.stocks = Stocks(initial_investment=capital)
        self.monthly_investment = monthly_investment
        self.year = starting_year
        self.income_tax_rate = income_tax_rate
        self.capital_gains_tax_rate = capital_gains_tax_rate

    def add_to_stocks(self, amount: float) -> None:
        self.stocks.amount_invested += amount
        assert self.stocks.amount_invested >= 0, "Amount invested cannot be negative"

    @staticmethod
    def get_min_monthly_payment(
            loan_amount: float,
            loan_apr: float,
            years_on_loan: float,
    ) -> float:
        r = loan_apr / 100 / 12  # monthly_interest_rate
        n = years_on_loan * 12  # months on loan
        return loan_amount * (r * (1 + r) ** n) / ((1 + r) ** n - 1)

    def buy_a_house(
            self,
            price: float,
            closing_costs: float,
            loan_apr: float,
            monthly_fees: float,
            monthly_rent_collected: float,
            down_payment_fraction: float = 0.20,
            years_on_loan: float = 30,
    ) -> None:
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
            monthly_rent_collected=monthly_rent_collected,
        ))

    def increment_one_month(self) -> None:
        self.year += 1 / 12
        self.stocks.wait(1 / 12)
        for house in self.houses:
            house.wait_one_month(int(self.year))
            house.make_a_payment()

            cash = house.cash - house.income * self.income_tax_rate
            self.add_to_stocks(cash)
            house.cash = 0
            house.income = 0
        self.add_to_stocks(self.monthly_investment)

    def get_net_worth(self, after_capital_gains_tax=True) -> float:
        net_worth = self.stocks.amount_invested - \
                    self.stocks.capital_gains * self.capital_gains_tax_rate * after_capital_gains_tax
        for house in self.houses:
            net_worth += house.equity - \
                         house.capital_gains * self.capital_gains_tax_rate * after_capital_gains_tax
        return net_worth

    def get_liquid_assets(self) -> float:
        return self.stocks.amount_invested
