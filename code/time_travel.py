''' Main loop code ''' 
from stock_lib import *
import numpy as np 
import os 
import pandas as pd 
from datetime import date, timedelta
import matplotlib.pyplot as plt
from random import randint
from random import choices
from matplotlib import ticker
from math import floor
from time import time
from copy import copy
from math import exp, log 

tic = time()

def net_plot(port_net_worth, acc_net_worth):
    ''' Final plot of net worth for each date '''
    return 

def load_stocks(l=[]):
    big_df = pd.DataFrame()
    data_folder_path = r"C:\Users\Konpoul\Desktop\Master\prog-ds\Projects-2021\Python\Stock_Market_data\Stocks"
    for txt in l :
        path = os.path.join(data_folder_path, txt)
        try:
            frame = pd.read_csv(path)
            name = txt.split('.')[0]
            frame.insert(0, 'Stock', name)
        except:
            print(f"Unable to load {txt}")
        big_df = big_df.append(frame)
    return big_df

def available_dates(big_df):
    dates = big_df['Date']
    dates = dates.sort_values(ignore_index=True)
    return dates

def intraday( single_date, portfolio, account, today_state, margine_called):
    ''' Intraday Trading'''

    possesions_copy = portfolio.possessions.copy()

    for poss in possesions_copy.keys(): 
        
        poss_today = today_state[today_state['Stock'] == poss]
        if (not poss_today.empty):
            poss_today = poss_today.iloc[0]
            N = portfolio.possessions[poss][3] - 2 # last dates' number of possessions
            open_p = poss_today.at['Open']
            high_p = poss_today.at['High']
            close_p = poss_today.at['Close']
            low_p = poss_today.at['Low']
            
            # compute most profitable transaction
            diff1 = incr * high_p - close_p
            diff2 = incr * open_p - low_p
            diff = diff1 - diff2 
            if (diff >= 0): decide = 1
            else : decide = 2 

            # Test for volume
            volume = poss_today.at['Volume']
            if (N + margine_called > 0.1 * volume) : 
                N = floor(0.1 * volume - margine_called)

            if ((incr * high_p >= close_p) and (decide == 1)) :
                success = trade('sell-high', single_date, poss, N, account, portfolio, today_state)      # Sell- high and then  buy-close
                if (type(success)==bool) : portfolio.log_transaction(single_date, 'sell-high', poss, N) ; print(' INTRADAY SELL TRADE EXECUTED, ', poss ,' sell high', N)
                success = trade('buy-close', single_date, poss, N, account, portfolio, today_state)
                if (type(success)==bool) : portfolio.log_transaction(single_date, 'buy-close', poss, N) ; print(' INTRADAY BUY TRADE EXECUTED, ', poss,' buy close', N) ; return True
     
            elif ((incr * open_p >= low_p ) and (decide == 2)) :
                success = trade('sell-open', single_date, poss, N, account, portfolio, today_state)      # Sell- open and then  buy-low
                if (type(success)==bool) : portfolio.log_transaction(single_date, 'sell-open', poss, N) ; print(' INTRADAY SELL TRADE EXECUTED , ', poss ,'sell open', N)
                success = trade('buy-low', single_date, poss, N, account, portfolio, today_state)
                if (type(success)==bool) : portfolio.log_transaction(single_date, 'buy-low', poss, N) ; print(' INTRADAY BUY TRADE EXECUTED , ', poss ,' buy low', N) ; return True
           
            # if I did not intra-trade return false
            return False
    return False
  
    

def margin_call(today_state, portfolio, account, date):
    ''' Liquidate assets !!! '''
    possesions_copy = portfolio.possessions.copy()
    N=0
    for poss in possesions_copy.keys(): 
        volume = today_state[today_state['Stock'] == poss].iloc[0].at['Volume']
        N = floor(0.09  * volume)
        if (N > portfolio.possessions[poss][1]):
            N = floor(portfolio.possessions[poss][1] )
        print('Attempting DEBULK')
        success = trade('sell-open', date, poss, N, account, portfolio, today_state)
        if (type(success)==bool) : portfolio.log_transaction(single_date, 'sell-open', poss, N) ; print("MAAAAAAAAAAARRRRRRRRGGGGGGGGGGGGIIIIIIINNNNNNNNN CAAAAAAAAAAAAAAAAALL")
    # amount of stocks margin called during this day (used for volume restrictions)
    return N


# Only Microsoft stock loaded
big_df = load_stocks( ['msft.us.txt']) 
dates = available_dates(big_df)
print('All dates :',len(dates))
print('unique dates :',len(dates.unique()))

# Initialization of objects
max_moves = 1000
portfolio = Portfolio(max_moves=max_moves) 
account = Account()
port_net_worth = []
acc_net_worth = []
plot_dates = []

