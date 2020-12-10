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
import math
from rawread import *

FIG_FOLDER='../figures/'
SPICE_FOLDER='../hspice/'
DATA_FOLDER='../data/'
CIRCUIT_FOLDER='../circuits/'
TECH_FOLDER='../technologies/'
DIR_NAME=''
SPICE_COMMAND='hspice'

#DVOUT_COUNT_VIN=800 # how many different input voltage values to use
#DVOUT_COUNT_VOUT=16000 # how many different output voltage values to use
DVOUT_COUNT_VIN=225 # how many different input voltage values to use
#DVOUT_COUNT_VIN=45 # how many different input voltage values to use
DVOUT_COUNT_VOUT=9000 # how many different output voltage values to use
HYSTERESIS_COUNT_MULT=1 # multiplicative factor how many more input voltage values
   # to use during the hysteresis

DATA_NAMES = ['', 'v(OUT)']
   
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

def calc_first_deriv_x(x, y, stepCnt):

    deriv = []

    for i in range(len(y)):

        if (i<stepCnt):
            value = 0

        elif (i> ( len(y) -stepCnt -1)):
            value = 0

        else:
            value = (y[i+stepCnt]-y[i-stepCnt])/ (x[i+stepCnt]-x[i-stepCnt])

        deriv.append(float(value))

    return deriv

#--------------------------------------------------------------------------------

def read_spectre(filename, varCnt):

    sim, structure = rawread(filename)

    data = []
    varNames = structure[0]['varnames']
    
    for i in range(varCnt):
        data.append([])

    for line in sim[0]:
        data[0].append(line[0])
        for idx in range(1,varCnt, 1):
            data[idx].append( line [ varNames.index( DATA_NAMES[idx] )  ] )
            
    minLen = len(data[0])

    # determine length of shortest array
    for i in range(len(data)):
        if (len(data[i]) < minLen):
            minLen = len(data[i])

    # set each array to same length
    for i in range(len(data)):
        data[i] = data[i][:minLen]
       
    return data

#----------------------------------------------------------------------------------------------

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
                "Iout-matrix, each line is one Vout value, starting with highest Vout\n")

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

def write_pgfplots_2D(data, name):

    fileName = DATA_FOLDER + DIR_NAME + name + '_pgfplots.dat'
    print_info("writing 2D data to pfgplot data file %s"%fileName)
    
    text = 'Vin Vout Iout\n'
    
    for idxVout, voutVal in enumerate(data[1]):
        for idxVin, vinVal in enumerate(data[0]):
            text += '%s %s %s\n'%(vinVal, voutVal, data[2][idxVout][idxVin])

        text += '\n'
        
    with open(fileName,'w') as f:
        f.write(text[:-1])
        
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
    
def read_Iout(fileName):
    
    if not os.path.isfile(fileName):
        get_Iout(circuit)

    return(read_csv_2D(fileName))

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
def read_meta(fileName):
    
    if not os.path.isfile(fileName):
        get_meta(circuit)

    return(read_csv(fileName))

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
def read_meta_dc(fileName):
    
    if not os.path.isfile(fileName):
        get_meta_dc(circuit)

    return(read_csv(fileName))

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def get_CL_P(vin):

    print_info("starting to determine average CL and P for vin="+str(vin))

    limit = 3
    
    startName = 'iout_trans_'    
    fileList = os.listdir(DATA_FOLDER + DIR_NAME)
    fileList.sort()

    stringVin = ("%.7f"%vin).replace('.','')

    CL = 0
    countCL = 0

    P = 0
    countP = 0
    
    for fileName in fileList:
        
        if not fileName.startswith(startName+stringVin):
            continue
        
        if not fileName.endswith('.csv'):
            continue


        
        f = open(DATA_FOLDER + DIR_NAME +fileName)
        lines = f.readlines()[1:]
        f.close()

        tmpCnt = 0
        
        for line in lines:
            if float(line[:-1].split(';')[0]) < 1e-10:
                continue
            
            CL += float(line[:-1].split(';')[-1])
            tmpCnt += 1

            if tmpCnt == limit:
                break

        countCL += tmpCnt


            
        fileName = fileName.replace('trans','match')
       
        f = open(DATA_FOLDER + DIR_NAME + fileName)
        lines = f.readlines()[1:]
        f.close()

        tmpCnt = 0
       
        for line in lines:
            if float(line[:-1].split(';')[0]) < 1e-10:
                continue
            
            P += float(line[:-1].split(';')[-1])
            tmpCnt += 1

            if tmpCnt == limit:
                break

        countP += tmpCnt
        

    if countP > 0:
        P /= countP
    CL /= countCL

    # capacitance stored in files in fF
    return CL*1e-15, P

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def do_trans_tau(vin, vout, startName='trans', doEval=True, vint=0):
   
    print_info("starting do_trans_tau for vin=%s and vout=%s"%(vin, vout))
    
    fileName = CIRCUIT_FOLDER + circuit + '/' + startName + '.sp'
    
    stringVin = ("%.7f"%vin).replace('.','')
    stringVout = ("%.7f"%vout).replace('.','')    
    
    spiceFileName = SPICE_FOLDER + DIR_NAME + startName + '_%s_%s.sp'%(stringVin, stringVout)

#    if not os.path.isfile(spiceFileName[:-3]+'.tr0'):
    if not os.path.isfile(spiceFileName[:-3]+'.aaa'):
        cmd = "sed -e 's/<sed>in<sed>/%s/' -e 's/<sed>out<sed>/%s/' -e 's/<sed>int<sed>/%s/' "\
                %(vin, vout, vint) + fileName  + " > "  + spiceFileName
        code = subprocess.call(cmd,shell = True ,  stderr=subprocess.STDOUT)

        if (code != 0):
            print_error("sed failed")
            return

        cmd = "hspice -i %s -o %s >> hspice_log 2>&1"%(spiceFileName[:-3], spiceFileName[:-3])
