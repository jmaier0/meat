Transient simulation of 8T controllable hysteresis Schmitt Trigger
.PARAM inValLower=<sed>lower<sed>V inValUpper=<sed>upper<sed>V
.PARAM stepWidth=<sed>step<sed>V outVal=<sed>out<sed>

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
+ RUNLVL=5

.include technology

VCC 5 0 supp
VIN 1 0 dc
VB 9 0 vbVal

XP1 3 1 5 5 pmos
XP2 2 1 3 5 pmos
XP3 6 2 3 5 pmos
XP4 0 9 6 5 pmos

XN1 4 1 0 0 nmos
XN2 2 1 4 0 nmos
XN3 7 2 4 0 nmos
XN4 5 9 7 0 nmos

.PROBE DC V(2)
.NODESET 2=outVal
.DC VIN inValLower inValUpper stepWidth

.END
