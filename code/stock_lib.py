import numpy as np 
import pandas as pd 
import os 

class Portfolio:
    def __init__(self, max_moves) -> None:
        # stocks possesed 
        self.possessions = {} ##### possessions = {stock: [today, N_t, yesterday, N_t-1]}  ######
        self.net_value = 0      # tracks the net value of the portfolio on a given date
        self.transactions = 0   # tracks number of transactions executed
        self.max_moves = max_moves  # maximum number of moves allowed 
        
        # Create a new transaction log file
        if (max_moves <= 1000):
            log = 'small.txt'
            with open(log, 'w') as the_file:
                the_file.write('')
        else:
            log = 'large.txt'
            with open(log, 'w') as the_file:
                the_file.write('')

    
    def insert(self, company, N, date):
        ''' Inserts N stocks of company 'company' inside the portfolio
            company(str) : company's stock to insert
            N(int) : number of stocks to insert '''
        if (N <= 0) or (N % 1 != 0) : return print("Rejected : Can only insert a positive integer amount of stocks in portfolio")
        if (company in self.possessions.keys()) :
            # Update possessions info
            today = self.possessions[company][0]
            Nt = self.possessions[company][1] 

            if(date != today): 
                self.possessions[company][2] = today # update last date 
               # self.possessions[company][0] = date  # update current date 
                self.possessions[company][3] = Nt    # update previous stock Holding

            self.possessions[company][0] = date   # date of transaction
            self.possessions[company][1] = N + Nt  # new stock balance
            self.transactions += 1
            return True
        # first ever entry of stock
        else : 
            # previous date N is equal to 0 and can only buy 1 stock in the first transaction.
            if (N>1) : print(f'Can not buy more than 1 stock on your first transaction for this company.')
            else : self.possessions[company] = [date, N, date, 0] 
            self.transactions += 1 
            return True
    
    def remove(self, company, N, date):
        ''' Removes N stocks of company 'company' from the portfolio
            company(str) : company's stock to insert
            N(int) : number of stocks to insert ''' 
        if (N <= 0) or (N % 1 != 0) : return print("Rejected : Can only remove a positive integer amount of stocks from portfolio")
        if (company in self.possessions.keys()) :
            # Avoid negative stock balance
            if(self.possessions[company][1] >= N):   
                # Update possessions info
                today = self.possessions[company][0]
                Nt = self.possessions[company][1] 
                if(date != today) : 
                    self.possessions[company][2] = today # update last date 
                    self.possessions[company][0] = date  # update current date 
                    self.possessions[company][3] = Nt    # update previous stock Holding
                self.possessions[company][1] =  self.possessions[company][1] - N 
                if (self.possessions[company][1] == 0 ):
                    del self.possessions[company]
                self.transactions += 1
                return True 
            else : return print(f"Portfolio contains less than {N} stocks of {company}")
        else : return print(f"No {company} stocks present in portfolio")       
    
    def log_transaction(self, date, command, company, N):
        string = date + ' ' + command + ' ' + company + ' ' + str(N) + '\n'
        if (self.max_moves <= 1000):
            with open('small.txt', 'a') as the_file:
                the_file.write(string)
        else:
            with open('large.txt', 'a') as the_file:
                the_file.write(string)
            
    def log_final(self):
        line = str(self.transactions)
        if (self.max_moves <= 1000) :
            with open('small.txt', 'r+') as f:
                content = f.read()
                f.seek(0, 0)
                f.write(line.rstrip('\r\n') + '\n' + content)
                print('LOG FINAL')
        else:
            with open('large.txt', 'r+') as f:
                content = f.read()
                f.seek(0, 0)
                f.write(line.rstrip('\r\n') + '\n' + content)
                print('LOG FINAL')           
        
    
    def evaluation(self, state_df, account):
        ''' Computes the net worth of the portfolio'''
        port_net_worth = account.balance 
        for company in self.possessions.keys():
            date = self.possessions[company][0]
            N = self.possessions[company][1]
            price, _ = get_data(company, date, 'Close', state_df)
            value_i = price * N 
            port_net_worth = port_net_worth + value_i
        return port_net_worth
            



