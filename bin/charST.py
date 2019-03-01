# -*- coding: utf-8 -*-
#encoding: utf-8

# Copyright 2019 Juergen Maier

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# author: Juergen Maier
# mail: juergen.maier@tuwien.ac.at
#********************************************************************************#

import sys
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import subprocess
import numpy as np
import time

FIG_FOLDER='../figures/'
SPICE_FOLDER='../hspice/'
DATA_FOLDER='../data/'
CIRCUIT_FOLDER='../circuits/'
TECH_FOLDER='../technologies/'
DIR_NAME=''
SPICE_COMMAND='hspice'

DVOUT_COUNT_VIN=100 # how many different input voltage values to use
DVOUT_COUNT_VOUT=100 # how many different output voltage values to use
HYSTERESIS_COUNT_MULT=1 # multiplicative factor how many more input voltage values
   # to use during the hysteresis

#********************************************************************************

def split_str(seq, length):
    return [float(seq[i:i+length]) for i in range(0, len(seq), length)]

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def print_info(msg):
    print('[INFO]: ' + msg)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def print_error(msg):
    print('[ERROR]: ' + msg)
  
#********************************************************************************

def read_hspice (filename, varCnt):

    data=[]

    for i in range(varCnt):
        data.append([])

    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # cut first lines, unfortunately not fixed amount, so try splitting on first,
    # if exception thrown remove line
    while(1):
        try:
            fieldCount = lines[0][:-1].count(".")
            fieldLength=len(lines[0][:-1])/fieldCount
            elements = split_str(lines[0][:-1],fieldLength)
            break
        except:
            lines=lines[1:]

    index=0

    # seperate values in file and move them to their corresponding arrays
    for i in lines:
        fieldCount = i.count(".")
        fieldLength=len(i[:-1])/fieldCount
        elements = split_str(i[:-1],fieldLength)
    
        for k in elements:
            data[index].append(k)
            index = ((index+1)%varCnt)

    minLen = len(data[0])

    # determine length of shortest array
    for i in range(varCnt):
        if (len(data[i]) < minLen):
            minLen = len(data[i])

    # set each array to same length
    for i in range(varCnt):
        data[i] = data[i][:minLen]

    return data

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def read_hspice_2D (filename):

    data=[ [], [], [] ]

    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # cut first lines, unfortunately not fixed amount, so try splitting on first,
    # if exception thrown remove line
    while(1):
        try:
            fieldCount = lines[0][:-1].count(".")
            fieldLength=len(lines[0][:-1])/fieldCount
            elements = split_str(lines[0][:-1],fieldLength)
            break
        except:
            lines=lines[1:]

    index=0

    newLine = True
    firstLine = True
    
    # seperate values in file and move them to their corresponding arrays
    tmpData = []
    for i in lines:
        fieldCount = i.count(".")
        fieldLength=len(i[:-1])/fieldCount
        elements = split_str(i[:-1],fieldLength)

        for k in elements:
            if newLine :
                newLine = False
                data[1] = [k] + data[1]
                idx=0
                continue
                
            if k > 0.1e30:
                newLine = True
                data[2] = [tmpData] + data[2]
                tmpData = []

                if firstLine == True:
                    firstLine = False
                continue

            if (idx == 0) and (firstLine == True):
                data[0].append(k)

            if (idx == 1):
                tmpData.append(k)
            idx= 1-idx

    return data

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def read_csv_2D(fileName):

    f = open(fileName,'r')


    # read first line (description)
    f.readline()
    data = []

    # read x and y vectors
    for i in range(2):
        data.append([float(j) for j in f.readline().split(';')])

    tmpMatrix = []

    # read values
    for line in f.readlines():
        tmpMatrix.append([float(j) for j in line.split(';')])

    data.append(np.matrix(tmpMatrix))

    f.close()
    
    return data

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def read_csv(fileName):

    data = []
    
    with open(fileName,'r') as f:

        # read values
        for line in f.readlines()[1:]:
            data.append([float(j) for j in line.split(';')])

    return data

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def write_csv_2D(data, name):

    fileName = DATA_FOLDER + DIR_NAME + name + '.csv'
    print_info("writing 2D data to %s"%fileName)
    
    with open(fileName,'w') as f:
        f.write("line 1: x-axis (Vin); line 2: y-axis (Vout); following lines: " \
                "dVout-matrix, each line is one Vout value, starting with highest Vout\n")

        text = ''
        for i in data[0]:
            text += '%s;'%i
        text = text[:-1] +'\n'
        f.write(text)

        text = ''
        for i in data[1]:
            text += '%s;'%i
        text = text[:-1] +'\n'
        f.write(text)

        for line in data[2]:
            text = ''
            for entry in line:
                text += '%s;'%entry
            text = text[:-1] +'\n'
            f.write(text)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def write_csv_row(fileName, data, header):

    print_info("writing data to %s"%fileName)
    
    with open(fileName,'w') as f:

        f.write(header)
        text = ''
        
        for entry in data:
            for i in entry:
                text += '%s;'%i

            f.write(text[:-1])
            text = '\n'

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def write_csv_column(fileName, data, header):

    print_info("writing data to %s"%fileName)
    
    with open(fileName,'w') as f:

        f.write(header)
        text = ''
        
        for idx in range(len(data[0])):
            for i in range(len(data)):
                text += '%s;'%data[i][idx]

            f.write(text[:-1])
            text = '\n'
            
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def row_to_column(data):

    result = []
    for i in range(len(data)):
        result.append([])
    
    for entry in data:
        for idx in range(len(entry)):
            result[idx].append(entry[idx])

    return result

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def column_to_row(data):

    result = []
    
    for idx in range(len(data[0])):
        tmp = []
        for j in range(len(data)):
            tmp.append(data[idx][j])
        result.append(tmp)

    return result

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
def read_dVout(fileName):
    
    if not os.path.isfile(fileName):
        get_dVout(circuit)

    return(read_csv_2D(fileName))

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
def read_meta(fileName):
    
    if not os.path.isfile(fileName):
        get_meta(circuit)

    return(read_csv(fileName))

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def do_trans_tau(vin, vout, dVout, compare=False):
   