#  Parameter Value Setting
sell_threshold = 0.18 #account.balance * 0.06
buy_threshold = 0.08 #account.balance * 0.04
sell_percent = 0.50
s = log(10)
b = log(10)
a_list = ['buy', 'hold', 'sell']
probs = [0.65, 0.125, 0.125] # probabilities for buy,sell
# intraday increase 
global incr 
incr = 1 - 0.045

# TIME SIMULATION
liquidate = False  # controls beggining of liquidation
for i, single_date in enumerate(dates.unique()): 
    # only today's information
    today_state = big_df[big_df['Date']==single_date]
    #print(single_date)
    year = int(single_date.split('-')[0])
    month = int(single_date.split('-')[1])
    day = int(single_date.split('-')[2])
    if ( year == 1990): 
        s = 1.001
        b = 1.001

    # Start mass selling
    if ((year == 2017) and (month == 5) and (day == 1)):
         liquidate = True
    if (liquidate):
       margine_called =  margin_call(today_state, portfolio, account, single_date)
    else : margine_called = 0 

    
    if not margine_called:
    # Under some conditions it is worth to do an Intraday Transaction
        intra = intraday(single_date, portfolio, account, today_state, margine_called)
        
    # if intraday transaction was not made 
    if ((not intra) and (not margine_called)) :
        buys = today_state[today_state['Low'] < buy_threshold] 
        for buy in buys['Stock']:
            decision = choices(a_list, probs)[0]
            if (decision=='buy'):
                if (buy in portfolio.possessions.keys()):
                    N = portfolio.possessions[buy][3] 
                    price = today_state[today_state['Stock']==buy].iloc[0].at['Low']
                    # If balance is not enough to buy maximum possible number of stocks, spend as much as possible
                    if (N*price > account.balance) : N = floor(account.balance/price) 
                    if (N==0) : N = 1

                   # volume = today_state[today_state['Stock'] == buy].iloc[0].at['Volume']
                  #  if (N > 0.1 * volume ) : 
                   #     N = floor(0.095 * volume)

                else:
                    N=1
                success = trade('buy-low', single_date, buy, N, account, portfolio, today_state)
                if (type(success)==bool) : portfolio.log_transaction(single_date, 'buy-low', buy, N) ; print(f'BOUGHT COMPANY {buy} , {N} PIECES')
    
            
        sells = today_state[today_state['High'] > sell_threshold]
        # think of adding a penalty once you have sold to increase thresh
        for sell in sells['Stock']:  
            print("SEEEEEELLLLLLLL")
            decision = choices(a_list, probs)[0]
            if (decision=='sell'): 
                if (sell in portfolio.possessions.keys()):
                    N = floor(sell_percent * portfolio.possessions[sell][1]) 
                    if (N==0) : N = 1

                    volume = today_state[today_state['Stock'] == sell].iloc[0].at['Volume']
                    if (N > 0.1 * volume ) : 
                        N = floor(0.095 * volume)
     
                    success = trade('sell-high', single_date, sell, N, account, portfolio, today_state)
                    if (type(success)==bool) : portfolio.log_transaction(single_date, 'sell-high', sell, N)
    
    # Important parameter Updates before finishing an iteration
      
    # Storing info about net worth for every day to use on final plot.
    port_net_worth.append(portfolio.evaluation(today_state, account))
    acc_net_worth.append(account.balance)
    plot_dates.append(single_date)
                        
    # If avaliable moves have finished break loop
    if (portfolio.transactions >= max_moves):
        print('Maximum Moves Reached !')
        break
    
    # threshold parameters update
    sell_threshold = sell_threshold * s 
    buy_threshold = buy_threshold * b 


# prepend the number of moves in the txt
portfolio.log_final()

# Print some info once finished 
print('Sell thresh : ',sell_threshold)
print('Buy thresh : ',buy_threshold)
print('Final date : ', single_date)
print('Balance is ', account.balance)
print('Movements : ', portfolio.transactions)
print(portfolio.possessions)

tac = time()
print('Time ellapsed : ', round(tac-tic,3), 'seconds')


fig, ax = plt.subplots(figsize = (10,5))
ax.step(x=plot_dates, y=acc_net_worth,  where='pre', color='blue', label='Balance', alpha=1.0)
ax.step(x=plot_dates, y=port_net_worth, where='pre', color='orange', label='Portfolio')
ax.set_yscale('log')
logfmt = ticker.LogFormatterExponent(base=10.0, labelOnlyBase=True)
ax.yaxis.set_major_formatter(logfmt)
ax.set_ylabel("$10^x$")
ax.fill_between(plot_dates , acc_net_worth , color='blue', step="pre")
ax.fill_between(plot_dates , acc_net_worth, port_net_worth , color='orange', step='pre') #, acc_net_worth
# plot 1 every 500 dates
plt.xticks(plot_dates[::500], rotation=25, fontsize=6)
plt.suptitle('Portfolio and Account Net worth through time (Log Scaled)', fontsize=16)# Add title
legend = ax.legend()  # add plot legend
ax.legend(loc='upper left')
plt.show()



    
    
    

    
    