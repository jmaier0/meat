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

VIN IN 0 inVal
VR R 0 ref
VSH SUHA 0 sh
VLSTB OUT OUT_FB dc=0

E OP SUHA IN 3 opamp_amplification MAX=sh MIN=-sh

R0 OP OUT R_0
C0 OUT 0 C_0

RA OUT_FB 3 R_A
RB 3 R R_B

.NODESET OUT=outVal
.AC DEC 10 1 10000G
.lstb mode=single vsource=vlstb
.probe ac lstb(db) lstb(p)

.measure LSTB unity_freq unity_gain_freq
.measure LSTB gain loop_gain_at_minifreq
.measure AC maxGain FIND lstb(db) AT=10
.measure AC cutoff_freq trig at=0 targ lstb(db) val='maxGain-3' FALL=LAST


.END
