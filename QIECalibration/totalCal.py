#!/usr/bin/env python

import sqlite3
from pprint import pprint
import glob
import os
import sys
from utils import Quiet

def totalCal(inFile):
    import ROOT as root

    plotBoundaries_slope = [0.27,0.36]
    plotBoundaries_offset = [1,16,100,900]

    shuntList = [1,1.5,2,3,4,5,6,7,8,9,10,11,11.5]
    rangeList = [0,1,2,3]

    # Create output directory if it doesn't exist
    if not os.path.exists("calSummary/"):
        os.makedirs("calSummary/")

    # Create root file
    rootout = root.TFile("calSummary/calSummary.root","recreate")

    # Initialize histograms
    slopeHist = {}
    offsetHist = {}

    for r in rangeList:
        if r not in slopeHist:
            slopeHist[r] = {}
        if r not in offsetHist:
            offsetHist[r] = {}
        for sh in shuntList:
            if r > 1 and sh != 1:
                continue
            slopeHist[r][sh] = root.TH1F("SLOPE_Sh_%s_R_%i"%(str(sh).replace(".",""),r),"Slope Shunt %.1f - Range %i"%(sh,r),100,plotBoundaries_slope[0]/sh,plotBoundaries_slope[1]/sh)
            slopeHist[r][sh].GetXaxis().SetTitle("Slope")
            slopeHist[r][sh].GetYaxis().SetTitle("Frequency")

            offsetHist[r][sh] = root.TH1F("OFFSET_Sh_%s_R_%i"%(str(sh).replace(".",""),r),"Offset Shunt %.1f - Range %i"%(sh,r),100,-1*plotBoundaries_offset[r],plotBoundaries_offset[r])
            offsetHist[r][sh].GetXaxis().SetTitle("Offset")
            offsetHist[r][sh].GetYaxis().SetTitle("Frequency")


    # Read input file
    with open(inFile) as f:
        files = [line.strip() for line in f]
    for i_file in files:

        # Open db file and start cursor
        dbFile = sqlite3.connect(i_file)
        cursor = dbFile.cursor()

        # Get list of values. gets qie, capID, range, and shunt in order to assure each slope and offset are unique and to determine which histogram each pair belongs to.
        # Only accesses database one time to reduce execution time
        values = cursor.execute("select slope, offset,qie,capID,range,shunt from qieshuntparams as p").fetchall()
        for val in values:
            slope,offset,qie,capID,r,sh = val
            slopeHist[r][sh].Fill(slope)
            offsetHist[r][sh].Fill(offset)

    for r in rangeList:
        for sh in shuntList:
            if r > 1 and sh != 1:
                continue
            slopeHist[r][sh].Write()
            offsetHist[r][sh].Write()
    rootout.Close()

if __name__ == '__main__':
    totalCal(sys.argv[1])
