Transient simulation of standard 6T Schmitt Trigger
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

.PARAM inVal=0.6V  outVal=0.8V
.PARAM simTime=3000ps
.PARAM P=1.4 D=0.1 I=1

.TEMP 25
.OPTION
+ INGOLD=2
+ MEASOUT=1
+ PARHIER=LOCAL
+ POST=2
+ PROBE
+ BRIEF
+ ACCURATE
+ ABSVAR=0.05
+ DELMAX=50fs
+ OPTLST = 1
+ MEASDGT=10
+ RUNLVL=5
*+ METHOD=GEAR

.include technology
.include common.sp

*************************************************

VCC 5 0 supp
VIN 1 0 inVal

XP1 3 1 5 5 pmos
XP2 2 1 3 5 pmos
XP3 0 2 3 5 pmos

XN1 4 1 0 0 nmos
XN2 2 1 4 0 nmos
XN3 5 2 4 0 nmos

Vmeas 2 8 0
HI in  0  Vmeas 1
*R_fc in in3 10
*C_fc in3 0 500fF

* Proportional
FP 8 0 Vmeas P

* Integral
xint in integv  integrator
GI 8 0 integv 0 I

* Differential
xdiff in diffv  differentiator
GD 8 0 diffv 0 D

COUT 8 0 0.002p

.MEAS TRAN finalVal FIND V(8) AT=simTime
.PROBE TRAN I(Vmeas) I(FP) I(GI) I(GD) V(8) V(integv) V(diffv)
.IC 1=inVal 2=outVal
.TRAN 200fs simTime

.END
