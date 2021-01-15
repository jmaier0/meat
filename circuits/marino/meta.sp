Simulate hysteresis of standard 6T schmitt trigger
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
.PARAM ref='supp/2' sh='supp/2'

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
.include parameters.sp

VIN IN 0 dc
VR R 0 ref
VOUT OUT 0 outVal
VSH SUHA 0 sh

E OP SUHA IN 3 opamp_amplification MAX=sh MIN=-sh

R0 OP OUT R_0
C0 OUT 0 C_0

RA OUT 3 R_A
RB 3 R R_B

.measure DC optMeasure max i(VOUT) GOAL=0

.model optMod1 OPT METHOD=BISECTION RELIN=1e-4 ITROPT=40
.param outVal=optFunc1(vout_start, vout_VL, vout_VH)
.DC VIN inVal inVal 1 SWEEP OPTIMIZE=optFunc1 RESULTS=optMeasure
+ MODEL=optMod1

.DC VIN inVal inVal 1
.PROBE DC V(OUT)

.END
