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
+ MEASDGT = 10

.include technology
.include parameters.sp


* 153.43 GHz AC at OP input
* 16.714 GHz AC between RA and RB
* 16.714 GHz AC between OUT and RA
* no f0 between R0 and OUT
* 153.43 GHz AC at OP input

* VIN IN 0 dc=inVal ac=0
* VR R 0 ref ac=0
* VSH SUHA 0 sh ac=0
* VCA OUT OUTC dc=0 ac=1

* E OP SUHA IN 5 MAX=sh MIN=-sh opamp_amplification
* *E OP SUHA vol='(v(IN)-v(5))*(opamp_amplification)'

* R0 OP OUT R_0
* C0 OUTC 0 C_0

* RA OUTC 5 R_A
* RB 5 R R_B

* *VAC OUT 3 dc=0 ac=1

* *RX IN 3 R_A
* *RY 3 0 R_B

* .NODESET OUT=outVal
* .AC DEC 1000 1 10000G
* .probe ac vdb(OUTC) vp(OUTC)
* .pz I(Vmeas) IL

* .measure AC maxGain FIND vdb(outc) AT=1
* .measure AC cutoff_freq trig at=0 targ vdb(outc) val='maxGain-20*log10(sqrt(2))' FALL=LAST


********************************************************************
********************************************************************
********************************************************************


* f0=45.3613 GHz
* VIN IN 0 inVal
* VR R 0 ref ac=0
* VSH SUHA 0 sh ac=0
* VLSTB OUT OUT_FB dc=0

* E OP SUHA IN 3 MAX=sh MIN=-sh opamp_amplification
* *E OP 0 vol='(v(IN)-v(3))*(opamp_amplification)'

* R0 OP OUT R_0
* C0 OUT 0 C_0

* RA OUT_FB 3 R_A
* RB 3 R R_B

* .NODESET OUT=outVal
* .AC OCT 1000 1 10000G
* .lstb mode=single vsource=vlstb
* .probe ac lstb(db) lstb(p)

* .measure LSTB unity_freq unity_gain_freq
* .measure LSTB gain loop_gain_at_minifreq
* .measure AC maxGain FIND lstb(db) AT=10
* .measure AC cutoff_freq trig at=0 targ lstb(db) val='maxGain-3' FALL=LAST


********************************************************************
********************************************************************
********************************************************************


* vout/il

* VIN IN 0 dc=inVal ac=0
* VR R 0 ref ac=0
* VSH SUHA 0 sh ac=0
* IL OUT 0 dc=0 ac 1 0

* E OP SUHA IN 5 MAX=sh MIN=-sh opamp_amplification
* *E OP SUHA vol='(v(IN)-v(5))*(opamp_amplification)'

* R0 OP OUT R_0
* C0 OUT 0 C_0

* RA OUT 5 R_A
* RB 5 R R_B

* *VAC OUT 3 dc=0 ac=1

* *RX IN 3 R_A
* *RY 3 0 R_B

* .NODESET OUT=outVal
* .AC DEC 1000 1 10000G
* .probe ac vdb(OUT) vp(OUT)

* .measure AC unity_freq trig at=0 targ vdb(out) val=0 FALL=LAST


********************************************************************
********************************************************************
********************************************************************

* iout/il

VIN IN 0 dc=inVal ac=0
VR R 0 ref ac=0
VSH SUHA 0 sh ac=0
IL OUTC 0 dc=0 ac 1 0
VMEAS OUT OUTC dc=0 ac=0

E OP SUHA IN 5 MAX=sh MIN=-sh opamp_amplification

R0 OP OUT R_0
C0 OUTC 0 C_0

RA OUT 5 R_A
RB 5 R R_B

.NODESET OUT=outVal
.AC DEC 200 1 10000G
.probe ac idb(vmeas) ip(vmeas)
.pz I(Vmeas) IL

.measure AC maxGain FIND idb(vmeas) AT=1
.measure AC cutoff_freq trig at=0 targ idb(vmeas) val='maxGain-20*log10(sqrt(2))' FALL=LAST

.END
