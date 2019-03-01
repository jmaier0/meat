determining gain of storage loop in 8T controllable hysteresis Schmitt Trigger
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

.PARAM inVal=<sed>vin<sed>V  outVal=<sed>vout<sed>V

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
VIN 1 0 inVal
VB 9 0 vbVal
VLSTB 2 20 dc=0

XP1 3 1 5 5 pmos
XP2 2 1 3 5 pmos
XP3 6 20 3 5 pmos
XP4 0 9 6 5 pmos

XN1 4 1 0 0 nmos
XN2 2 1 4 0 nmos
XN3 7 20 4 0 nmos
XN4 5 9 7 0 nmos

C1 2 0 loadVal

.IC 2=outVal
.ac dec '10' '0' '10'
.lstb mode=single vsource=vlstb
.measure ac maxMag max LSTB(r)
.measure lstb gain loop_gain_at_minifreq

.END