#        cmd = "spectre +mt +spp -format nutbin -outdir " + SPICE_FOLDER + DIR_NAME[:-1] + " =log " + spiceFileName[:-3] + ".log " + spiceFileName
        code = subprocess.call(cmd,shell = True ,  stderr=subprocess.STDOUT)

        if (code != 0):
            print_error("hspice failed")
            return

    #-----------------------------------------------------------------
    # the start has to be cut as derivative changes overproportional there

    if doEval == True:
    
        data = read_hspice(spiceFileName[:-3]+'.tr0',4)
    #    data = read_spectre(spiceFileName[:-3]+'.raw',2)

        logVoutTrace = [np.log(abs(j)) for j in data[1]]
        plt.figure()
        plt.plot(data[0], logVoutTrace, 'b*-')
        plt.grid()
        plt.xlabel('time')
        plt.ylabel('V_out')
        plt.savefig(FIG_FOLDER+DIR_NAME[:-1]+'_' + startName + '_%.4f_%.8f.png'%(vin, vout))

        # plt.figure()
        # plt.plot(data[0], data[2], 'b*-')
        # plt.grid()
        # plt.xlabel('time')
        # plt.ylabel('V_out')
        # plt.savefig(FIG_FOLDER+DIR_NAME[:-1]+'_' + startName + '_dVout_%.4f_%.8f.png'%(vin, vout))    

    #    deriv = calc_first_deriv_x(data[0], data[1], 5)
     #   data.append(deriv)

        startIdx= int(len(data[2])*6.6/10)
        dVoutTrace = data[2][startIdx:]
        timeTrace = data[0][startIdx:]

        logDVoutTrace = [np.log(abs(j)) for j in dVoutTrace]
        maxIdx = logDVoutTrace.index(max(logDVoutTrace))

        plt.figure()
        logDVoutTracePrint = [np.log(abs(j)) for j in data[2]]
        plt.plot(data[0], logDVoutTracePrint, 'b*-')

    #    plt.savefig(FIG_FOLDER+DIR_NAME[:-1]+'_' + startName + '_%.5f_%.5f.png'%(vin, vout))

        if maxIdx == 0:
            plt.grid()
            plt.xlabel('time')
            plt.ylabel("ln(V_out')")
            plt.savefig(FIG_FOLDER+DIR_NAME[:-1]+'_' + startName + '_dVout_log_%.4f_%.8f.png'%(vin, vout))
            return[-1,0]
        polyParams = np.polyfit(timeTrace[:maxIdx],logDVoutTrace[:maxIdx],1)


        p1 = np.poly1d(polyParams)
        y = [p1(x) for x in timeTrace]
        plt.plot(timeTrace, y, 'r-')
        plt.grid()
        plt.xlabel('time')
        plt.ylabel("ln(V_out')")
        plt.savefig(FIG_FOLDER+DIR_NAME[:-1]+'_' + startName + '_dVout_log_%.4f_%.8f.png'%(vin, vout))

        ootau = polyParams[0]
        idx = maxIdx/1

        # OUTDATED!
        # see documentation for more details on that expression
        # t0 = (logDVoutTrace[idx] - np.log(ootau))/ootau

        # if (data[1][-1] > data[1][0]):
        #     Vm = data[1][idx]- np.exp(t0*ootau)
        # else:
        #     Vm = data[1][idx]+ np.exp(t0*ootau)

        # this is the method used in the paper

        Vm = data[1][idx]- data[2][idx]/ootau

        return [Vm, ootau]

    else:
        return [0,0]
    
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def get_crossing (V1, slope1, V2, slope2):
#    return ((slope1*V1+slope2*V2)/(slope1+slope2))

    t = abs(V1 - V2) / (abs(slope1) + abs(slope2))

    if V1 < V2 :
        if slope1 < 0:
            return V1 - t * slope1
        else:
            return V1 + t * slope1
    else:

        if slope1 > 0:
            return V1 - t * slope1
        else:
            return V1 + t * slope1
        
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
    metaData = [ [len(vinVals)-limits[1]-1, limits[0]] ]
#    metaData = [ [0, len(metaLine[0])] ]

    # for idx in range(len(metaLine[0])):
    #     entry = [metaLine[0][idx]]
    #     entry.append(0)
    #     entry.append(metaLine[1][idx])
    #     entry.append(0)
    #     metaData.append(entry)
    
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

        if limit== -1:
            vths[0].append(data[0][-1])
            vths[1].append(data[1][-1])
            limits.append(len(data[1])-1)
        else:
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
#        if (vin < 0.3) or (vin > 0.5):
#            continue
        
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
# generate a map that displays the output current over the input-output
# voltage plane

def get_Iout(name):
    print_info("generating Iout over Vin-Vout plane")

    start_time = time.time()
    
    fileName = CIRCUIT_FOLDER + name + '/Iout.sp'

    spiceFileName = SPICE_FOLDER+DIR_NAME+'Iout.sp'
    cmd = "sed -e 's/<sed>stepsVout<sed>/%s/' -e 's/<sed>stepsVin<sed>/%s/' "\
            %(DVOUT_COUNT_VOUT+1, DVOUT_COUNT_VIN) + fileName  + " > "  + spiceFileName
    code = subprocess.call(cmd,shell = True ,  stderr=subprocess.STDOUT)

    if (code != 0):
        print_error("sed failed")
        return

    if not os.path.isfile(spiceFileName[:-3]+'.sw0'):
        cmd = "hspice -mt 4 -i %s -o %s >> hspice_log 2>&1"%(spiceFileName[:-3], spiceFileName[:-3])
        code = subprocess.call(cmd,shell = True ,  stderr=subprocess.STDOUT)

        if (code != 0):
            print_error("hspice failed")
            return

    print_info("get_Iout took %s seconds"%(time.time()-start_time))
        
    data = read_hspice_2D(spiceFileName[:-3]+'.sw0')

    write_csv_2D(data, 'Iout')
    write_pgfplots_2D(data, 'Iout')

    print_info("starting generation of matlab file")
    cmd = "matlab -r 'plot_Iout '%s' '%s'; quit' -nodisplay"\
            %(DATA_FOLDER + DIR_NAME, FIG_FOLDER + DIR_NAME[:-1] + '_')
    code = subprocess.call(cmd,shell = True ,  stderr=subprocess.STDOUT)

    if (code != 0):
        print_error("matlab failed")
        return
   
    print_info("finished plotting figures")

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# calculate metastable voltage by using data from the Iout map

def get_meta_Iout(circuit):
    
    print_info("starting analytic calculation of metastable voltages based on Iout map")
    
    slopeFittingCount = 2
    slopeSkipEnd = 2
    
    Iout = read_Iout(DATA_FOLDER + DIR_NAME + 'Iout.csv')
    meta = read_meta(DATA_FOLDER + DIR_NAME + 'meta.csv')

    start_time = time.time()
    
    #-----------------------------------------------------------------
    
    # get lower value of metastable region
    limits = [int(i) for i in meta[0]]
    meta = meta[1:]

    IoutColIdx = 0
    while Iout[0][IoutColIdx] < meta[limits[0]][0]:
        IoutColIdx += 1