class Account:
    def __init__(self) -> None:
        self.balance = 1 

    def deposit(self, amount):
        if (amount<=0): return print("Deposit rejected, can't deposit 0 or negative amount !")
        self.balance = self.balance + amount
        print(f'+++ Deposited {amount} into account ')
        return True 

    def withdraw(self, amount):
        if (amount<=0): return print("Please provide a positive amount above zero 0 .")
        if (self.balance >= amount):
            self.balance = self.balance - amount
            print(f'--- Withdrawed {amount} from account ')
            return True 
        else:
            return print(f"Withdrawl rejected, not enough money in account balance !")
    


def trade(code:str, date, company, N:int, account, portfolio, state_df):
    ''' Executes trades for a portfolio and an account
        code(str) : Trade code to execute ['buy-open','sell-open','buy-high','sell-low',
                                           'buy-close', 'sell-close' ]
        date(str) : Date of execution
        company(str) : The company the trade is being executed for
        N (int) :  Amount of stocks to trade
        account(class Account) : The account to transact money with
        portfolio(class Portfolio) : The portfolio to/from stocks will be added/removed '''
    
    company = company.lower()
    trade_codes = ['buy-open', 'sell-open', 'buy-low', 'sell-high', \
                   'buy-close', 'sell-close']
    if (code not in trade_codes): return print("Unsupported trade")

    price_code = code.split(sep='-')[1]
    price, volume = get_data(company, date, price_code.capitalize(), state_df)
    if (price == None) or (volume == None) : return print('Trade rejected, stock not available for the set date.')
    total_price = price * N 
    trade_code = code.split(sep='-')[0]

    
    if (trade_code == 'buy'):
        # test account has enough money available
        if (account.balance < total_price) : return print("Buy Trade rejected, not enough account balance.")
        # test buy amount is <= 0.1*volume
        if (N > 0.1*volume) : return print(r"Buy Trade rejected, N exceeds 10% of volume.")
        # test buy amount respects N <= N_{d-1} + 1 
            # first ever trade on 'company'
        if (company not in portfolio.possessions.keys()  and N>1): return print("First time Trade rejected, trade limits are not respected.")
        elif (company not in portfolio.possessions.keys()  and N==1):
            # withdraw money from account
            success = account.withdraw(total_price)
            if (type(success)!=bool): return print('Not enough money to buy stock')
            # Insert stocks to portfolio
            success = portfolio.insert(company, N, date)
            if (type(success)==bool): return True
            else: 
                account.deposit(total_price)
            return 0

        if (company in portfolio.possessions.keys() ): 
            today = portfolio.possessions[company][0]
            if (date == today) : # intra day trading
                prev_N = portfolio.possessions[company][3] # previous day holdings
                Nt = portfolio.possessions[company][1] # same day holdings
                if (N + Nt > 2 * prev_N + 1) : return print("INTRAday Trade rejected, trade limits are not respected.")
            if (date != today) : # not intra day trade
                Nt = portfolio.possessions[company][1] # same day holdings
                if (N  > Nt + 1) : return print("Sell Trade rejected, trade limits are not respected.")  
        # withdraw money from account
        success = account.withdraw(total_price)
        if (type(success)!=bool): return print('Not enough money to buy stock')
        # Insert stocks to portfolio
        success = portfolio.insert(company, N, date)
        if (type(success) == bool): return True
        else : 
            account.deposit(total_price)
        return 0

    elif (trade_code == 'sell'):
        # test portfolio contains at least 1 stock of company
        if (company not in portfolio.possessions.keys()) : return print(f'Trade rejected, {company} not present in portfolio.')
        # test portfolio posseses the requested amount of Stocks
        if (portfolio.possessions[company][1] < N): return print(f'Trade rejected, not enough {company} stock in portfolio.')
        # test sell amount is <= 0.1*volume
        if (N > 0.1*volume) : return print(f"Sell Trade rejected, trade amount N exceeds 10% of {company}'s trade volume.")
        # remove stocks from portfolio
        success = portfolio.remove(company, N, date)
        # deposit money to account  
        if (type(success)!=bool) : return print('Stock removement failed')
        success = account.deposit(total_price)
        if (type(success)==bool) : return True
        


def get_data(company, date, price_code, df):
    ''' Searches and returns the price and volume for company "company" on date "date", from the available data.
        Parameters:
            company(str) : Company stock name to search for.
            date(str) : Date to search for
            price_code(str) : Search and return one of (Open,High,Low,Close) prices.

        Returns:
            price(int) : The "price_code" price of "company" furing "date".
            volume (int) : The volume traded during "date" for "company".
    '''
  
    info = df.iloc[0]
    price = info.at[price_code]
    volume = info.at['Volume']

    return price, volume