#    print_info("starting do_trans_tau for vout=%s"%(vout))
    
    fileName = CIRCUIT_FOLDER + circuit + '/trans.sp'
    
    stringVin = ("%.7f"%vin).replace('.','')
    stringVout = ("%.7f"%vout).replace('.','')    
    
    spiceFileName = SPICE_FOLDER + DIR_NAME + 'trans_%s_%s.sp'%(stringVin, stringVout)

    if not os.path.isfile(spiceFileName[:-3]+'.tr0'):
        cmd = "sed -e 's/<sed>in<sed>/%s/' -e 's/<sed>out<sed>/%s/' -e 's/<sed>time<sed>/%s/' "\
                %(vin, vout, 200) + fileName  + " > "  + spiceFileName
        code = subprocess.call(cmd,shell = True ,  stderr=subprocess.STDOUT)

        if (code != 0):
            print_error("sed failed")
            return

        cmd = "hspice -i %s -o %s >> hspice_log 2>&1"%(spiceFileName[:-3], spiceFileName[:-3])
        code = subprocess.call(cmd,shell = True ,  stderr=subprocess.STDOUT)

        if (code != 0):
            print_error("hspice failed")
            return

    #-----------------------------------------------------------------
    # the start has to be cut as derivative changes overproportional there
    
    data = read_hspice(spiceFileName[:-3]+'.tr0',3)

    startIdx= len(data[2])/10
    dVoutTrace = data[2][startIdx:]
    timeTrace = data[0][startIdx:]
    
    logDVoutTrace = [np.log(abs(j)) for j in dVoutTrace]
    maxIdx = logDVoutTrace.index(max(logDVoutTrace))

    if maxIdx == 0:
        return[-1,0]
    polyParams = np.polyfit(timeTrace[:maxIdx],logDVoutTrace[:maxIdx],1)
    
    ootau = polyParams[0]
    idx = maxIdx/2

    # see documentation for more details on that expression
    t0 = (logDVoutTrace[idx] - np.log(ootau))/ootau

    if (data[1][-1] > data[1][0]):
        Vm = data[1][idx]- np.exp(t0*ootau)
    else:
        Vm = data[1][idx]+ np.exp(t0*ootau)

    #-----------------------------------------------------------------
    # calculate static dVout fitted to start of dynamic one and plot curve
    
    if compare:

        if (data[1][-1] > data[1][0]):
            up = True
        else:
            up = False

        staticDeriv = [ [0], [np.log(abs(data[2][1]))] ]
        scaleFactor = data[2][1] / dVout[1][0]
        dVoutIdx = 1

        idx = 0
        while True:

            if (idx >= len(data[1])):
                break

            if up :
                while (dVout[0][dVoutIdx] > data[1][idx]):
                    idx += 1

                    if (idx > len(data[1])-1):
                        break
            else:
                while (dVout[0][dVoutIdx] < data[1][idx]):
                    idx += 1

                    if (idx > len(data[1])-1):
                        break

            if (idx >= len(data[1])):
                break

            staticDeriv[0].append(data[0][idx])
            staticDeriv[1].append(np.log(abs(dVout[1][dVoutIdx]*scaleFactor)))
            dVoutIdx += 1

            if dVoutIdx == len(dVout[0]):
                break


        p1 = np.poly1d(polyParams)
        tmpY = [p1(i) for i in timeTrace[:maxIdx]]

        plt.figure()
        plt.plot(timeTrace, logDVoutTrace, 'b-')
        plt.plot(timeTrace[:maxIdx], tmpY, 'r-')
        plt.plot(staticDeriv[0], staticDeriv[1], 'g*')
        plt.grid()
        plt.savefig(FIG_FOLDER + DIR_NAME[:-1] + '_trans_%s_%s.png'%(stringVin, stringVout))

    #-----------------------------------------------------------------
    
    return [Vm, ootau]

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def get_crossing (V1, slope1, V2, slope2):
    return ((slope1*V1+slope2*V2)/(slope1+slope2))
        
#********************************************************************************
# return combination of both stable and metastable values

def get_meta(name):

    print_info("starting determination of metastable line")

    [vths, limits, hystData] = get_hysteresis(name)
               
    vinVals = hystData[0][0]
    metaLine = get_meta_line(name, vths, vinVals[len(vinVals)-limits[1]-1:limits[0]+1])
               
    #-----------------------------------------------------------------
    # export metastable data per Vin

    idx0=0
    idx1=len(hystData[1][0])-1
    metaData = [ [len(vinVals)-limits[1], limits[0]] ]

    for vin in vinVals:
        entry = [vin]

        if idx1 <= limits[1]:
            entry.append(hystData[1][1][idx1])

        if (idx0 >= len(vinVals)-limits[1]-1) and idx0 < limits[0]+1:
            entry.append(metaLine[1][idx0-(len(vinVals)-limits[1]-1)])

        if idx0 <= limits[0]:
            entry.append(hystData[0][1][idx0])

        idx0 +=1
        idx1 -=1
        metaData.append(entry)

    write_csv_row(DATA_FOLDER + DIR_NAME + 'meta.csv', metaData,
                 'vin;vout[;vout;vout]\n')
    
    #-----------------------------------------------------------------
    # plot and export (meta-)stable line
    
    metaCurve = [ [], [] ]
    
    for idx in range(limits[0]):
        metaCurve[0].append(hystData[0][0][idx])
        metaCurve[1].append(hystData[0][1][idx])

    for idx in range(len(metaLine[0])-1,-1,-1):
        metaCurve[0].append(metaLine[0][idx])
        metaCurve[1].append(metaLine[1][idx])        
        
    for idx in range(limits[1], -1, -1):
        metaCurve[0].append(hystData[1][0][idx])
        metaCurve[1].append(hystData[1][1][idx])

    maxVal = max(metaCurve[1])
        
    upperLimit = len(metaCurve[0])- limits[1] -1
    plt.figure()
    plt.plot(metaCurve[0][:limits[0]], metaCurve[1][:limits[0]], 'b')
    plt.plot(metaCurve[0][limits[0]-1:upperLimit], metaCurve[1][limits[0]-1:upperLimit], 'g')
    plt.plot(metaCurve[0][upperLimit-1:], metaCurve[1][upperLimit-1:], 'b')
    plt.grid()
    plt.ylim([-0.1,maxVal*1.1])
    plt.xlabel('Vin')
    plt.ylabel('Vout')
    plt.savefig(FIG_FOLDER+DIR_NAME[:-1]+'_meta.png')

    write_csv_column(DATA_FOLDER + DIR_NAME + 'meta_line.csv', metaCurve,
                 'vin;vout\n')
              
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# delivers data for hysteresis, i.e., all the truly stable states

