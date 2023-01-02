# What's in the repo?

This repo houses simple tools to simulate two kinds of investments over time:

1. Stocks
2. Houses

I created this to fit my style of investing which is to put all of my liquid assets into S&P500 index funds. Now that I am thinking about branching out into real estate investments, I wanted a way to compare stock returns to returns on houses, and compare house loans to each other. This seemed a little too complicated to just work out on paper, so I created the tools in this repo to simulate these investments.

I assume that any investment money that is not currently wrapped up in real estate equity will be put into the stock market.

I made this tool for my own research, but figured it wouldn't hurt to let others use it if they like.

# Assumptions

The two main assumptions that went into the model have to do with house appreciation. These are the assumptions:

1. Long-term median house prices are dictated by
   1. inflation
   2. the number of people who are participating in the housing market (demand)
2. Average inflation over a long period of time is approximately constant

These two assumptions together mean that the difference between the current YOY growth of house prices and the historical YOY growth of house prices is equal to the YOY growth of the current demand minus the historical YOY growth of the demand. To estimate growth in demand, I simply used population growth 33 years prior (the average age that a person buys their first house according to Google).

Am I worried about these assumptions? Not really. Compared to the assumptions that the user must input to the model, such as the rate of return in the stock market or how much it will cost to maintain a house, I suspect that the implications of the preceding assumptions are rather small. Furthermore, I am quite confident that adding these assumptions into the model is better than the alternative assumption, which is that housing prices continue to grow at the average rate that they have grown over the past 60 years or whatever.

There is one other assumption, but I believe this one is quite solid: Rent increase is proportional the increase in property value.

# How complex is the model? Does it model everything?

The stock market model is very simple and just assumes continuous exponential growth. For long-term diversified stock investments, I believe this to be reasonable.

For the real estate model, I added everything I could think of to the model. Here is a list:
- Purchase price
- Down payment size
- Closing costs
- APR on the loan
- Number of years on the loan
- Monthly fees (This is the sum of all the monthly fees, including HOA fees, homeowners insurance, and maintenance)
- House appreciation
- Monthly rent collected (or saved if you are buying a house instead of renting)
- Increase in monthly rent proportional to increase in house value
- Property tax
- Income tax
- Write-offs for monthly fees, interest, and property tax.
- Capital gains tax for net worth calculation (optional whether to apply it)
- Adjustment for inflation for net worth calculation (optional whether to apply it)

Please let me know if I should be adding anything to this model!

# How to use it

Please see the following two files for examples of how to use the model:
- simulate.py
- stocks_vs_houses.ipynb (this one is probably a bit more informative)

# Data sources

- Population growth rates by year: https://www.macrotrends.net/countries/USA/united-states/population-growth-rate
- Median housing prices by year: https://fred.stlouisfed.org/series/MSPUS