#    IoutColIdx += 1

    #-----------------------------------------------------------------
    
    oneOverTau = [ [], [], [] ]
    metaPoints = [ [], [], [], [] ]
    
    while Iout[0][IoutColIdx] < meta[limits[1]][0]:

        # stable value not exactly at 0V, therefore lowermost row has
        # derivative > 0, so skip it
        IoutRowIdx = len(Iout[1])-1
        while (Iout[2][IoutRowIdx,IoutColIdx] > 0) :
            IoutRowIdx -= 1

        # go upwards until metastable value crossed
        while (Iout[2][IoutRowIdx,IoutColIdx] < 0) :
            IoutRowIdx -= 1

        oneOverTau[0].append(Iout[0][IoutColIdx])

        CL, P = get_CL_P(Iout[0][IoutColIdx])
        
        if IoutRowIdx < len(Iout[1])-slopeFittingCount - slopeSkipEnd -1:
            
            polyParams = np.polyfit(Iout[1][IoutRowIdx:IoutRowIdx+slopeFittingCount],
                                    Iout[2][IoutRowIdx:IoutRowIdx+slopeFittingCount,
                                             IoutColIdx].flatten().tolist()[0],1)
            ootau = polyParams[0]
            metaDown = -polyParams[1]/ootau
#            metaDown = Iout[1][IoutRowIdx+1]+Iout[2][IoutRowIdx+1,IoutColIdx]/ootau
            
            oneOverTau[2].append(ootau/(CL*P))
        else:
            oneOverTau[2].append(0)
            metaDown = -1

        # plt.figure()
        # plt.plot(Iout[1][IoutRowIdx:IoutRowIdx+slopeFittingCount],
        #                             Iout[2][IoutRowIdx:IoutRowIdx+slopeFittingCount,
        #                                      IoutColIdx].flatten().tolist()[0], 'b*-')

        # timeTrace = Iout[1][IoutRowIdx:IoutRowIdx+slopeFittingCount]
        # p1 = np.poly1d(polyParams)
        # y = [p1(x) for x in timeTrace]
        # plt.plot(timeTrace, y, 'r-')

        # plt.savefig(FIG_FOLDER+DIR_NAME[:-1]+'_tau_Iout_down_%.05f.png'%(Iout[0][IoutColIdx]))
            
        if (IoutRowIdx > slopeFittingCount + slopeSkipEnd) :
            
            polyParams = np.polyfit(Iout[1][IoutRowIdx:IoutRowIdx-slopeFittingCount:-1],
                                    Iout[2][IoutRowIdx:IoutRowIdx-slopeFittingCount:-1,
                                             IoutColIdx].flatten().tolist()[0],1)
            ootau = polyParams[0]
            metaUp = -polyParams[1]/ootau
#            metaUp = Iout[1][IoutRowIdx+1]-Iout[2][IoutRowIdx+1,IoutColIdx]/ootau
            
            oneOverTau[1].append(ootau/(CL*P))
        else:
            oneOverTau[1].append(0)
            metaUp = -1

        # plt.figure()
        # plt.plot(Iout[1][IoutRowIdx:IoutRowIdx-slopeFittingCount:-1],
        #                             Iout[2][IoutRowIdx:IoutRowIdx-slopeFittingCount:-1,
        #                                      IoutColIdx].flatten().tolist()[0], 'b*-')

        # timeTrace = Iout[1][IoutRowIdx:IoutRowIdx-slopeFittingCount:-1]
        # p1 = np.poly1d(polyParams)
        # y = [p1(x) for x in timeTrace]
        # plt.plot(timeTrace, y, 'r-')
        
        # plt.savefig(FIG_FOLDER+DIR_NAME[:-1]+'_tau_Iout_up_%.05f.png'%(Iout[0][IoutColIdx]))
            
        if (metaUp > 0) and (metaDown > 0):           
            metaPoints[0].append(Iout[0][IoutColIdx])
            Vm = get_crossing(metaDown, 1/oneOverTau[2][-1],
                              metaUp, 1/oneOverTau[1][-1])
            metaPoints[1].append(Vm)
            metaPoints[2].append(metaUp)
            metaPoints[3].append(metaDown)
            
            print_info("vin=%.5f: %s  -->   %s/%s/%s    <--   %s"%(Iout[0][IoutColIdx],Iout[1][IoutRowIdx+1],
                                                            metaDown, metaPoints[1][-1], metaUp,
                                                     Iout[1][IoutRowIdx]))

        IoutColIdx += 1

    #-----------------------------------------------------------------

    print_info("get_meta_Iout took %s seconds"%(time.time()-start_time))
    
    plt.figure()
    plt.plot(oneOverTau[0], oneOverTau[1], 'b-')
    plt.plot(oneOverTau[0], oneOverTau[2], 'g-')
    plt.grid()
    plt.xlabel('Vin')
    plt.ylabel('1/tau')
    plt.savefig(FIG_FOLDER+DIR_NAME[:-1]+'_tau_Iout.png')

    write_csv_column(DATA_FOLDER + DIR_NAME + 'metaIout.csv', metaPoints, 'vin; vmeta; vmeta_up; vmeta_down\n');
    write_csv_column(DATA_FOLDER + DIR_NAME + 'metaIoutTau.csv', oneOverTau, 'vin;1/tau_up;1/tau_down\n');
    
    print_info("analytic calculation of metastable voltages done")

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# determine metastability by transient simulations and predicting backwards

def get_meta_trans(circuit):
    print_info("determining metastable voltages by transients")

    slopeFittingCount = 1
    slopeSkipEnd = 2
    
    Iout = read_Iout(DATA_FOLDER + DIR_NAME + 'Iout.csv')
    meta = read_meta(DATA_FOLDER + DIR_NAME + 'meta.csv')

    start_time = time.time()
    
    #-----------------------------------------------------------------
    
    # get lower value of metastable region
    limits = [int(i) for i in meta[0]]
    meta = meta[1:]

    IoutColIdx = 0
    while Iout[0][IoutColIdx] < meta[limits[0]][0]:
        IoutColIdx += 1
#    IoutColIdx += 1

    #-----------------------------------------------------------------

    oneOverTau = [ [], [], [] ]
    metaPoints = [ [], [], [], [] ]
  
    while Iout[0][IoutColIdx] < meta[limits[1]][0]:
       
#        print_info("starting transient simulations for vin=%s"%Iout[0][IoutColIdx])

