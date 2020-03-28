# -*- coding: utf-8 -*-
"""implied_volatility_calculator.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ZNLKHqjumm9gGnwE5vu0j1AzcWlLOxUC
"""


import csv
import scipy.stats as si
from math import log,sqrt,exp,pi

class DataReader:
  def __init__(self,file_name):
    self.file_name = str(file_name)
  
  def instantiate_trades(self):
    list_of_trades = []
    with open(self.file_name,'r') as csv_file:
      csv_reader = csv.reader(csv_file)

      #skip the first row as it contains the headings
      next(csv_reader)

      for row in csv_reader:
        
        each_trade = Trade(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8])
        list_of_trades.append(each_trade)

      return list_of_trades

class Trade:
  def __init__(self,trade_id,underlying_type,underlying,r,T,K,option_type,model_type,market_price):
        self.trade_id = trade_id
        self.underlying_type = underlying_type
        self.underlying = float(underlying) 
        self.K=float(K)
        self.T= float(T)/365
        self.r = float (r)
        self.option_type = option_type
        self.model_type=model_type
        self.market_price = float(market_price)

class Model:

  @staticmethod
  def black_scholes(Trade,sigma):
      S, K, r, T,option_type = Trade.underlying, Trade.K, Trade.r,Trade.T,Trade.option_type

      d1 = (log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrt(T))
      d2 = d1 - sigma * sqrt(T)


      if option_type == 'Put':
        bs_price = K * exp(-r * T) * si.norm.cdf(-d2) -S * si.norm.cdf(-d1)  
     
      if option_type=='Call':
        bs_price = S * si.norm.cdf(d1) - K * exp(-r * T) * si.norm.cdf(d2)
      
      return bs_price

  @staticmethod
  def bachelier(Trade,sigma):
      S, K, r, T,option_type = Trade.underlying, Trade.K, Trade.r,Trade.T,Trade.option_type
      d1  = (S-K)/(sigma*sqrt(T))

      if option_type == 'Call':
        ba_price =   ((S - K)*si.norm.cdf(d1) + sigma*sqrt(T)*si.norm.pdf(d1))*exp(-r*T)
      
      if option_type == 'Put':
        ba_price = ((K-S)*si.norm.cdf(-d1) + sigma*sqrt(T)*si.norm.pdf(d1)) * exp(-r*T)
      
      return ba_price

class NewtonSolver: 
   
  @staticmethod
  def calculate_volatility(Trade):
    #note here that the parameter vol is the initial guess for volatility

      S, K, r,T, C = Trade.underlying, Trade.K, Trade.r,  Trade.T, Trade.market_price
      
      #Use Brenner Subrahmanyam (1988) approximation for initial guess of volatility
      vol = (C/S) * sqrt ( 2*pi / T)


        

      if Trade.model_type== "BlackScholes": 
        d1 = (log(S / K) + (r + 0.5 * vol ** 2) * T) / (vol * sqrt(T))
      elif Trade.model_type== "Bachelier": 
         d1  = (S-K)/(vol*sqrt(T))

      #tolerances
      tolerance = 1e-8
      epsilon =1

      count =0
      max_iteration = 1000
      

      while epsilon > tolerance:
        count+=1
        if count>= max_iteration:
          print('breaking on count')
          return

        initial_vol = vol

        #funtion_value is the funtion we are finding the root of
         
        if Trade.model_type == "BlackScholes":   
            

            theoretical_price = Model.black_scholes(Trade,vol)
          
        if Trade.model_type == "Bachelier":
          
            theoretical_price = Model.bachelier(Trade,vol)
            
        function_value = theoretical_price -C

        #vega is derivative of the option price wrt to sigma(implied_volatility)
        vega = S*si.norm.pdf(d1)*sqrt(T)

        vol = vol -function_value/vega  

        epsilon = abs((vol-initial_vol)/initial_vol)
       
        vega = (1 / sqrt(2 * pi)) * S * sqrt(T) * exp(-(si.norm.cdf(d1) ** 2) * 0.5)
      
   
      return vol

class OutputWriter:

    @staticmethod
    def write_output_file(trades_list,file_name):
      
      with open(str(file_name),'w',newline='') as new_file:
        csv_writer=csv.writer(new_file)
        
        csv_writer.writerow(['ID', 'Spot', 'Strike', 'Risk-Free Rate', 'Years to Expiry', 
                    'Option Type', 'Model Type', 'Implied Volatility', 'Market Price'])
        
        for trade in trades_list:
          
          
          implied_volatility = NewtonSolver.calculate_volatility(trade)
          csv_writer.writerow([trade.trade_id,trade.underlying,trade.K,trade.r,trade.T,trade.option_type,trade.model_type,implied_volatility,trade.market_price])

class IVCRunner:

  @staticmethod
  def run_program():
    dr = DataReader("input.csv")
   
    trades_list  = dr.instantiate_trades()
   
    OutputWriter.write_output_file(trades_list[0:100],'volatilities.csv')


if __name__ =="__main__":
  IVCRunner.run_program()

dr1 = DataReader("input.csv")
data = dr1.instantiate_trades()[0]

NewtonSolver.calculate_volatility(data)

'''t = Model.bachelier(data,1.01)
y = Model.black_scholes(data,1.01)'''