def get_hysteresis(name):

    start_time = time.time()
    
    params = [ ['hyst_up.sp', '0', 'supp'], ['hyst_down.sp', 'supp', '0'] ]
    
    fileName = CIRCUIT_FOLDER + name + '/hyst.sp'
    hystData = []
    limits = []
    vths = [[],[]]

    tolerance = 0.3
    
    for data in params:
        spiceFileName = SPICE_FOLDER+DIR_NAME+ data[0]

        if not os.path.isfile(spiceFileName[:-3]+'.sw0'):
        
            cmd = "sed -e 's/<sed>start<sed>/%s/' -e 's/<sed>stop<sed>/%s/' -e 's/<sed>steps<sed>/%s/' "\
                %(data[1],data[2], HYSTERESIS_COUNT_MULT*DVOUT_COUNT_VIN) + fileName  + " > "  + spiceFileName
            code = subprocess.call(cmd,shell = True ,  stderr=subprocess.STDOUT)

            if (code != 0):
                print_error("sed failed")
                return

            cmd = "hspice -i %s -o %s >> hspice_log 2>&1"%(spiceFileName[:-3], spiceFileName[:-3])
            code = subprocess.call(cmd,shell = True ,  stderr=subprocess.STDOUT)

            if (code != 0):
                print_error("hspice failed")
                return

        data = read_hspice(spiceFileName[:-3]+'.sw0',2)

        # search first point where a jump is observed (at threshold)
        limit = -1
        for idx in range(1,len(data[1])):
            if abs(data[1][idx] - data[1][idx-1]) > tolerance:
                vths[0].append(data[0][idx-1])
                vths[1].append(data[1][idx-1])
                limit = idx-1
                break

        limits.append(limit)
        hystData.append(data)

    print_info("get_hysteresis took %s seconds"%(time.time()-start_time))
        
    maxVal = max(max(hystData[0][1]), max(hystData[1][1]))
        
    plt.figure()
    plt.plot(hystData[0][0], hystData[0][1], 'b-')
    plt.plot(hystData[1][0], hystData[1][1], 'b-')
    plt.grid()
    plt.ylim([-0.1,maxVal*1.1])
    plt.xlim([0,maxVal])
    plt.xlabel('Vin')
    plt.ylabel('Vout')
    plt.savefig(FIG_FOLDER+DIR_NAME[:-1]+'_hyst.png')
        
    print_info("threshold voltages are:")
    print(vths)
    return [vths, limits, hystData]

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# delivers the metastable states in between the hysteresis

def get_meta_line(name, vths, metaVin):

    print_info('starting to get metastable line')
    print_info('%s simulations required for that'%len(metaVin))

    start_time = time.time()
    
    fileName = CIRCUIT_FOLDER + name + '/meta.sp'
    metaData = [[],[]]
    
    voutVL=min(vths[1])*(1+1e-3)
    voutVH=max(vths[1])*(1-1e-3)

    counter =0
    
    for vin in metaVin:
        spiceFileName = SPICE_FOLDER+DIR_NAME+'meta_%s.sp'%(str(vin).replace('.',''))
        
        if not os.path.isfile(spiceFileName[:-3]+'.lis'):        

            cmd = "sed -e 's/<sed>vin<sed>/%sV/' -e 's/<sed>voutVL<sed>/%sV/' " \
                "-e 's/<sed>voutVH<sed>/%sV/' "%(vin, voutVL, voutVH)\
                + fileName  + " > "  + spiceFileName
            code = subprocess.call(cmd,shell = True ,  stderr=subprocess.STDOUT)

            if (code != 0):
                print_error("sed failed")
                return
        
            cmd = "hspice -i %s -o %s >> hspice_log 2>&1 "%(spiceFileName[:-3], spiceFileName[:-3])
            code = subprocess.call(cmd,shell = True ,  stderr=subprocess.STDOUT)

            if (code != 0):
                print_error("hspice failed")
                return
        
        cmd = "grep \".param outval\" %s.lis | awk '{print $4}'"%(spiceFileName[:-3])
        code = subprocess.Popen(cmd,shell = True ,  stdout=subprocess.PIPE)

        metaData[0].append(vin)
        metaData[1].append(float(code.stdout.read()))

        if (counter % 10) == 0:
            print_info("finished %s/%s simulations"%(counter,len(metaVin)))
        
        counter +=1

    print_info("get_meta_line took %s seconds"%(time.time()-start_time))
        
    return metaData

#********************************************************************************
# generate a map that displays the output derivative over the input-output
# voltage plane

def get_dVout_dt(name):
    print_info("generating dVout_dt over Vin-Vout plane")

    start_time = time.time()
    
    fileName = CIRCUIT_FOLDER + name + '/dVout_dt.sp'

    spiceFileName = SPICE_FOLDER+DIR_NAME+'dVout_dt.sp'
    cmd = "sed -e 's/<sed>stepsVout<sed>/%s/' -e 's/<sed>stepsVin<sed>/%s/' "\
            %(DVOUT_COUNT_VOUT+1, DVOUT_COUNT_VIN) + fileName  + " > "  + spiceFileName
    code = subprocess.call(cmd,shell = True ,  stderr=subprocess.STDOUT)

    if (code != 0):
        print_error("sed failed")
        return

    if not os.path.isfile(spiceFileName[:-3]+'.sw0'):
        cmd = "hspice -i %s -o %s >> hspice_log 2>&1"%(spiceFileName[:-3], spiceFileName[:-3])
        code = subprocess.call(cmd,shell = True ,  stderr=subprocess.STDOUT)

        if (code != 0):
            print_error("hspice failed")
            return

    print_info("get_dVout took %s seconds"%(time.time()-start_time))
        
    data = read_hspice_2D(spiceFileName[:-3]+'.sw0')

    write_csv_2D(data, 'dVout_dt')

    print_info("starting generation of matlab file")
    cmd = "matlab -r 'plot_dVout_dt '%s' '%s'; quit' -nodisplay"\
            %(DATA_FOLDER + DIR_NAME, FIG_FOLDER + DIR_NAME[:-1] + '_')
    code = subprocess.call(cmd,shell = True ,  stderr=subprocess.STDOUT)

    if (code != 0):
        print_error("matlab failed")
        return
   
    print_info("finished plotting figures")

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# calculate metastable voltage by using data from the dVout_dt map

