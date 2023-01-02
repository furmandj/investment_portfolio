"""
The classes in this file were built with the intention of comparing stock
investments to real estate investments, and further to compare different
real estate investments to each other.
"""
import pandas as pd


class EconomyData:
    def __init__(self):
        """
        This class houses the following economic data:
        - average inflation rate
        - population over time
        - median house price over time
        And some of their derivatives that allow us to estimate the median
        house prices into the future.
        """
        self.inflation_rate = 0.038  # Average inflation rate according to worlddata.info

        self.house_prices = pd.read_csv('US_median_housing_prices.csv')
        self.population = pd.read_csv('US_population.csv')

        self.house_prices['year'] = self.house_prices.DATE.str.slice(0, 4)
        house_prices = self.house_prices[['MSPUS', 'year']].groupby('year').mean().reset_index()
        self.population['year'] = self.population.date.str.slice(0, 4)

        self.population['year'] = self.population['year'].astype(float)
        house_prices['year'] = house_prices['year'].astype(float)

        start_year = 1983
        end_year = 2022
        n_years = end_year - start_year
        self.average_age_to_buy_house = 33  # source: Google

        starting_population = self.population[
            self.population.year == start_year - self.average_age_to_buy_house].population.item()
        ending_population = self.population[
            self.population.year == end_year - self.average_age_to_buy_house].population.item()

        starting_house_price = house_prices[house_prices.year == start_year].MSPUS.item()
        ending_house_price = house_prices[house_prices.year == end_year].MSPUS.item()

        self.historical_population_growth_factor = self.get_historical_growth_factor(
            starting_population,
            ending_population,
            n_years
        )
        self.historical_house_price_growth_factor = self.get_historical_growth_factor(
            starting_house_price,
            ending_house_price,
            n_years
        )

    @staticmethod
    def get_historical_growth_factor(
            starting_value: float,
            ending_value: float,
            n_years: float,
    ) -> float:
        return (ending_value / starting_value) ** (1 / n_years)

    def get_monthly_housing_growth_rate(self, year: int) -> float:
        """
        The median price of houses over a long time period seems to be
        dictated by inflation and population growth. Assuming average
        inflation is the same as its historical values, we can just
        look at population growth rates. Luckily for us, we know the
        future of the effective population growth rates because we
        don't actually care about how many babies are born. We just
        care about the number of people who want to buy houses, which
        is predictable since we know how many people were born over
        the last 30+ years. According to Google, the average age at
        which people buy their first house is 33. So, we can simply
        look back at the population growth rate 33 years ago to
        estimate the growth rate of the number of people who want to
        buy houses today. We then adjust the historical growth rate of
        house prices by subtracting off the delta between the current
        year-over-year (YOY) growth in demand vs the historical YOY
        growth in demand calculated over the same time period as the
        historical housing prices. This allows us to estimate the
        growth rate of house prices 33 years into the future. This
        population data set actually has estimates of future US
        populations out to 2100, so we can go further out, but with
        less certainty.

        :param year: The year we are interested in. E.g. 2025
        :return: The estimated monthly rate of growth in median
            house price.
        """
        if year + self.average_age_to_buy_house > 2100:
            current_population_growth_factor = self.population.iloc[-1]['Annual % Change'].item() / 100 + 1
        else:
            current_population_growth_factor = self.population[
                self.population.year == year - self.average_age_to_buy_house
            ]['Annual % Change'].item() / 100 + 1
        current_estimated_house_price_growth_factor = self.historical_house_price_growth_factor \
                                                    + current_population_growth_factor \
                                                    - self.historical_population_growth_factor
        return current_estimated_house_price_growth_factor ** (1 / 12) - 1


