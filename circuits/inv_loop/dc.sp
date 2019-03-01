Transient simulation of inverter loop Schmitt Trigger
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

.PARAM inValLower=<sed>lower<sed>V inValUpper=<sed>upper<sed>V
.PARAM stepWidth=<sed>step<sed>V outVal=<sed>out<sed>V

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
+ MEASDGT=10
+ RUNLVL=6

.include technology

VCC 5 0 supp
VIN 1 0 dc

*forward inverter 1
XP1 3 1 5 5 pmos
XN1 3 1 0 0 nmos

*forward inverter 2
XP2 2 3 5 5 pmos
XN2 2 3 0 0 nmos

*backward inverter
XP3 3 2 5 5 pmos_weak
XN3 3 2 0 0 nmos_weak

C1 2 0 loadVal

.PROBE DC V(2)
.NODESET 2=outVal
.DC VIN inValLower inValUpper stepWidth

.END
