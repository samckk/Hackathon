# Import packages and data
import alphien 
from alphien.data import *
import heapq
import random
import pandas as pd

def equalWeightsSP500Select(features):
        
    # Get the inclusion matrix
    inclusionMatrix = getTickersSP500(ticker=features.tickers, startDate=features.startDate, endDate=features.endDate, asMatrix=True)
    
    # Create dataframe with tickers as columns
    px = features.subset(fields='bb_live', asDataFeatures=True)    
    selection = inclusionMatrix.copy()
    selection.iloc[:, :] = 0.0 #initialise
    rebalDates = inclusionMatrix.index[~(inclusionMatrix == inclusionMatrix.shift(1)).all(axis=1)].tolist()
    selection = selection.reindex(index=rebalDates)
    save = selection.iloc[0,:]
    
    # Loop through the rebalance dates
    for date in rebalDates:
        
        # If stock in portfolio no longer in S&P
        if (save * inclusionMatrix.loc[date,:]).sum() != 1:
            
            gics = getGICSDescription()
            sectors = gics.sector.unique()
            numofstock = []

            # Find out the number of stocks required for each sector
            for i in sectors:
                fins = gics[gics.sector==i].industry.unique().tolist()
                # For robustness
                tkr = getTickersSP500(ticker=features.tickers, industry=fins, zoom=str(date)).ticker.unique().tolist()
                numofstock.append(len(tkr))

            newnumofstock = [int(i / sum(numofstock) * 50) for i in numofstock]

            if sum(newnumofstock) != 50:
                for i in heapq.nlargest(50-sum(newnumofstock), range(len(newnumofstock)), newnumofstock.__getitem__):
                    newnumofstock[i] += 1

            includedAtDate = (inclusionMatrix.loc[date,:]>0.0).values

            # Add the stock into the portfolio if chosen
            for i, d in enumerate(sectors):
                fins = gics[gics.sector==d].industry.unique().tolist()
                tkr = getTickersSP500(ticker=features.tickers, industry=fins, zoom=str(date)).ticker.unique().tolist()
                tkr = [tk for tk, incl in zip(tkr, includedAtDate) if incl]
                random.seed(10)
                random.shuffle(tkr)
                selected = tkr[:newnumofstock[i]]
                selection.loc[date,selected] = 0.02

            save = selection.loc[date,selected]
                
    selection = selection[selection.sum(axis=1) == 1]
    
    return selection