def get_meta_dVout_dt(circuit):
    
    print_info("starting analytic calculation of metastable voltages based on dVout map")
    
    slopeFittingCount = 3
    slopeSkipEnd = 2
    
    dVout = read_dVout(DATA_FOLDER + DIR_NAME + 'dVout_dt.csv')
    meta = read_meta(DATA_FOLDER + DIR_NAME + 'meta.csv')

    start_time = time.time()
    
    #-----------------------------------------------------------------
    
    # get lower value of metastable region
    limits = [int(i) for i in meta[0]]
    meta = meta[1:]

    dVoutColIdx = 0
    while dVout[0][dVoutColIdx] < meta[limits[0]][0]:
        dVoutColIdx += 1
    dVoutColIdx += 1

    #-----------------------------------------------------------------
    
    oneOverTau = [ [], [], [] ]
    metaPoints = [ [], [], [], [] ]
    
    while dVout[0][dVoutColIdx] < meta[limits[1]][0]:

        # stable value not exactly at 0V, therefore lowermost row has
        # derivative > 0, so skip it
        dVoutRowIdx = len(dVout[1])-1
        while (dVout[2][dVoutRowIdx,dVoutColIdx] > 0) :
            dVoutRowIdx -= 1

        # go upwards until metastable value crossed
        while (dVout[2][dVoutRowIdx,dVoutColIdx] < 0) :
            dVoutRowIdx -= 1

        oneOverTau[0].append(dVout[0][dVoutColIdx])

        if dVoutRowIdx < len(dVout[1])-slopeFittingCount - slopeSkipEnd -1:
            
            polyParams = np.polyfit(dVout[1][dVoutRowIdx:dVoutRowIdx+slopeFittingCount],
                                    dVout[2][dVoutRowIdx:dVoutRowIdx+slopeFittingCount,
                                             dVoutColIdx].flatten().tolist()[0],1)
            ootau = polyParams[0]
            metaDown = -polyParams[1]/ootau
            
            oneOverTau[2].append(ootau)
        else:
            oneOverTau[2].append(0)
            metaDown = -1
            
        if (dVoutRowIdx > slopeFittingCount + slopeSkipEnd) :
            
            polyParams = np.polyfit(dVout[1][dVoutRowIdx:dVoutRowIdx-slopeFittingCount:-1],
                                    dVout[2][dVoutRowIdx:dVoutRowIdx-slopeFittingCount:-1,
                                             dVoutColIdx].flatten().tolist()[0],1)
            ootau = polyParams[0]
            metaUp = -polyParams[1]/ootau
            
            oneOverTau[1].append(ootau)
        else:
            oneOverTau[1].append(0)
            metaUp = -1
           
        if (metaUp > 0) and (metaDown > 0):           
            metaPoints[0].append(dVout[0][dVoutColIdx])
            Vm = get_crossing(metaDown, oneOverTau[2][-1],
                              metaUp, oneOverTau[1][-1])
            metaPoints[1].append(Vm)
            metaPoints[2].append(metaUp)
            metaPoints[3].append(metaDown)
            
            print_info("%s  -->   %s/%s/%s    <--   %s"%(dVout[1][dVoutRowIdx+1],
                                                            metaUp, metaPoints[1][-1], metaDown,
                                                     dVout[1][dVoutRowIdx]))

        dVoutColIdx += 1

    #-----------------------------------------------------------------

    print_info("get_meta_dVout_dt took %s seconds"%(time.time()-start_time))
    
    plt.figure()
    plt.plot(oneOverTau[0], oneOverTau[1], 'b-')
    plt.plot(oneOverTau[0], oneOverTau[2], 'g-')
    plt.grid()
    plt.xlabel('Vin')
    plt.ylabel('1/tau')
    plt.savefig(FIG_FOLDER+DIR_NAME[:-1]+'_tau_dVout_dt.png')

    write_csv_column(DATA_FOLDER + DIR_NAME + 'metaDVoutDt.csv', metaPoints, 'vin; vmeta; vmeta_up; vmeta_down\n');
    write_csv_column(DATA_FOLDER + DIR_NAME + 'metaDVoutDtTau.csv', oneOverTau, 'vin; 1/tau\n');
    
    print_info("analytic calculation of metastable voltages done")

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# determine metastability by transient simulations and predicting backwards

def get_meta_trans(circuit):
    print_info("determining metastable voltages by transients")

    slopeFittingCount = 1
    slopeSkipEnd = 2
    
    dVout = read_dVout(DATA_FOLDER + DIR_NAME + 'dVout_dt.csv')
    meta = read_meta(DATA_FOLDER + DIR_NAME + 'meta.csv')

    start_time = time.time()
    
    #-----------------------------------------------------------------
    
    # get lower value of metastable region
    limits = [int(i) for i in meta[0]]
    meta = meta[1:]

    dVoutColIdx = 0
    while dVout[0][dVoutColIdx] < meta[limits[0]][0]:
        dVoutColIdx += 1
    dVoutColIdx += 1

    #-----------------------------------------------------------------

    oneOverTau = [ [], [], [] ]
    metaPoints = [ [], [], [], [] ]
  
    while dVout[0][dVoutColIdx] < meta[limits[1]][0]:

