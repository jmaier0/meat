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

.PARAM inVal=<sed>in<sed>V  outVal=<sed>out<sed>V
.PARAM simTime='3000ps*<sed>mult<sed>'
.PARAM P=50
*P=<sed>P<sed>
*PARAM D=0 I=0

.TEMP 25
.OPTION
+ INGOLD=2
+ MEASOUT=1
+ MEASDGT=10
+ PARHIER=LOCAL
+ POST=2
+ PROBE
+ BRIEF
+ ACCURATE
+ ABSVAR=0.05
+ DELMAX=100fs
+ OPTLST = 1

.include technology
.include common.sp
.include parameters.sp

VIN IN 0 inVal
VR R 0 ref
VSH SUHA 0 sh

Vmeas OUT_FB OUT

E OP SUHA IN 3 opamp_amplification MAX=sh MIN=-sh

R0 OP OUT R_0
C0 OUT_FB 0 C_0

RA OUT 3 R_A
RB 3 R R_B

* Proportional
FP OUT 0 Vmeas P

* Integral
*xint in integv  integrator
*GI 8 0 integv 0 I

* Differential
*xdiff in diffv  differentiator
*GD 8 0 diffv 0 D

.MEAS TRAN finalVal FIND V(OUT) AT=simTime
.PROBE TRAN V(OUT) I(Vmeas) I(FP)
.IC OUT=outVal
.TRAN 200fs simTime

.END
