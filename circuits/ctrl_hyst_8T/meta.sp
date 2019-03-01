determining metastable curve of 8T controllable hysteresis Schmitt Trigger
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

.PARAM inVal=<sed>vin<sed>
.PARAM vout_VL=<sed>voutVL<sed> vout_VH=<sed>voutVH<sed>
.PARAM vout_start='(vout_VL+vout_VH)/2'

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
+ DELMAX=100fs
+ OPTLST = 1

.include technology

VCC 5 0 supp
VIN 1 0 dc
VOUT 2 0 outVal
VB 9 0 vbVal

XP1 3 1 5 5 pmos
XP2 2 1 3 5 pmos
XP3 6 2 3 5 pmos
XP4 0 9 6 5 pmos

XN1 4 1 0 0 nmos
XN2 2 1 4 0 nmos
XN3 7 2 4 0 nmos
XN4 5 9 7 0 nmos

.measure DC optMeasure max i(VOUT) GOAL=0

.model optMod1 OPT METHOD=BISECTION RELIN=1e-4 ITROPT=40
.param outVal=optFunc1(vout_start, vout_VL, vout_VH)
.DC VIN inVal inVal 1 SWEEP OPTIMIZE=optFunc1 RESULTS=optMeasure
+ MODEL=optMod1

.DC VIN inVal inVal 1
.PROBE DC V(2)

.END