#        print_info("starting transient simulations for vin=%s"%dVout[0][dVoutColIdx])
        
        # skip first derivative which are positive as stable value not exactly at 0V
        dVoutRowIdx = len(dVout[1])-1
        while (dVout[2][dVoutRowIdx,dVoutColIdx] > 0) :
            dVoutRowIdx -= 1
        
        # go upwards until metastable value crossed
        while (dVout[2][dVoutRowIdx,dVoutColIdx] < 0) :
            dVoutRowIdx -= 1

        oneOverTau[0].append(dVout[0][dVoutColIdx])

        # print(dVoutRowIdx)
        # print(dVoutColIdx)
        # print(dVout[2][dVoutRowIdx:0:-1, dVoutColIdx])
        # print(dVout[2][dVoutRowIdx, dVoutColIdx])
        
        
        if dVoutRowIdx > slopeFittingCount + slopeSkipEnd :  
            [metaUp, ootauUp] = do_trans_tau(dVout[0][dVoutColIdx], dVout[1][dVoutRowIdx],
                   [dVout[1][dVoutRowIdx:0:-1],
                    dVout[2][dVoutRowIdx:0:-1, dVoutColIdx].flatten().tolist()[0]])
            oneOverTau[1].append(ootauUp)
        else:
            oneOverTau[1].append(0)
            metaUp = -1
            
        if dVoutRowIdx < len(dVout[1])-slopeFittingCount - slopeSkipEnd -1:
            [metaDown, ootauDown] = do_trans_tau(dVout[0][dVoutColIdx], dVout[1][dVoutRowIdx+1],
                    [dVout[1][dVoutRowIdx+1:],
                    dVout[2][dVoutRowIdx+1:, dVoutColIdx].flatten().tolist()[0]])
            oneOverTau[2].append(ootauDown)
        else:
            oneOverTau[2].append(0)
            metaDown = -1
        
        if (metaUp > 0) and (metaDown > 0):           
            metaPoints[0].append(dVout[0][dVoutColIdx])
            Vm = get_crossing(metaDown, oneOverTau[2][-1],
                              metaUp, oneOverTau[1][-1])
            metaPoints[1].append(Vm)
            metaPoints[2].append(metaUp)
            metaPoints[3].append(metaDown)
            print_info("%s  -->   %s/%s/%s    <--   %s"%(dVout[1][dVoutRowIdx+1],
                                                         metaUp, metaPoints[1][-1], metaDown,
                                                         dVout[1][dVoutRowIdx]))
        dVoutColIdx += 1

    #-----------------------------------------------------------------

    print_info("get_meta_trans took %s seconds"%(time.time()-start_time))
    
    plt.figure()
    plt.plot(oneOverTau[0], oneOverTau[1], 'b-')
    plt.plot(oneOverTau[0], oneOverTau[2], 'g-')
    plt.grid()
    plt.xlabel('Vin')
    plt.ylabel('1/tau')
    plt.savefig(FIG_FOLDER+DIR_NAME[:-1]+'_tau_trans.png')

    write_csv_column(DATA_FOLDER + DIR_NAME + 'metaTrans.csv', metaPoints, 'vin; vmeta; vmeta_up; vmeta_down\n');
    write_csv_column(DATA_FOLDER + DIR_NAME + 'metaTransTau.csv', oneOverTau, 'vin; 1/tau\n');
    
    print_info("determining metastable voltages by transients done")

    
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# determine metastable value by using metastability inversion

def get_inv_meta_trans(circuit):
    
    print_info("starting inverted metastable transient analysis")
    
    dVout = read_dVout(DATA_FOLDER + DIR_NAME + 'dVout_dt.csv')
    meta = read_meta(DATA_FOLDER + DIR_NAME + 'meta.csv')

    start_time = time.time()
    
    #-----------------------------------------------------------------
    
    # get lower value of metastable region
    limits = [int(i) for i in meta[0]]
    meta = meta[1:]

    dVoutColIdx = 0
    while dVout[0][dVoutColIdx] < meta[limits[0]][0]:
        dVoutColIdx += 1
    dVoutColIdx += 1

    #-----------------------------------------------------------------

    fileName = CIRCUIT_FOLDER + circuit + '/inv_meta_trans.sp'
    metaPoints = [[], []]
    counter=0

    while dVout[0][dVoutColIdx] < meta[limits[1]][0]:

        vin = dVout[0][dVoutColIdx]        
        vout= meta[limits[0]][2] + (meta[limits[1]][2]-meta[limits[0]][2])/\
            (meta[limits[1]][0] - meta[limits[0]][0]) * (vin - meta[limits[0]][0])
        
        print_info("started vin=%s"%vin)
        metaPoints[0].append(vin)
        voltage = ("%.7f"%(vin)).replace('.','')
        spiceFileName = SPICE_FOLDER + DIR_NAME + 'inv_meta_trans_%s.sp'%voltage
         
        if not os.path.isfile(spiceFileName[:-3]+'.tr0'):
            cmd = "sed -e 's/<sed>in<sed>/%s/' -e 's/<sed>out<sed>/%s/' -e 's/<sed>time<sed>/%s/' "\
                    %(vin, vout, 7000) + fileName  + \
                    " > "  + spiceFileName
            code = subprocess.call(cmd,shell = True ,  stderr=subprocess.STDOUT)

            if (code != 0):
                print_error("sed failed")
                return

            cmd = "hspice -i %s -o %s >> hspice_log 2>&1"%(spiceFileName[:-3], spiceFileName[:-3])
            code = subprocess.call(cmd,shell = True ,  stderr=subprocess.STDOUT)

            if (code != 0):
                print_error("hspice failed")
                return

        cmd = "grep finalval= %s.lis"%(spiceFileName[:-3])
        code = subprocess.Popen(cmd,shell = True ,  stdout=subprocess.PIPE)

        lastVal = float( code.stdout.read().split(' ')[2] )
        metaPoints[1].append(lastVal)

        dVoutColIdx += 1

    print_info("get_inv_meta_trans took %s seconds"%(time.time()-start_time))
        
    write_csv_column(DATA_FOLDER + DIR_NAME + 'invMetaTrans.csv', metaPoints, 'vin; vmeta\n');
    
    print_info("inverted metastable transient analysis done")

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# determine metastability using DC analysis

