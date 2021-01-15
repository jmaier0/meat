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

.PARAM inVal=<sed>vin<sed>V  outVal=<sed>vout<sed>V
.PARAM intVal='supp/2' jumpVal=10e-9

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
+ pz_num = 15
+ PZABS=1e-4
+ PZTOL=1e-8
+ RITOL=1e-4

.include technology
.include parameters.sp

VR R 0 ref
VSH SUHA 0 sh
VIN IN 0 dc inVal ac 0 0
IL OUT_FB 0 pulse (0 jumpVal 0ps 0ps 0ps 20ns 100s) AC 1 0

Vmeas OUT_FB OUT dc 0 ac 0 0

E OP SUHA IN 3 opamp_amplification MAX=sh MIN=-sh

R0 OP OUT R_0
C0 OUT_FB 0 C_0

RA OUT_FB 3 R_A
RB 3 R R_B

.TRAN 1ps 1ns 
.AC DEC 10 1 10000G
.probe ac idb(Vmeas) ip(Vmeas)
.probe tran v(IN) v(OUT) i(Vmeas) i(IL)
.pz I(Vmeas) IL

.IC OUT=outVal


.END
