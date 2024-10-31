# External modules
from neuralintents.assistants import BasicAssistant # This is the AI library we'll use for our chatbot/AI assistant, updated to BasicAssistant b/c Generic isn't in use anymore
import matplotlib.pyplot as plt
import pandas as pd 
import pandas_datareader as web 
import mplfinance as mpf

import pickle # For serialization
import sys # To exti the script when necessary
import datetime as dt


# Guideline to react/directions for what to say depending on our message
# Set of sample inputs so we don't have to hard-code every prompt in a json file: json doesn't allow comment but we can have as many intents as we want (intent=feature we want from our financial assistant).
# In each intent, we can have as many patterns as we want. The more patterns we feed our ML model, the more accurate our responses will be. 
# The context_set field in chatbot intents is used to manage conversation flow by creating/switching contexts based on user interactions. It helps maintain continuity+understand when a certain response or behavior is appropriate within a specific conversational context.

portfolio = {'AAPL': 20, 'TSLA': 5, 'GS': 10} # Key = ticket symbol, value = how many pair of each we own


# Serialize portfolio into a file. 
with open('C:/Users/narge/VSCodeProjects/CSC301/A2/portfolio.pkl', 'rb') as f:
    portfolio = pickle.load(f) # Dump portfolio into the file 
# Have it in a file, dont need to create object during runtime


def save_portfolio():
    # If we change something, this function is how we will save it to the file
    with open('C:/Users/narge/VSCodeProjects/CSC301/A2/portfolio.pkl', 'wb') as f:
        pickle.dump(portfolio, f)


def add_portfolio():
    # Ask for user input (hard-coded)
    ticker = input("Which stock would you like to add to your portfolio? ")
    amount = input("How many shares would you like to add? ")
    # Don't want to over-ride the value, we want to modify it (increase) by *amount* shares
    if ticker in portfolio.keys():
        portfolio[ticker] += amount
    else: # Stock not in portfolio; new stock
        portfolio[ticker] = amount
    # Save our changes to the portfolio
    save_portfolio()


def remove_portfolio():
    # Ask for user input (hard-coded)
    ticker = input("Which stock would you like to sell from your portfolio? ")
    amount = input("How many shares would you like to sell? ")
    # Don't want to over-ride the value, we want to modify it (increase) by *amount* shares
    if ticker in portfolio.keys():
        # Check that we have the number of shares user is trying to sell
        if amount <= portfolio[ticker]:
            portfolio[ticker] -= amount
            save_portfolio()
        # Can't remove what we don't own 
        else: 
            print("Oops, you don't have enough shares! ")
    else:
        print(f"Oops, you don't own any shares of {ticker}. ")


def show_portfolio():
    print("Your portfolio: ")
    # Contents of portfolio:
    for ticker in portfolio.keys():
        print(f"You own {portfolio[ticker]} shares of {ticker}. ")


def portfolio_worth():
    # Real-time worth of user's portfolio
    worth_sum = 0 
    for ticker in portfolio.keys():
        # Grab value from Yahoo finance API
        data = web.DataReader(ticker, 'yahoo')
        price = data['Close'].iloc[-1] # Last closing value
        worth_sum += price
    print(f"Your portfolio is worth {worth_sum} USD.")


def portfolio_gains():
    # How is portfolio performing? Compares portfolio to a date in the past to answer this question.
    # Exact stocks we own, their price now versus in the past, no complex analysis of how much we made by buying/selling in the past, etc.
    start_date = input("Enter a date for comparison (YYYY-MM-DD): ")
    sum_now = 0 # Worth of stocks we own currently
    sum_then = 0 # Worth of stocks we own at a previous date
    try:
        for ticker in portfolio.keys():
            data = web.DataReader(ticker, 'yahoo')
            price_now = data['Close'].iloc[-1]
            price_then = data.loc[data.index == start_date]['Close'].values[0] # Data location is there the index is the same as our start date
            sum_now += price_now
            sum_then += price_then
        print(f"Relative gains are {((sum_now - sum_then)/sum_then) * 100}%. ")
        print(f"Absolute gains are {(sum_now - sum_then)} USD. ")
    except IndexError: # No trading on stock that day, we can't look up the price
        print("Oops, there was no trading on this day!")


def plot_chart():
    # Basic candlestick chart
    ticker = input("Choose a ticker symbol: ")
    start_string = input("Enter a starting date (DD/MM/YYYY): ") # Need to covert this to a datetime object 
    plt.style.use('fivethirtyeight')
    start_date = dt.datetime.strptime(start_string, "%d/%m/%Y") # Converts the string to a date
    end_date = dt.datetime.now() # Current date
    data = web.DataReader(ticker, 'yahoo', start_date, end_date)
    # Change look (colours)
    colours = mpf.make_marketcolors(up = '#00fa9a', down = '#ff0000', wick = 'inherit', edge = 'inherit', volume = 'in') # inherit means take it from the parent theme
    mpf_style = mpf.make_mpf_style(base_mpf_style = 'charles', marketcolors = colours)
    mpf.plot(data, type = 'candle', style = mpf_style, volume = True)


#def bye():
#    sys.exit(0)


# Map intents to functions
mappings = {
    'plot_chart' : plot_chart,
    'show_portfolio' : show_portfolio,
    'add_portfolio' : add_portfolio,
    'portfolio_gains' : portfolio_gains,
    'portfolio_worth' : portfolio_worth,
    'remove_portfolio' : remove_portfolio
    # 'bye' : bye
}
assistant = BasicAssistant('C:/Users/narge/VSCodeProjects/CSC301/A2/intents.json')
assistant.fit_model(epochs=50)
assistant.save_model()
done = False

while not done:
    message = input("Enter a message: ")
    if message == "STOP":
        done = True
    else:
        print(assistant.process_input(message))