def get_meta_dc(circuit):
    
    print_info("starting metastable dc analysis")

    dVout = read_dVout(DATA_FOLDER + DIR_NAME + 'dVout_dt.csv')
    meta = read_meta(DATA_FOLDER + DIR_NAME + 'meta.csv')

    start_time = time.time()
    
    #-----------------------------------------------------------------
    
    # get lower value of metastable region
    limits = [int(i) for i in meta[0]]
    meta = meta[1:]

    voutInit = meta[limits[0]+(limits[1]-limits[0])/10][2]

    #-----------------------------------------------------------------

    fileName = CIRCUIT_FOLDER + circuit + '/dc.sp'
    metaPoints = [[], []]

    spiceFileName = SPICE_FOLDER + DIR_NAME + 'dc.sp'

    if not os.path.isfile(spiceFileName[:-3]+'.sw0'):
        cmd = "sed -e 's/<sed>lower<sed>/%s/' -e 's/<sed>upper<sed>/%s/' -e 's/<sed>step<sed>/%s/' "\
            "-e 's/<sed>out<sed>/%s/' "\
            %(meta[limits[0]][0], meta[limits[1]][0], meta[1][0]-meta[0][0], voutInit) + fileName  + \
            " > "  + spiceFileName

        code = subprocess.call(cmd,shell = True ,  stderr=subprocess.STDOUT)

        if (code != 0):
            print_error("sed failed")
            return

        cmd = "hspice -i %s -o %s >> hspice_log 2>&1"%(spiceFileName[:-3], spiceFileName[:-3])
        code = subprocess.call(cmd,shell = True ,  stderr=subprocess.STDOUT)

        if (code != 0):
            print_error("hspice failed")
            return

    print_info("get_meta_dc took %s seconds"%(time.time()-start_time))
        
    data = read_hspice(spiceFileName[:-3]+'.sw0',2)
    write_csv_column(DATA_FOLDER + DIR_NAME + 'metaDC.csv', data, 'vin; vmeta\n');

    print_info("metastable dc analysis done")

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# calculate loop amplification in determined metastable values

def get_loop_amplification(circuit):

    print_info("determining loop amplification in metastable points")
    
    meta = read_meta(DATA_FOLDER + DIR_NAME + 'meta.csv')
    limits = [int(i) for i in meta[0]]
    meta = meta[1:]    

    amps = [[],[]]
   
    start_time = time.time()
    
    #-----------------------------------------------------------------

    fileName = CIRCUIT_FOLDER + circuit + '/amp.sp'
    
    for idx in range(limits[0], limits[1], 1):

        # if not in metastable range
        if len(meta[idx]) < 4:
            continue
        
        vin = meta[idx][0]
        vout = meta[idx][2]

        print_info("started vin=%s"%vin)
        
        stringVin = ("%.7f"%vin).replace('.','')
        stringVout = ("%.7f"%vout).replace('.','')    
        
        spiceFileName = SPICE_FOLDER + DIR_NAME + 'amp_%s_%s.sp'%(stringVin, stringVout)
        
        if not os.path.isfile(spiceFileName[:-3]+'.ma0'):
            cmd = "sed -e 's/<sed>vin<sed>/%s/' -e 's/<sed>vout<sed>/%s/' "\
                %(vin, vout) + fileName  + " > "  + spiceFileName
            code = subprocess.call(cmd,shell = True ,  stderr=subprocess.STDOUT)

            if (code != 0):
                print_error("sed failed")
                return

            cmd = "hspice -i %s -o %s >> hspice_log 2>&1"%(spiceFileName[:-3], spiceFileName[:-3])
            code = subprocess.call(cmd,shell = True ,  stderr=subprocess.STDOUT)

            if (code != 0):
                print_error("hspice failed")
                return

        cmd = "grep loop_gain_at_min_freq %s.lis"%(spiceFileName[:-3])
        code = subprocess.Popen(cmd,shell = True ,  stdout=subprocess.PIPE)

        amp = float( code.stdout.read().split('=')[1] )

        amps[0].append(vin)
        amps[1].append(10**(amp/20))

    write_csv_column(DATA_FOLDER + DIR_NAME + 'amp.csv', amps, 'vin; amplification\n');

    print_info("get_loop_amplification took %s seconds"%(time.time()-start_time))

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# get loop amplification for single value of vin but multiple values of vout