#        if Iout[0][IoutColIdx] != 0.3969:
#        if Iout[0][IoutColIdx] != 0.4041:
#            IoutColIdx += 1
#            continue
        
        # skip first derivative which are positive as stable value not exactly at 0V
        IoutRowIdx = len(Iout[1])-1
        while (Iout[2][IoutRowIdx,IoutColIdx] > 0) :
            IoutRowIdx -= 1
        
        # go upwards until metastable value crossed
        while (Iout[2][IoutRowIdx,IoutColIdx] < 0) :
            IoutRowIdx -= 1

        oneOverTau[0].append(Iout[0][IoutColIdx])

        # print(IoutRowIdx)
        # print(IoutColIdx)
        # print(Iout[2][IoutRowIdx:0:-1, IoutColIdx])
        # print(Iout[2][IoutRowIdx, IoutColIdx])
        
        if IoutRowIdx > slopeFittingCount + slopeSkipEnd :  
            [metaUp, ootauUp] = do_trans_tau(Iout[0][IoutColIdx], Iout[1][IoutRowIdx])
            oneOverTau[1].append(ootauUp)
        else:
            oneOverTau[1].append(0)
            metaUp = -1
            
        if IoutRowIdx < len(Iout[1])-slopeFittingCount - slopeSkipEnd -1:
            [metaDown, ootauDown] = do_trans_tau(Iout[0][IoutColIdx], Iout[1][IoutRowIdx+1])
            oneOverTau[2].append(ootauDown)
        else:
            oneOverTau[2].append(0)
            metaDown = -1
        
        if (metaUp > 0) and (metaDown > 0):           
            metaPoints[0].append(Iout[0][IoutColIdx])
            Vm = get_crossing(metaDown, 1/oneOverTau[2][-1],
                              metaUp, 1/oneOverTau[1][-1])
            metaPoints[1].append(Vm)
            metaPoints[2].append(metaUp)
            metaPoints[3].append(metaDown)
            print_info("%s  -->   %s/%s/%s    <--   %s"%(Iout[1][IoutRowIdx+1],
                                                         metaDown, metaPoints[1][-1], metaUp,
                                                         Iout[1][IoutRowIdx]))
        IoutColIdx += 1

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
    write_csv_column(DATA_FOLDER + DIR_NAME + 'metaTransTau.csv', oneOverTau, 'vin; 1/tau_up; 1/tau_down\n');
    
    print_info("determining metastable voltages by transients done")

    
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# determine metastable value by using metastability inversion

def get_inv_meta_trans(circuit):
    
    print_info("starting inverted metastable transient analysis")
    
    Iout = read_Iout(DATA_FOLDER + DIR_NAME + 'Iout.csv')
    meta = read_meta(DATA_FOLDER + DIR_NAME + 'meta.csv')

    start_time = time.time()
    
    #-----------------------------------------------------------------
    
    # get lower value of metastable region
    limits = [int(i) for i in meta[0]]
    meta = meta[1:]

    IoutColIdx = 0
    while Iout[0][IoutColIdx] < meta[limits[0]][0]:
        IoutColIdx += 1
    IoutColIdx += 1

    #-----------------------------------------------------------------

    fileName = CIRCUIT_FOLDER + circuit + '/inv_meta_trans.sp'
    metaPoints = [[], []]
    counter=0

    while Iout[0][IoutColIdx] < meta[limits[1]][0]:

        vin = Iout[0][IoutColIdx]        
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

        IoutColIdx += 1

    print_info("get_inv_meta_trans took %s seconds"%(time.time()-start_time))
        
    write_csv_column(DATA_FOLDER + DIR_NAME + 'invMetaTrans.csv', metaPoints, 'vin; vmeta\n');
    
    print_info("inverted metastable transient analysis done")

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# determine metastability using DC analysis

def get_meta_dc(circuit):
    
    print_info("starting metastable dc analysis")

    meta = read_meta(DATA_FOLDER + DIR_NAME + 'meta.csv')
    dcData = []
    
    start_time = time.time()
    
    #-----------------------------------------------------------------
    
    # get lower value of metastable region
    limits = [int(i) for i in meta[0]]
    meta = meta[1:]

    voutInit = meta[limits[0]+(limits[1]-limits[0])/10][2]

    iterations = [ [voutInit, 'meta'], ['supp', 'upper'], ['0.0V', 'lower']]
    
    #-----------------------------------------------------------------

    fileName = CIRCUIT_FOLDER + circuit + '/dc.sp'

    for entry in iterations:
        spiceFileName = SPICE_FOLDER + DIR_NAME + 'dc_%s.sp'%entry[1]

        if not os.path.isfile(spiceFileName[:-3]+'.sw0'):
            cmd = "sed -e 's/<sed>lower<sed>/%s/' -e 's/<sed>upper<sed>/%s/' -e 's/<sed>step<sed>/%s/' "\
                "-e 's/<sed>out<sed>/%s/' "\
                %(meta[limits[0]][0], meta[limits[1]][0], meta[1][0]-meta[0][0], entry[0]) + fileName  + \
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

        data = read_hspice(spiceFileName[:-3]+'.sw0', 2)
        
        if dcData == []:
            dcData.append(data[0])
                
        dcData.append(data[1])
#        dcData.append(data[2])
#        dcData.append(data[3])
#        dcData.append(data[4])

    print_info("get_meta_dc took %s seconds"%(time.time()-start_time))
        
    write_csv_column(DATA_FOLDER + DIR_NAME + 'metaDC.csv', dcData, 'vin;vmeta;vupper;vlower\n');

    print_info("metastable dc analysis done")

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# calculate loop amplification in determined metastable values

def get_loop_amplification(circuit):

    print_info("determining loop amplification in metastable points")
    
    meta = read_meta(DATA_FOLDER + DIR_NAME + 'meta.csv')
    limits = [int(i) for i in meta[0]]
    meta = meta[1:]    

    data = [[],[],[],[]]
   
    start_time = time.time()
    
    #-----------------------------------------------------------------

#    fileName = CIRCUIT_FOLDER + circuit + '/amp.sp'
    
    for idx in range(limits[0], limits[1]+1, 1):
        
        # if not in metastable range
        if len(meta[idx]) < 4:
            continue
        
        vin = meta[idx][0]
        vout = meta[idx][2]
        
        print_info("started vin=%s"%vin)

        cutoff_freq, unity_freq, gain = get_amp(vin, vout)
        
        data[0].append(vin)
        if gain != False :
            data[1].append(gain)
        else :
            data[1].append(data[1][-1])

        if cutoff_freq != False :
            data[2].append(cutoff_freq)
        else :
#            data[2].append(data[2][-1])
            data[2].append(0)

        if unity_freq != False :
            data[3].append(unity_freq)
        else :
            data[3].append(data[3][-1])
        
    plt.figure()
    plt.plot(data[0], data[1], 'b-')
    plt.grid()
    plt.xlabel('Vin')
    plt.ylabel('loop gain')
    plt.savefig(FIG_FOLDER+DIR_NAME[:-1]+'_amp.png')
    write_csv_column(DATA_FOLDER + DIR_NAME + 'amp.csv', data, 'vin;gain;cutoff_freq;unity_freq\n');

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

