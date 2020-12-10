Transient simulation of 8T controllable hysteresis Schmitt Trigger
*
* Copyright 2019 Juergen Maier
*
* Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
*
* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*
* author: Juergen Maier
* mail: juergen.maier@tuwien.ac.at

.PARAM inVal=<sed>in<sed>V  outVal=<sed>out<sed>V
.PARAM simTime=<sed>time<sed>ps

.TEMP 25
.OPTION
+ INGOLD=2
+ MEASOUT=1
+ PARHIER=LOCAL
+ POST=0
+ PROBE
+ BRIEF
+ ACCURATE
+ ABSVAR=0.05
+ DELMAX=100fs
+ OPTLST = 1

.include technology

VCC 5 0 supp
VIN 1 0 inVal
VB 9 0 vbVal

XP1 3 1 5 5 pmos
XP2 2 1 3 5 pmos
XP3 6 2 3 5 pmos
XP4 0 9 6 5 pmos

XN1 4 1 0 0 nmos
XN2 2 1 4 0 nmos
XN3 7 2 4 0 nmos
XN4 5 9 7 0 nmos

.MEASURE startVal FIND V(2) AT=0ps
.MEASURE stopVal FIND V(2) AT=simTime
.MEASURE diff PARAM='stopVal-startVal'
.IC 1=inVal 2=outVal
.TRAN 1ps simTime

.END
