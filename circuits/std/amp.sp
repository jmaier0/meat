determining gain of storage loop in standard 6T Schmitt Trigger
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
+ MEASFORM=3
+ MEASDGT=10

.include technology

VCC 5 0 supp ac 0 0
VIN 1 0 inVal ac 0 0
IL 20 0 dc 0 AC 1 0

Vmeas 20 2 dc 0 ac 0 0

XP1 3 1 5 5 pmos
XP2 2 1 3 5 pmos
XP3 0 20 3 5 pmos

XN1 4 1 0 0 nmos
XN2 2 1 4 0 nmos
XN3 5 20 4 0 nmos

.IC 2=outVal
.AC DEC 10 1 10000G
.probe ac idb(vmeas) ip(vmeas)
.pz I(Vmeas) IL

.measure AC maxGain FIND idb(vmeas) AT=1
.measure AC cutoff_freq trig at=0 targ idb(vmeas) val='maxGain-20*log10(sqrt(2))' FALL=LAST



* VCC 5 0 supp
* VIN 1 0 inVal
* VLSTB 2 20 dc=0

* XP1 3 1 5 5 pmos
* XP2 2 1 3 5 pmos
* XP3 0 20 3 5 pmos

* XN1 4 1 0 0 nmos
* XN2 2 1 4 0 nmos
* XN3 5 20 4 0 nmos

* .OP vol
* .NODESET 2=outVal
* .AC DEC 10 1 10000G
* .lstb mode=single vsource=vlstb
* *.lstb mode=comm vsource=vlstb3,vlstb4
* .probe ac lstb(db) lstb(p)

* .measure LSTB unity_freq unity_gain_freq
* .measure LSTB gain loop_gain_at_minifreq
* .measure AC maxGain FIND lstb(db) AT=10
* *.measure AC cutoff_freq trig lstb(db) val=maxGain targ lstb(db) val='maxGain-3'
* .measure AC cutoff_freq trig at=0 targ lstb(db) val='maxGain-3' FALL=LAST

* *.measure ac myfreq FIND lstb(M) AT=10meg
* *.measure ac maxMag max LSTB(r)



* VCC 5 0 supp ac 0
* VIN 1 0 inVal ac 0
* VCA 2 20 dc=0 ac 1 0

* XP1 3 1 5 5 pmos
* XP2 2 1 3 5 pmos
* XP3 0 20 3 5 pmos

* XN1 4 1 0 0 nmos
* XN2 2 1 4 0 nmos
* XN3 5 20 4 0 nmos

* .OP vol
* .NODESET 2=outVal
* .AC DEC 100 1 10000G
* .probe ac vdb(2) vp(2)

* .measure AC maxGain FIND vdb(2) AT=1
* .measure AC cutoff_freq trig at=0 targ vdb(2) val='maxGain-20*log10(sqrt(2))' FALL=LAST


.END
