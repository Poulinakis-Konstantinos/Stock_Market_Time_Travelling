
# Stock_Market_Time_Travelling, a stock-market simulation. 
Imagine you managed to time travel back to 1960 's Wall Street and you've got stock market data with you!
What are you going to buy ? How will you become a billionare at last ?

I've got the answer for you and you can verify it too with this Python simulation. Your grand-grand-grand children will thank you !

![alt text](https://github.com/Poulinakis-Konstantinos/Stock_Market_Time_Travelling/blob/main/results/small_value_graph.png)

### You have this *[financial dataset](https://www.kaggle.com/borismarjanovic/price-volume-data-for-all-us-stocks-etfs/version/3)* with you.
We will use this in order to analyze and pick our stocks. We also use it to run the stock market simulation.

### Rules : Unfortunately, since we have time travelled, we need to respect the following rules in order to keep space-time safe!
 - Can only buy/sell up to 10% of a stock's volume in any given day.
 - If during day T-1 you have N stocks of company ABC then you can only buy up to N+1 stocks of ABC during day T.
 - Since we don't have information if Hight price or Low price  happened first , we can only execute the following orders for Intraday trading
 [(buy-open, sell-high), (buy-open, sell-close), (buy-high, sell-close), (sell-open, buy-low),(sell-open, buy-close), (sell-high, buy-close) ]
 <sup>(do not try other combinations eg. (buy-low, sell-high) historical data shows you lose money in the long run ;P)<sup>


### File description
- code :
    - stock_lib.py  : is **the backbone of this repo**, it contains all the neccessary classes and functions to run the simulation.
    - time_travel.py : is the **main loop of the simulation that also executes our strategy**.
    - time_travel_large.py  : just like time_travel.py  but with a sligtly different strategy since we can use up to 1 Million moves.
    - stock_analysis.ipynb  : a notebook used to discover stocks that would fit our strategy.
- results :
    - report.pdf :  A report providing a brief explanation of the code and a detailed explanation of the strategy. (Currently in Greek, English to be uploaded).
    - small.txt : A txt containing the sequence of trades we executed ( small is limited to 1000 moves).
    - large.txt : A txt containing the large sequence of trades we executed (up to 1 million).