#    fileName = CIRCUIT_FOLDER + circuit + '/amp.sp'

    idx = (limits[0]+ limits[1])/2
    vin = meta[idx][0]
    print_info("using vin=%s"%vin)
    stringVin = ("%.7f"%vin).replace('.','')

    data = [[vin],[meta[idx][2]]]
    
    for vout in np.linspace(meta[idx][2]*(1-factor),meta[idx][2]*(1+factor), 10):

        print_info("started vout=%s"%vout)
        cutoff_freq, unity_freq, gain = get_amp(vin, vout)
        
        data[0].append(vout)
        #amps[1].append(10**(amp/20))
        data[1].append(cutoff_freq*2*math.pi * gain)

    write_csv_column(DATA_FOLDER + DIR_NAME + 'amp_%s.csv'%stringVin, data, 'vout; gain_bw\n');

    print_info("get_loop_amplification_vin took %s seconds"%(time.time()-start_time))

#********************************************************************************        
    
def get_amp(vin, vout):

    amps = []
    
    fileName = CIRCUIT_FOLDER + circuit + '/amp.sp'
    
    stringVin = ("%.7f"%vin).replace('.','')
    stringVout = ("%.7f"%vout).replace('.','')    
        
    spiceFileName = SPICE_FOLDER + DIR_NAME + 'amp_%s_%s.sp'%(stringVin, stringVout)
  
#    if not os.path.isfile(spiceFileName[:-3]+'.ac0'):
    if not os.path.isfile(spiceFileName[:-3]+'.aaa'):
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

    cmd = "grep cutoff_freq= %s.lis"%(spiceFileName[:-3])
    code = subprocess.Popen(cmd,shell = True ,  stdout=subprocess.PIPE)
    try :
        cutoff_freq = float( code.stdout.read().split(' ')[2] )
    except:
        cutoff_freq = False

    cmd = "grep loop_gain_at_min_freq %s.lis"%(spiceFileName[:-3])
    code = subprocess.Popen(cmd,shell = True ,  stdout=subprocess.PIPE)
    try:
        gain = float( code.stdout.read().split('=')[1] )
        gain = 10**(gain/20)
    except :
        gain = False
    
    cmd = "grep unity_gain_freq %s.lis"%(spiceFileName[:-3])
    code = subprocess.Popen(cmd,shell = True ,  stdout=subprocess.PIPE)
    try:
        unity_freq = float( code.stdout.read().split('=')[1] )
    except:
        unity_freq = False
   
    data = read_hspice(spiceFileName[:-3]+'.ac0',3)
    
    f = plt.figure()
    ax = f.add_subplot(2, 1, 1, ylabel='gain')
    ax.plot(data[0], data[1])
    plt.semilogx()

    ax = f.add_subplot(2, 1, 2, ylabel='phase')        
    ax.plot(data[0], data[2])
    plt.semilogx()        
    plt.savefig(FIG_FOLDER+DIR_NAME[:-1]+'_amp_%s_%s.png'%(stringVin, stringVout))

    write_csv_column(DATA_FOLDER + DIR_NAME + 'amp_%s_%s.dat'%(stringVin, stringVout),
                     data, 'freq;gain;phase\n')
    
    return cutoff_freq, unity_freq, gain
    
   
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# get loop characteristic

def get_loop_characteristic(circuit):

    print_info("determining loop characteristic in metastable points")

    meta = read_meta(DATA_FOLDER + DIR_NAME + 'meta.csv')
    limits = [int(i) for i in meta[0]]
    meta = meta[1:]    
 
    start_time = time.time()
    
    #-----------------------------------------------------------------

    fileName = CIRCUIT_FOLDER + circuit + '/ctrl.sp'    

    for idx in range(limits[0], limits[1], 1):

        # if not in metastable range
        if len(meta[idx]) < 4:
            continue
        
        vin = meta[idx][0]
        vout = meta[idx][2]
        
        print_info("started vin=%s"%vin)
        
        stringVin = ("%.7f"%vin).replace('.','')
        stringVout = ("%.7f"%vout).replace('.','')    
        
        spiceFileName = SPICE_FOLDER + DIR_NAME + 'ctrl_%s_%s.sp'%(stringVin, stringVout)

        if not os.path.isfile(spiceFileName[:-3]+'.aaa') :
        
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

        data = read_hspice(spiceFileName[:-3]+'.ac0',3)

        f = plt.figure()
        ax = f.add_subplot(2, 1, 1, ylabel='gain')
        ax.plot(data[0], data[1])
        plt.semilogx()

        ax = f.add_subplot(2, 1, 2, ylabel='phase')        
        ax.plot(data[0], data[2])
        plt.semilogx()        
        plt.savefig(FIG_FOLDER+DIR_NAME[:-1]+'_bode_%s_%s.png'%(stringVin, stringVout))

        write_csv_column(DATA_FOLDER + DIR_NAME + 'bode_%s_%s.dat'%(stringVin, stringVout),
                         data, 'freq;gain;phase\n')
        
        data = read_hspice(spiceFileName[:-3]+'.tr0',5)
        for i in range(len(data)):
            data[i] = data[i][::10]

        plt.figure()
        plt.plot(data[0], data[1], label='vin')
        plt.plot(data[0], data[2], label='vout')
        plt.savefig(FIG_FOLDER+DIR_NAME[:-1]+'_jump_%s_%s.png'%(stringVin, stringVout))
        
        write_csv_column(DATA_FOLDER + DIR_NAME + 'jump_%s_%s.dat'%(stringVin, stringVout),
                         data, 'time;vin;vout;imeas;ictrl\n')
        
    print_info("characterizing loop done")
        
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def evaluate_meta(circuit):
   
    metaLine = read_meta(DATA_FOLDER + DIR_NAME + 'meta_line.csv')
    meta = read_meta(DATA_FOLDER + DIR_NAME + 'meta.csv')
    limits = [int(i) for i in meta[0]]
    meta = meta[1:]
    
    fileName = DATA_FOLDER + DIR_NAME + 'metaIout.csv'
    if not os.path.isfile(fileName):
        get_meta_Iout(circuit)
    metaIout = read_csv(fileName)
    
    fileName = DATA_FOLDER + DIR_NAME + 'metaTrans.csv'
    if not os.path.isfile(fileName):
        get_meta_trans(circuit)
    metaTrans = read_csv(fileName)

    fileName = DATA_FOLDER + DIR_NAME + 'metaTrans.csv'