def get_loop_amplification_vin(circuit):

    print_info("determining loop amplification in metastable points")
    factor=5e-2
    
    meta = read_meta(DATA_FOLDER + DIR_NAME + 'meta.csv')
    limits = [int(i) for i in meta[0]]
    meta = meta[1:]    
 
    start_time = time.time()
    
    #-----------------------------------------------------------------

    fileName = CIRCUIT_FOLDER + circuit + '/amp.sp'

    idx = (limits[0]+ limits[1])/2
    vin = meta[idx][0]
    print_info("using vin=%s"%vin)
    stringVin = ("%.7f"%vin).replace('.','')

    amps = [[vin],[meta[idx][2]]]
    
    for vout in np.linspace(meta[idx][2]*(1-factor),meta[idx][2]*(1+factor), 10):

        print_info("started vout=%s"%vout)
        
        stringVout = ("%.7f"%vout).replace('.','')    
        
        spiceFileName = SPICE_FOLDER + DIR_NAME + 'amp_vin_%s_%s.sp'%(stringVin, stringVout)
        
        if not os.path.isfile(spiceFileName[:-3]+'.ma0'):
            cmd = "sed -e 's/<sed>vin<sed>/%s/' -e 's/<sed>vout<sed>/%s/' "\
                %(vin, vout) + fileName  + " > "  + spiceFileName
            code = subprocess.call(cmd,shell = True ,  stderr=subprocess.STDOUT)

            if (code != 0):
                print_error("sed failed")
                return

            cmd = "hspice -i %s -o %s >> hspice_log 2>&1"%(spiceFileName[:-3], spiceFileName[:-3])
            code = subprocess.call(cmd,shell = True ,  stderr=subprocess.STDOUT)

            if (code != 0):
                print_error("hspice failed")
                return

        cmd = "grep loop_gain_at_min_freq %s.lis"%(spiceFileName[:-3])
        code = subprocess.Popen(cmd,shell = True ,  stdout=subprocess.PIPE)

        amp = float( code.stdout.read().split('=')[1] )

        amps[0].append(vout)
        amps[1].append(10**(amp/20))

    write_csv_column(DATA_FOLDER + DIR_NAME + 'amp_%s.csv'%stringVin, amps, 'vin; amp\n');

    print_info("get_loop_amplification_vin took %s seconds"%(time.time()-start_time))
    
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def evaluate_meta(circuit):
   
    metaLine = read_meta(DATA_FOLDER + DIR_NAME + 'meta_line.csv')
    meta = read_meta(DATA_FOLDER + DIR_NAME + 'meta.csv')
    limits = [int(i) for i in meta[0]]
    meta = meta[1:]
    
    fileName = DATA_FOLDER + DIR_NAME + 'metaDVoutDt.csv'
    if not os.path.isfile(fileName):
        get_meta_dVout(circuit)
    metaDVout = read_csv(fileName)
    
    fileName = DATA_FOLDER + DIR_NAME + 'metaTrans.csv'
    if not os.path.isfile(fileName):
        get_meta_trans(circuit)
    metaTrans = read_csv(fileName)

    fileName = DATA_FOLDER + DIR_NAME + 'invMetaTrans.csv'
    if not os.path.isfile(fileName):
        get_inv_meta_trans(circuit)
    invMetaTrans = read_csv(fileName)

    fileName = DATA_FOLDER + DIR_NAME + 'metaDC.csv'
    if not os.path.isfile(fileName):
        get_inv_meta_dc(circuit)
    invMetaDC = read_csv(fileName)
    
    #-----------------------------------------------------------------

    printSPICE = row_to_column(metaLine)
    printDVout = row_to_column(metaDVout)
    printTrans = row_to_column(metaTrans)
    printInvMetaTrans = row_to_column(invMetaTrans)
    printInvMetaDC = row_to_column(invMetaDC)
    printLinear= [[],[]]
    for idx in range(limits[0],limits[1]+1):
        printLinear[0].append(meta[idx][0])
    vL = meta[limits[0]][2]
    vH = meta[limits[1]][2]
    dV = meta[limits[1]][0] - meta[limits[0]][0]
    printLinear[1] = [vL + (vH-vL)*(i-printLinear[0][0])/dV for i in printLinear[0]]
    
    plt.figure()
    plt.plot(printSPICE[0], printSPICE[1], 'b-')
    plt.plot(printDVout[0], printDVout[1], 'g-')
    plt.plot(printTrans[0], printTrans[1], 'r-')
    plt.plot(printInvMetaTrans[0], printInvMetaTrans[1], 'c-')
    plt.plot(printInvMetaDC[0], printInvMetaDC[1], 'm-')
    plt.plot(printLinear[0], printLinear[1], 'k-')
    plt.grid()
    plt.ylim([-0.1,1.3])
    plt.xlabel('Vin')
    plt.ylabel('Vout')
    plt.savefig(FIG_FOLDER+DIR_NAME[:-1]+'_meta_prediction.png')
   
    metaIdx = limits[0]
    
    while abs(meta[metaIdx][0] -metaDVout[0][0]) > 1e-8:
        metaIdx+= 1

    measured = meta[metaIdx:-1:HYSTERESIS_COUNT_MULT]
    
    outDeviation = [ [], [], [], [], [] ]
    fileName = CIRCUIT_FOLDER + circuit + '/eval.sp'

    tmpDVout = [metaDVout[idx][1] - measured[idx][2] for idx in range(len(metaDVout))]
    tmpTrans = [metaTrans[idx][1] - measured[idx][2] for idx in range(len(metaTrans))]
    tmpInvMetaTrans = [invMetaTrans[idx][1] - measured[idx][2] for idx in range(len(invMetaTrans))]
    tmpInvMetaDC = [invMetaDC[idx][1] - meta[limits[0]:limits[1]+1][idx][2] for idx in range(len(invMetaDC))]
    tmpLinear = [printLinear[1][idx] - meta[limits[0]:limits[1]+1][idx][2] for idx in range(len(printLinear[0]))]
       
    plt.figure()
    plt.plot(printDVout[0], tmpDVout, 'g-', label='static prediction')
    plt.plot(printTrans[0], tmpTrans, 'b-', label='dynamic prediction')
    plt.plot(printInvMetaTrans[0], tmpInvMetaTrans, 'c-', label='inverted meta trans')
    plt.plot(printInvMetaDC[0], tmpInvMetaDC, 'm-', label='inverted meta DC')
    plt.plot(printLinear[0], tmpLinear, 'k-', label='linear approx')
    plt.grid()
    plt.xlabel('Vin')
    plt.ylabel('diff(Vm)')
    plt.ylim([max(tmpTrans)*1.1,min(tmpTrans)*1.1])
    plt.legend(loc='upper right')
    plt.savefig(FIG_FOLDER+DIR_NAME[:-1]+'_meta_prediction_diff.png')

    tmpDVout = [np.abs(i) for i in tmpDVout]
    tmpTrans = [np.abs(i) for i in tmpTrans]
    tmpInvMetaTrans = [np.abs(i) for i in tmpInvMetaTrans]
    tmpInvMetaDC = [np.abs(i) for i in tmpInvMetaDC]
    tmpLinear = [np.abs(i) for i in tmpLinear]

    write_csv_column(DATA_FOLDER + DIR_NAME + 'metaDVoutDiff.csv', [printDVout[0], tmpDVout], 'vin; vdiff\n');    
    write_csv_column(DATA_FOLDER + DIR_NAME + 'metaTransDiff.csv', [printTrans[0], tmpTrans], 'vin; vdiff\n');
    write_csv_column(DATA_FOLDER + DIR_NAME + 'invMetaTransDiff.csv', [printInvMetaTrans[0], tmpInvMetaTrans], 'vin; vdiff\n');
    write_csv_column(DATA_FOLDER + DIR_NAME + 'invMetaDCDiff.csv', [printInvMetaDC[0], tmpInvMetaDC], 'vin; vdiff\n');
    
    plt.figure()
    plt.semilogy(printDVout[0], tmpDVout, 'g-', label='static prediction')
    plt.semilogy(printTrans[0], tmpTrans, 'b-', label='dynamic prediction')
    plt.semilogy(printInvMetaTrans[0], tmpInvMetaTrans, 'c-', label='inverted meta trans')
    plt.semilogy(printInvMetaDC[0], tmpInvMetaDC, 'm-', label='inverted meta DC')
    plt.plot(printLinear[0], tmpLinear, 'k-', label='linear approx')
    plt.grid()
    plt.xlabel('Vin')
    plt.ylabel('log(diff(Vm))')
#    plt.ylim([max(tmpTrans)*1.1,min(tmpTrans)*1.1])
    plt.legend(loc='upper right')
    plt.savefig(FIG_FOLDER+DIR_NAME[:-1]+'_meta_prediction_diff_log.png')
    
