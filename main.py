import csv
from datetime import date, datetime, timedelta
from multiprocessing import Pool
from decimal import Decimal
import multiprocessing
import pickle
import pathlib
import os

from dataTypes import *
from simulation import *
import hypothesis




class HypothesisTesterStupid:
    def __init__(self, startingDate, shortTermWindow, endingDate, shortTermData, longTermData, startingCash):
        self.startingDate = startingDate
        self.shortTermWindow = shortTermWindow
        self.endingDate = endingDate
        self.shortTermData = shortTermData
        self.longTermData = longTermData
        self.startingCash = startingCash

    def testHypothesis(self, hypothesis):
        assert callable(hypothesis)
        return simulation(self.startingDate, self.shortTermWindow, self.endingDate, self.shortTermData, self.longTermData, hypothesis, self.startingCash)["success"]

def DataFrame(data):
    
    #short = pd.DataFrame([val.__dict__ for val in data['short']]).dropna()
    long = pd.DataFrame([val.__dict__ for val in data['long']]).dropna()
    #plt.plot_date(short.date,short.safeMeanPrice, linestyle='solid', marker='')
        
    #check for linearity with scatter plots
    
    
    #create additional data
    def signMomentum(sign):
        momentum = []
        mom = 0
        LastSignPositive = True
        for index, sign in enumerate(sign):
            if sign == 0: #concern, we should probably count very small differences as 0 instead of increasing momentum
                mom = 0
            if sign == 1:
                if LastSignPositive == True:
                    mom += 1
                else:
                    mom = 1
                LastSignPositive = True
            if sign == -1:
                if LastSignPositive == True:
                    mom = -1
                else:
                    mom -= 1
                LastSignPositive = False
            if np.isnan(sign):
                momentum.append(np.nan)
            else:
                momentum.append(mom)
        return momentum
    long['deltaPrice1Row'] = long['price'].diff()
    long['deltaPrice5Row'] = long['price'].diff(periods=5)
    #long['deltaPrice500Row'] = long['safeMeanPrice'].diff(periods=500)
    #^^ if you graph all of these with the above scatter, you will find linearity starting to increase at >100 rows ^^ which makes some sense
    
    
    long['deltaSign1Row'] = np.sign(long['deltaPrice1Row'])
    long['signMomentum1Row'] = signMomentum(long['deltaSign1Row'])
    #long['deltaSign500Row'] = np.sign(long['deltaPrice500Row'])
    #long['signMomentum500Row'] = signMomentum(long['deltaSign500Row'])
    long['std5Row'] = long['price'].rolling(5).std()
    long['std100Row'] = long['price'].rolling(100).std()
    long['volume5Row'] = long['volume'].rolling(5).sum()
    #long['volume500Row'] = long['volume'].rolling(500).sum()
    
    long['movingAverage5'] = long['price'].rolling(5).sum()/5
    long['movingAverage50'] = long['price'].rolling(50).sum()/50
    #long['movingAverage500'] = long['safeMeanPrice'].rolling(500).sum()/500
    # plt.scatter(short.deltaPrice500Row, short.safeMeanPrice)
    # plt.scatter(short.signMomentum1Row, short.safeMeanPrice)
    
    
    # linear-ish combos: std5row, safemeanprice
    # signmomentum500row, deltaprice500row -- also on log scale
    # signmomentum500row * volume500Row, deltaprice500row
    
    
    
    with pd.ExcelWriter('btcusdlongtest.xlsx') as writer:  
        #short.to_excel(writer, sheet_name='short')
        long.to_excel(writer, sheet_name='long')


    return long#,long



def main():
    THREAD_COUNT = os.cpu_count()
    print("I have {} cores".format(THREAD_COUNT))
    FILENAME = "XBTUSD.csv"
    # print(hypothesisTester(FILENAME, hypothesis.equationMethod))
    

    startingDate = datetime(year=2017, month=1, day=1, hour=0, minute=0, second=0)
    endingDate = datetime(year=2021, month=12, day=31)
    shortTermWindow = timedelta(hours=1)
    longTermWindow = timedelta(hours=24)

    import time
    start = time.time()
    data = getData(FILENAME, startingDate, endingDate, shortTermWindow, longTermWindow)
    shortdf = DataFrame(data) #,longdf
    print("Took {} seconds".format(time.time() - start))
    # for x in longTerm:
    #     print("L RANGE:", x.date, " - ", x.endDate)
    # # for x in shortTerm:
    # #     print("S RANGE:", x.date, " - ", x.endDate)

    result = simulation(startingDate, shortTermWindow, endingDate, data["short"], data["long"], hypothesis.equationMethod, Decimal(1_000))
    # print("{}% success".format(result["success"]))    
    simulationPlotter(data["long"], result)
    # print(hypothesisTester(FILENAME, hypothesis.hold))

    # hypothesisTester = HypothesisTester(startingDate, shortTermWindow, endingDate, data["short"], data["long"], Decimal(1_000)).testHypothesis

    # inputList = np.arange(.05, 3, .05)
    # hypothesisList = [hypothesis.HypothesisVariation(hypothesis.bollingerBandsSafe, bollinger_number_of_stdev=i).hypothesis for i in inputList]

    # pool = multiprocessing.Pool(THREAD_COUNT)
    # results = pool.map(hypothesisTester, hypothesisList)
    # associatedDict = {}
    # for i in range(len(results)):
    #     associatedDict[inputList[i]] = results[i]

    #     print("Stdev {} : {}% profit".format(inputList[i], results[i]))
    
    # bestResult = max(results)
    # bestResultIndex = results.index(bestResult)
    # print("Best: {} : {}% profit".format(inputList[bestResultIndex], results[bestResultIndex]))

    
if __name__ == "__main__":
    main()
    