#    fileName = DATA_FOLDER + DIR_NAME + 'invMetaTrans.csv'
    if not os.path.isfile(fileName):
        get_inv_meta_trans(circuit)
    invMetaTrans = read_csv(fileName)

    fileName = DATA_FOLDER + DIR_NAME + 'metaDC.csv'
    if not os.path.isfile(fileName):
        get_inv_meta_dc(circuit)
    invMetaDC = read_csv(fileName)
    
    #-----------------------------------------------------------------

    printSPICE = row_to_column(metaLine)
    printIout = row_to_column(metaIout)
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
    plt.plot(printIout[0], printIout[1], 'g-')
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
    
    while abs(meta[metaIdx][0] -metaIout[0][0]) > 1e-8:
        metaIdx+= 1

    measured = meta[metaIdx:-1:HYSTERESIS_COUNT_MULT]
    
    outDeviation = [ [], [], [], [], [] ]
    fileName = CIRCUIT_FOLDER + circuit + '/eval.sp'

    tmpIout = [metaIout[idx][1] - measured[idx][2] for idx in range(len(metaIout))]
    tmpTrans = [metaTrans[idx][1] - measured[idx][2] for idx in range(len(metaTrans))]
    tmpInvMetaTrans = [invMetaTrans[idx][1] - measured[idx][2] for idx in range(len(invMetaTrans))]
    tmpInvMetaDC = [invMetaDC[idx][1] - meta[limits[0]:limits[1]+1][idx][2] for idx in range(len(invMetaDC))]
    tmpLinear = [printLinear[1][idx] - meta[limits[0]:limits[1]+1][idx][2] for idx in range(len(printLinear[0]))]
       
    plt.figure()
    plt.plot(printIout[0], tmpIout, 'g-', label='static prediction')
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

    tmpIout = [np.abs(i) for i in tmpIout]
    tmpTrans = [np.abs(i) for i in tmpTrans]
    tmpInvMetaTrans = [np.abs(i) for i in tmpInvMetaTrans]
    tmpInvMetaDC = [np.abs(i) for i in tmpInvMetaDC]
    tmpLinear = [np.abs(i) for i in tmpLinear]

    write_csv_column(DATA_FOLDER + DIR_NAME + 'metaIoutDiff.csv', [printIout[0], tmpIout], 'vin; vdiff\n');    
    write_csv_column(DATA_FOLDER + DIR_NAME + 'metaTransDiff.csv', [printTrans[0], tmpTrans], 'vin; vdiff\n');
    write_csv_column(DATA_FOLDER + DIR_NAME + 'invMetaTransDiff.csv', [printInvMetaTrans[0], tmpInvMetaTrans], 'vin; vdiff\n');
    write_csv_column(DATA_FOLDER + DIR_NAME + 'DCDiff.csv', [printInvMetaDC[0], tmpInvMetaDC], 'vin; vdiff\n');
    
    plt.figure()
    plt.semilogy(printIout[0], tmpIout, 'g-', label='static prediction')
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
    
    return
    
    styles = ['g-', 'b-', 'c-', 'm-', 'k']
    labels = ['static prediction', 'dynamic prediction', 'inverted meta trans', 'inverted meta dc', 'binary search']

    # output file name, position in outDeviation, array holding data, entry to pick from data
    params = [['eval_dVout',2, metaIout,1],
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

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


# def get_tau(Iout, IoutRowIdx, IoutColIdx, dc=False):

#     slopeFittingCount = 3
#     slopeSkipEnd = 2

#     taus = []

#     if IoutRowIdx < len(Iout[1])-slopeFittingCount - slopeSkipEnd -1:

#         polyParams = np.polyfit(Iout[1][IoutRowIdx+1:IoutRowIdx+1+slopeFittingCount],
#                                 Iout[2][IoutRowIdx+1:IoutRowIdx+1+slopeFittingCount,
#                                          IoutColIdx].flatten().tolist()[0],1)
#         ootau = polyParams[0]
        
#         if dc == False:
#             # run transient simulation starting in the metastable prediction from the DC analysis
#             [metaDown, ootauDown] = do_trans_tau(Iout[0][IoutColIdx], -polyParams[1]/ootau,
#                                                  [Iout[1][IoutRowIdx+1:],
#                                                   Iout[2][IoutRowIdx+1:, IoutColIdx].flatten().tolist()[0]])

#             taus.append(ootauDown)

#             #amp = get_amp(Iout[0][IoutColIdx], Iout[1][IoutRowIdx+1])
#             #taus.append(amp)
                        
#         else:
            
#             taus.append(ootau)

#             plt.figure()
#             plt.plot(Iout[1][IoutRowIdx+1:IoutRowIdx+1+slopeFittingCount],
#                                     Iout[2][IoutRowIdx+1:IoutRowIdx+1+slopeFittingCount,
#                                              IoutColIdx].flatten().tolist()[0], 'b*-')

#             print("starting in (vin, vout) = (%.5f, %.5f)"%(Iout[0][IoutColIdx], Iout[1][IoutRowIdx+1]))

#             p1 = np.poly1d(polyParams)
#             y = [p1(x) for x in Iout[1][IoutRowIdx+1:IoutRowIdx+1+slopeFittingCount]]
#             plt.plot(Iout[1][IoutRowIdx+1:IoutRowIdx+1+slopeFittingCount], y, 'r-')
#             plt.grid()
#             plt.xlabel('Vin')
#             plt.ylabel('I_out')
#             plt.savefig(FIG_FOLDER+DIR_NAME[:-1]+'_tau_map_%.3f_down.png'%Iout[0][IoutColIdx])
        
#     else:
#         taus.append(0)

#     if (IoutRowIdx > slopeFittingCount + slopeSkipEnd) :

#         polyParams = np.polyfit(Iout[1][IoutRowIdx:IoutRowIdx-slopeFittingCount:-1],
#                                 Iout[2][IoutRowIdx:IoutRowIdx-slopeFittingCount:-1,
#                                          IoutColIdx].flatten().tolist()[0],1)
#         ootau = polyParams[0]
        
#         if dc == False:
#             [metaUp, ootauUp] = do_trans_tau(Iout[0][IoutColIdx],  -polyParams[1]/ootau,
#                                              [Iout[1][IoutRowIdx:0:-1],
#                                               Iout[2][IoutRowIdx:0:-1, IoutColIdx].flatten().tolist()[0]])
            
#             taus.append(ootauUp)

#             #amp = get_amp(Iout[0][IoutColIdx], Iout[1][IoutRowIdx+1])
#             #taus.append(amp)
#         else:
        
#             print("starting in (vin, vout) = (%.5f, %.5f)"%(Iout[0][IoutColIdx], Iout[1][IoutRowIdx]))

#             plt.figure()
#             plt.plot(Iout[1][IoutRowIdx:IoutRowIdx-slopeFittingCount:-1],
#                                     Iout[2][IoutRowIdx:IoutRowIdx-slopeFittingCount:-1,
#                                              IoutColIdx].flatten().tolist()[0], 'b*-')

#             p1 = np.poly1d(polyParams)
#             y = [p1(x) for x in Iout[1][IoutRowIdx:IoutRowIdx-slopeFittingCount:-1]]
#             plt.plot(Iout[1][IoutRowIdx:IoutRowIdx-slopeFittingCount:-1],y, 'r-')
#             plt.grid()
#             plt.xlabel('Vin')
#             plt.ylabel('I_out')
#             plt.savefig(FIG_FOLDER+DIR_NAME[:-1]+'_tau_map_%.3f_up.png'%Iout[0][IoutColIdx])
        
#     else:
#         taus.append(0)

#     return taus
    
# #********************************************************************************    

# def get_tau_from_map(circuit):

#     print_info("starting determination of tau based on Iout map")
    
#     tauData = [[], [], [], []]
    
#     Iout = read_Iout(DATA_FOLDER + DIR_NAME + 'Iout.csv')

#     start_time = time.time()
    
#     #-----------------------------------------------------------------

#     for colIdx in range(len(Iout[0])):
#         print("starting vin=%s"%Iout[0][colIdx])
#         for rowIdx in range(1,len(Iout[1])):

#             # metastable point crossed
#             # note that we go from vout=supp towards vout=gnd
#             if (Iout[2][rowIdx, colIdx] < 0 ) and (Iout[2][rowIdx-1, colIdx] > 0):
#                 tauData[0].append(Iout[0][colIdx])
#                 taus=get_tau(Iout, rowIdx-1, colIdx, False)
                
#                 tauData[1].append(taus[0])
#                 tauData[2].append(taus[1])
#                 tauData[3].append( (taus[0]+taus[1])/2 )
#                 break

#     #-----------------------------------------------------------------

#     print_info("get_tau_from_map took %s seconds"%(time.time()-start_time))
        
#     plt.figure()
#     plt.plot(tauData[0], tauData[1], 'b-')
#     plt.plot(tauData[0], tauData[2], 'g-')
#     plt.plot(tauData[0], tauData[3], 'c-')
#     plt.grid()
#     plt.xlabel('Vin')
#     plt.ylabel('1/tau')
#     plt.savefig(FIG_FOLDER+DIR_NAME[:-1]+'_tau_map.png')

#     write_csv_column(DATA_FOLDER + DIR_NAME + 'TauFromMap.csv', tauData, 'vin;tau_d;tau_u;tau_avg\n');
    
#     print_info("determination of tau done")
    

#********************************************************************************    

def get_tau(circuit):

    print_info("starting determination of tau based on metastable values from Bisection")
    
    meta = read_meta(DATA_FOLDER + DIR_NAME + 'meta.csv')

    printData = [[],[]]
    start_time = time.time()
    
    #-----------------------------------------------------------------
    
    # get lower value of metastable region
    limits = [int(i) for i in meta[0]]
    meta = meta[1:]
    
    #-----------------------------------------------------------------
    
#    for idx in range(limits[0], limits[1]+1):
    for idx in range(limits[0], limits[1]+1, 1):        

#        if (meta[idx][0] < 0.3) or (meta[idx][0] > 0.5):
#            continue
        
        [metaVal, ootau] = do_trans_tau(meta[idx][0], meta[idx][2], 'transTau')

        if metaVal < 0:
            print_info("for vin=%s the maximum derivative was achieved at the beginning\n"%meta[idx][0])
            continue
        
        printData[0].append(meta[idx][0])
        printData[1].append(ootau)

    #-----------------------------------------------------------------

    print_info("get_tau took %s seconds"%(time.time()-start_time))
        
    plt.figure()
    plt.plot(printData[0], printData[1], 'b-')
    plt.grid()
    plt.xlabel('Vin')
    plt.ylabel('1/tau')
    plt.savefig(FIG_FOLDER+DIR_NAME[:-1]+'_tau.png')

    write_csv_column(DATA_FOLDER + DIR_NAME + 'tau.csv', printData, 'vin;1/tau\n');
    
    print_info("determination of tau done")

#********************************************************************************    

def get_tau_dc(circuit):

    print_info("starting determination of tau based on metastable values from DC predictions")
    
    meta = read_meta_dc(DATA_FOLDER + DIR_NAME + 'metaDC.csv')

    printData = [[],[]]
    tolerance = 1e-3
    start_time = time.time()
    
    #-----------------------------------------------------------------
    
    for idx in range(0,len(meta),5):

        # procedure works not properly near the borders of metastability
        if (abs(meta[idx][1] - meta[idx][3]) < tolerance) or (abs(meta[idx][1] - meta[idx][5]) < tolerance):
            continue
        
        [metaVal, ootau] = do_trans_tau(meta[idx][0], meta[idx][1], 'transTauDC', meta[idx][2])

        if metaVal < 0:
            print_info("for vin=%s the maximum derivative was achieved at the beginning\n"%meta[idx][0])
            continue
        
        printData[0].append(meta[idx][0])
        printData[1].append(ootau)

    #-----------------------------------------------------------------

    print_info("get_tau_dc took %s seconds"%(time.time()-start_time))
        
    plt.figure()
    plt.plot(printData[0], printData[1], 'b-')
    plt.grid()
    plt.xlabel('Vin')
    plt.ylabel('1/tau')
    plt.savefig(FIG_FOLDER+DIR_NAME[:-1]+'_tau.png')

    write_csv_column(DATA_FOLDER + DIR_NAME + 'TauTransDC.csv', printData, 'vin;tau\n');
    
    print_info("determination of tau done")

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# matches the currents from static and transient simulation
# this is required to investigate the differences which are the results of
#   the finite speed of the feedback loop

def match_static_trans(circuit):

    print_info("starting to match static to transient results")
    Iout = read_Iout(DATA_FOLDER + DIR_NAME + 'Iout.csv')
    meta = read_meta(DATA_FOLDER + DIR_NAME + 'meta.csv')
    
    start_time = time.time()

    #-----------------------------------------------------------------
    
    # get lower value of metastable region
    limits = [int(i) for i in meta[0]]
    meta = meta[1:]

    IoutColIdx = 0
    while Iout[0][IoutColIdx] < meta[limits[0]][0]:
        IoutColIdx += 1
#    IoutColIdx += 1

    #-----------------------------------------------------------------

    while Iout[0][IoutColIdx] < meta[limits[1]][0]:
       
        # skip first derivative which are positive as stable value not exactly at 0V
        IoutRowIdx = len(Iout[1])-1
        while (Iout[2][IoutRowIdx,IoutColIdx] > 0) :
            IoutRowIdx -= 1
        
        # go upwards until metastable value crossed
        while (Iout[2][IoutRowIdx,IoutColIdx] < 0) :
            IoutRowIdx -= 1

    
    
    # Iout = read_Iout(DATA_FOLDER + DIR_NAME + 'Iout.csv')
    # startName = 'trans_'

    # fileList = os.listdir(SPICE_FOLDER + DIR_NAME)
    # fileList.sort()
    
    # for fileName in fileList:
        
    #     if not fileName.startswith(startName):
    #         continue
        
    #     if not fileName.endswith('.tr0'):
    #         continue

    #     plotData = [[],[],[]]        
    #     parts = fileName[:-4].split('_')
    #     vin = float(parts[-2])/1e7
    #     vout = float(parts[-1][:-4])/1e7
               
    #     # Step #1: Determine static simulation point that will be crossed next
        
    #     IoutColIdx = 0
    #     # safer than equality for float values
    #     while abs(vin - Iout[0][IoutColIdx]) > 1e-10:
    #         IoutColIdx += 1

    #     IoutRowIdx =0
    #     # Note that Iout[1][IoutRowIdx] decreases with incresing index!
    #     while (Iout[1][IoutRowIdx] > vout[0]):
    #         IoutRowIdx += 1
          

        for shift in [-4,5]:
            calculate_matching(Iout, IoutColIdx, IoutRowIdx+shift)

        IoutColIdx += 1
            
    print_info("match_static_trans took %s seconds"%(time.time()-start_time))

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def calculate_matching(Iout, IoutColIdx, IoutRowIdx):

    plotData = [[],[],[]]
    startName = 'transMatch'
    
    do_trans_tau(Iout[0][IoutColIdx], Iout[1][IoutRowIdx], startName, False)
        
#        if vin != 0.3969:
#        if vin != 0.4041:
#            continue

    stringVin = ("%.7f"%Iout[0][IoutColIdx]).replace('.','')
    stringVout = ("%.7f"%Iout[1][IoutRowIdx]).replace('.','') 
    fileName = startName + '_%s_%s.tr0'%(stringVin, stringVout)

    print_info("processing file " + fileName);
    data = read_hspice(SPICE_FOLDER + DIR_NAME + fileName, 4)
    vout = data[1]
    itrans = data[3]

    if (vout[-1] > vout[0]):
        up = True
    else:
        up = False
    
    for idx in range(len(data[0])):

        # Step n+1: If static simulation point reached by transient trace add
        # value of Iout at current simulation time and jump to next static
        # simulation point

        if up == True and vout[idx] > Iout[1][IoutRowIdx]:
            plotData[0].append(data[0][idx])
            plotData[1].append(Iout[2][IoutRowIdx, IoutColIdx])
            plotData[2].append(plotData[1][-1] / itrans[idx])
            IoutRowIdx -= 1

        if up == False and vout[idx] < Iout[1][IoutRowIdx]:
            plotData[0].append(data[0][idx])
            plotData[1].append(Iout[2][IoutRowIdx, IoutColIdx])
            plotData[2].append(plotData[1][-1] / itrans[idx])
            IoutRowIdx += 1

        if IoutRowIdx < 0 or IoutRowIdx > len(Iout[1])-1 :
            break

    plt.figure()
    tmpY = [np.log(abs(i)) for i in itrans]
    plt.plot(data[0], tmpY, 'b-')

    tmpY = [np.log(abs(i)) for i in plotData[1]]
    plt.plot(plotData[0], tmpY, 'g*')
    plt.grid()
    plt.savefig(FIG_FOLDER + DIR_NAME[:-1] + '_match' + fileName[len(startName):-4] + '.png')

    write_csv_column(DATA_FOLDER + DIR_NAME + 'iout_match' + fileName[len(startName):-4] + '.csv', plotData,
             'time;iout;P\n')

    skip = len(data[0])/1000
    Cout = []
    for idx in range(len(data[3][::skip])):
        if data[2][::skip][idx] == 0:
            Cout.append(0)
        else:
            Cout.append((data[3][::skip][idx]*1e15) / data[2][::skip][idx])
            
    write_csv_column(DATA_FOLDER + DIR_NAME + 'iout_trans' + fileName[len(startName):-4] + '.csv',
                     [data[0][::skip], data[1][::skip], data[2][::skip], data[3][::skip], Cout],
                     'time;vout;dVout;iout;Cout[fF]\n') 
    
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def prepare_simulation(circuit, technology, suffix):

    global DIR_NAME
    
    if os.path.islink('technology'):
        os.remove('technology')

    if os.path.isfile(TECH_FOLDER+technology):
        os.symlink(TECH_FOLDER+technology, 'technology')
    else:
        print_error("stated technology '%s' does not exist!"%technology)
        sys.exit(1)

    DIR_NAME = circuit + '_' + technology + '/'

    if suffix != '':
        DIR_NAME = DIR_NAME[:-1] + '_' + suffix + '/'

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
        
    print("usage: python %s <circuit> <technology> <analysis> [path suffix]"%sys.argv[0])
    print("\nmeta ... calculate hysteresis and metastable line using bisection")
    print("map ... print map of Iout over the Vin-Vout plane")
    print("Iout ... calculate metastable values based on Iout map")
    print("tau ... derive tau values")
    print("trans ... calculate metastable values based on transient simulations")
    print("match ... match static and transient simulations")
    print("inv ... calculate metastable values based on metastability inversion")
    print("dc ... calculate metastable values based on DC analysis")
    print("amp ... determine loop amplification in metastable values")
    print("amp_vin ... loop amplification for single input voltage but multiple output voltages")
    print("ctrl ... determine loop characteristic")    
    print("eval ... evaluate all estimations")
    print("all ... execute everything")
        
#********************************************************************************
# main ###
#********************************************************************************

if __name__ == '__main__':

    if len(sys.argv) < 4 or len(sys.argv) > 5:
        print_usage()
        sys.exit()

    circuit=sys.argv[1]
    technology=sys.argv[2]
    mode=sys.argv[3]
    if len(sys.argv) == 5:
        suffix = sys.argv[4]
    else:
        suffix = ''

    prepare_simulation(circuit, technology, suffix)
    
    if (mode == "meta"):
        get_meta(circuit)
    elif (mode == "map"):
        get_Iout(circuit)
    elif (mode == "Iout"):
        get_meta_Iout(circuit)
    elif (mode == "tau"):
#        get_tau_from_map(circuit)
        get_tau(circuit)
    elif (mode == "tau_dc"):
        get_tau_dc(circuit)        
    elif (mode == "trans"):
        get_meta_trans(circuit)
    elif (mode == "match"):
        match_static_trans(circuit)
    elif (mode == "inv"):
        get_inv_meta_trans(circuit)
    elif (mode == "dc"):
        get_meta_dc(circuit)
    elif (mode == "amp"):
        get_loop_amplification(circuit)
    elif (mode == "amp_vin"):
        get_loop_amplification_vin(circuit)
    elif (mode == "ctrl"):
        get_loop_characteristic(circuit)
    elif (mode == "eval"):
        evaluate_meta(circuit)
    elif (mode == "all"):
        get_meta(circuit)
        get_Iout(circuit)
        get_meta_trans(circuit)
        get_meta_Iout(circuit)
        get_inv_meta_dc(circuit)
        get_inv_meta_trans(circuit)
        evaluate_meta(circuit)
    else:
        print_error("unknown mode")
        print_usage()