#    return
    
    styles = ['g-', 'b-', 'c-', 'm-', 'k']
    labels = ['static prediction', 'dynamic prediction', 'inverted meta trans', 'inverted meta dc', 'binary search']

    # output file name, position in outDeviation, array holding data, entry to pick from data
    params = [['eval_dVout',2, metaDVout,1],
              ['eval_Trans',3, metaTrans,1],
              ['eval_invMetaTrans',4, invMetaTrans,1],
              ['eval_invMetaDC',5, invMetaDC,1],
              ['eval_SPICE',1, meta[limits[0]:limits[1]+1],2]]

    print_info("number of metastable values: %s"%(limits[1]-limits[0]+1))
    
    start_time = time.time()
    
    plt.figure()

    idxPlot = 0
    for entry in params:

        print_info("starting simulation of '%s'"%entry[0])
        tmpPrint = [ [], [] ]

        for idx in range(len(entry[2])):

            tmpPrint[0].append(entry[2][idx][0])
            voltage = ("%.7f"%(entry[2][idx][0])).replace('.','')
            spiceFileName = SPICE_FOLDER + DIR_NAME + entry[0] + '_%s.sp'%voltage
            
            print_info("doing vin=%s, vout=%s"%(entry[2][idx][0], entry[2][idx][entry[3]]))
        
            if not os.path.isfile(spiceFileName[:-3]+'.lis'):
                cmd = "sed -e 's/<sed>in<sed>/%s/' -e 's/<sed>out<sed>/%s/' -e 's/<sed>time<sed>/%s/' "\
                        %(entry[2][idx][0], entry[2][idx][entry[3]], 200) + fileName  + \
                        " > "  + spiceFileName
                code = subprocess.call(cmd,shell = True ,  stderr=subprocess.STDOUT)

                if (code != 0):
                    print_error("sed failed")
                    return

                cmd = "hspice -i %s -o %s >> hspice_log 2>&1"%(spiceFileName[:-3], spiceFileName[:-3])
                code = subprocess.call(cmd,shell = True ,  stderr=subprocess.STDOUT)

                if (code != 0):
                    print_error("hspice failed")
                    return

            cmd = "grep diff= %s.lis"%(spiceFileName[:-3])
            code = subprocess.Popen(cmd,shell = True ,  stdout=subprocess.PIPE)

            tmpPrint[1].append(abs(float( code.stdout.read().split('=')[1] )))

        plt.semilogy(tmpPrint[0], tmpPrint[1], styles[idxPlot], label=labels[idxPlot])
        write_csv_column(DATA_FOLDER + DIR_NAME + entry[0] + '.csv', tmpPrint, 'vin,log(deviation)\n')
        idxPlot += 1
            
    plt.grid()
    plt.legend(loc='upper right')
    plt.xlabel('Vin')
    plt.ylabel('dev(.)')
    plt.savefig(FIG_FOLDER+DIR_NAME[:-1]+'_meta_prediction_comp.png')    

    print_info("evaluate_meta took %s seconds"%(time.time()-start_time))
    
#********************************************************************************

def prepare_simulation(circuit, technology):

    global DIR_NAME
    
    if os.path.islink('technology'):
        os.remove('technology')

    if os.path.isfile(TECH_FOLDER+technology):
        os.symlink(TECH_FOLDER+technology, 'technology')
    else:
        print_error("stated technology '%s' does not exist!"%technology)
        sys.exit(1)

    DIR_NAME = circuit + '_' + technology + '/'

    if not os.path.isdir(SPICE_FOLDER):
        os.mkdir(SPICE_FOLDER)
        
    if not os.path.isdir(SPICE_FOLDER +DIR_NAME):
        os.mkdir(SPICE_FOLDER +DIR_NAME)

    if not os.path.isdir(FIG_FOLDER):
        os.mkdir(FIG_FOLDER)
        
    if not os.path.isdir(SPICE_FOLDER +DIR_NAME):
        os.mkdir(SPICE_FOLDER +DIR_NAME)
        
    if not os.path.isdir(DATA_FOLDER):
        os.mkdir(DATA_FOLDER)

    if not os.path.isdir(DATA_FOLDER +DIR_NAME):
        os.mkdir(DATA_FOLDER +DIR_NAME)

#********************************************************************************

def print_usage():
        
    print("usage: python %s <circuit> <technology> <analysis>"%sys.argv[0])
    print("\nmeta ... calculate hysteresis and metastable line using bisection")
    print("map ... print map of dVout/dt over the Vin-Vout plane")
    print("dVout ... calculate metastable values based on dVout/dt map")
    print("trans ... calculate metastable values based on transient simulations")
    print("inv ... calculate metastable values based on metastability inversion")
    print("dc ... calculate metastable values based on DC analysis")
    print("amp ... determine loop amplification in metastable values")
    print("amp_vin ... loop amplification for single input voltage but multiple output voltages")
    print("eval ... evaluate all estimations")
    print("all ... executed everything")
        
#********************************************************************************
# main ###
#********************************************************************************

if __name__ == '__main__':

    if len(sys.argv) != 4:
        print_usage()
        sys.exit()

    circuit=sys.argv[1]
    technology=sys.argv[2]
    mode=sys.argv[3]
    
    prepare_simulation(circuit, technology)
    
    if (mode == "meta"):
        get_meta(circuit)
    elif (mode == "map"):
        get_dVout_dt(circuit)
    elif (mode == "dVout"):
        get_meta_dVout_dt(circuit)
    elif (mode == "trans"):
        get_meta_trans(circuit)
    elif (mode == "inv"):
        get_inv_meta_trans(circuit)
    elif (mode == "dc"):
        get_meta_dc(circuit)
    elif (mode == "amp"):
        get_loop_amplification(circuit)
    elif (mode == "amp_vin"):
        get_loop_amplification_vin(circuit)
    elif (mode == "eval"):
        evaluate_meta(circuit)
    elif (mode == "all"):
        get_meta(circuit)
        get_dVout(circuit)
        get_meta_trans(circuit)
        get_meta_dVout_dt(circuit)
        get_inv_meta_dc(circuit)
        get_inv_meta_trans(circuit)
        evaluate_meta(circuit)
    else:
        print_error("unknown mode")
        print_usage()