class House:
    def __init__(
            self,
            equity: float,
            principal: float,
            loan_apr: float,
            property_tax_frac: float,
            min_monthly_payment: float,
            monthly_fees: float,
            monthly_rent_collected: float,
    ) -> None:
        """
        This class keeps track of a house loan, collected
        rent, taxable income, and capital gains.

        :param equity: Amount the house is worth minus the principal
        :param principal: The amount still owed on the loan
        :param loan_apr: APR % of the loan
        :param property_tax_frac: fraction applied to house_value to get
            the yearly property tax.
        :param min_monthly_payment: The minimum monthly payment on the loan
        :param monthly_fees: The sum of all fees that are paid monthly. This
            includes HOA fees, homeowners insurance, and maintenance.
        :param monthly_rent_collected: The amount of rent that can be collected
            monthly
        """
        self.equity = equity
        self.principal = principal
        self.monthly_interest_rate = loan_apr / 100 / 12
        self.monthly_property_tax_frac = property_tax_frac / 12
        self.min_monthly_payment = min_monthly_payment + monthly_fees
        self.monthly_fees = monthly_fees
        self.monthly_rent_collected = monthly_rent_collected
        self.cash = 0
        self.capital_gains = 0
        self.income = 0
        self.months_into_loan = 0
        self.accumulated_growth_factor = 1

        self.house_value = equity + principal
        self.monthly_property_tax = self.house_value * self.monthly_property_tax_frac

    def wait_one_month(self, monthly_housing_growth_rate: float) -> None:
        """
        This method collects the rent, updates the house_value,
        equity, taxable_income, cash on hand, and capital_gains.

        It also increases the rent every year proportionally to
        the house_value. The assumption is that with year-long
        leases, we will only be able to do this yearly. Similarly,
        we assume that property taxes are also only adjusted once
        per year.

        :param monthly_housing_growth_rate: The monthly growth
            rate of the median house price (the monthly growth
            factor is 1 + monthly_housing_growth_rate)
        """
        self.months_into_loan += 1
        self.accumulated_growth_factor *= 1 + monthly_housing_growth_rate
        increase_in_value = self.house_value * monthly_housing_growth_rate
        self.capital_gains += increase_in_value
        self.equity += increase_in_value
        self.house_value += increase_in_value
        net_earnings = self.monthly_rent_collected - self.monthly_property_tax
        self.cash += net_earnings
        self.income += net_earnings
        if (self.months_into_loan % 12) == 0:
            self.monthly_rent_collected *= self.accumulated_growth_factor
            self.accumulated_growth_factor = 1
            self.monthly_property_tax = self.house_value * self.monthly_property_tax_frac

    def make_a_payment(self, payment_amount: float = None) -> None:
        """
        Makes a payment on the loan, and updates the equity, principal,
        cash on hand, and taxable income accordingly. The assumption is
        that we are allowed to write off the interest_paid and the
        monthly fees.

        :param payment_amount: Amount you wish to pay on the loan. This
            must be at least the minimum monthly payment.
        """
        if payment_amount is None:
            payment_amount = self.min_monthly_payment
        assert payment_amount >= self.min_monthly_payment, \
            "Payment cannot be less than the minimum monthly payment"
        interest_paid = self.principal * self.monthly_interest_rate
        if self.principal + interest_paid + self.monthly_fees < payment_amount:
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
            yearly_growth_factor: float = 1.1,
    ) -> None:
        """
        Keeps track of the value of your stock portfolio, as well as
        the amount of capital gains.

        :param initial_investment: (float, optional) The initial amount
            you want to put into stocks. Default: 0
        :param yearly_growth_factor: (float, optional) YOY growth factor.
            1.1 was chosen because the average return of S&P500 seems to
            be around 10% (though different numbers also get thrown around).
            Default: 1.1
        """
        self.amount_invested = initial_investment
        self.yearly_growth_factor = yearly_growth_factor
        self.capital_gains = 0

    def wait(self, years: float) -> None:
        """
        Allow the stocks to grow in value for a period of time.
        Updates the capital_gains accordingly.

        :param years: Number of years to wait
        """
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
        """
        Tracks a portfolio comprised of stocks and real estate.
        Any amount of money in the portfolio is assumed to be
        invested in the stock market if it is not currently in
        a house. Any number of houses with varying loan details
        can be added to the portfolio as long as there is enough
        capital. Whenever a house is added to the portfolio, the
        money used to buy the house is taken out of the stocks
        portion of the portfolio.

        :param capital: Starting investment amount
        :param starting_year: The year the investment is made. E.g. 2025
        :param monthly_investment: The amount of cash added to the
             portfolio every month
        :param income_tax_rate: The rate at which your income is taxed
        :param capital_gains_tax_rate: The rate at which long term
            capital gains are taxed
        """
        self.houses = []
        self.stocks = Stocks(initial_investment=capital)
        self.monthly_investment = monthly_investment
        self.year = starting_year
        self.starting_year = starting_year
        self.income_tax_rate = income_tax_rate
        self.capital_gains_tax_rate = capital_gains_tax_rate
        self.economy_data = EconomyData()

    def add_to_portfolio(self, amount: float) -> None:
        """
        Add some amount of money to the stocks portion of
        the portfolio. This is the only way to increase the
        portfolio investment through using outside funds.

        Note that if amount is negative, then money is taken
        out of the portfolio.

        :param amount: Amount of money to add to the portfolio
        """
        self.stocks.amount_invested += amount
        assert self.stocks.amount_invested >= 0, "Amount invested cannot be negative"

    @staticmethod
    def get_min_monthly_payment(
            loan_amount: float,
            loan_apr: float,
            years_on_loan: float,
    ) -> float:
        """
        Calculates the monthly payment of the amortized loan.

        :param loan_amount: Original loan amount
        :param loan_apr: APR % on the loan
        :param years_on_loan: Number of years it will take to pay
            the loan off
        :return: The monthly payment amount required to pay off the
            loan in exactly years_on_loan years.
        """
        r = loan_apr / 100 / 12  # monthly_interest_rate
        n = years_on_loan * 12  # months on loan
        return loan_amount * (r * (1 + r) ** n) / ((1 + r) ** n - 1)

    def buy_a_house(
            self,
            price: float,
            closing_costs: float,
            loan_apr: float,
            property_tax_frac: float,
            monthly_fees: float,
            monthly_rent_collected: float,
            down_payment_fraction: float = 0.20,
            years_on_loan: float = 30,
    ) -> None:
        """
        Adds a house to the portfolio.

        :param price: Price paid for the house (no additional
            costs, such as closing costs, included)
        :param closing_costs: Closing costs
        :param loan_apr: APR % of the loan
        :param property_tax_frac: fraction applied to house_value to get
            the yearly property tax.
        :param monthly_fees: The sum of all fees that are paid monthly. This
            includes HOA fees, homeowners insurance, and maintenance.
        :param monthly_rent_collected: Amount of monthly rent that can
            be charged once the house gets rented out.
        :param down_payment_fraction: Fraction of the house price that
            is paid up front
        :param years_on_loan: Number of years on the loan
        """
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
            property_tax_frac=property_tax_frac,
            min_monthly_payment=min_monthly_payment,
            monthly_fees=monthly_fees,
            monthly_rent_collected=monthly_rent_collected,
        ))

    def increment_one_month(self) -> None:
        """
        Waits for one month. This does the following:
        1. Grows the value of the stock portfolio
        2. Updates the value of the houses in the portfolio
        3. Collects rent on all the house
        4. Makes payments on all the houses
        5. Moves the cash generated from rent minus expenses into
            the stock portfolio. Note that if this number is negative,
            then money is actually taken out of the stock portfolio.
        6. Adds the monthly investment to the stock portfolio
        """
        self.year += 1 / 12
        monthly_housing_growth_rate = self.economy_data.get_monthly_housing_growth_rate(int(self.year))
        self.stocks.wait(1 / 12)
        for house in self.houses:
            house.wait_one_month(monthly_housing_growth_rate)
            house.make_a_payment()

            cash = house.cash - house.income * self.income_tax_rate
            self.add_to_portfolio(cash)
            house.cash = 0
            house.income = 0
        self.add_to_portfolio(self.monthly_investment)

    def get_net_worth(self, after_capital_gains_tax=False, adjust_for_inflation=False) -> float:
        """
        Calculates the net worth of the portfolio

        :param after_capital_gains_tax: (bool, optional) If True,
            subtracts off the capital gains tax. Otherwise, returns
            the net worth without considering capital gains tax.
            Default: False
        :param adjust_for_inflation: (bool, optional) If True, adjusts
            the net worth for inflation, so that it is in today's dollars.
        :return: The net worth of the portfolio
        """
        net_worth = self.stocks.amount_invested - \
                    self.stocks.capital_gains * self.capital_gains_tax_rate * after_capital_gains_tax
        for house in self.houses:
            net_worth += house.equity - \
                         house.capital_gains * self.capital_gains_tax_rate * after_capital_gains_tax
        if adjust_for_inflation:
            net_worth /= (self.economy_data.inflation_rate + 1) ** (self.year - self.starting_year)
        return net_worth
