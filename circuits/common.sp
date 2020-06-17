*common circuits

* Integrator
* v(out)=(- gain/(rval*cval))* integral(vin)
.subckt integrator  in out  gain=-1 rvalue=1k cvalue=1p
*eopamp  outOpamp  0  opamp   inOpamp  0
eopamp  outOpamp  0  inOpamp  0 1e12
*eopamp  outOpamp  0  inOpamp  0 1e12 max=supp min=-supp
rint in  inOpamp  rvalue
cint inOpamp outOpamp cvalue
egain out 0 outOpamp 0 gain
rout  out 0 1e12
.ends

*------------------------------------------------

* Differentiator
* v(out)= rval * cval * ( - gain) * (d/dt v(in))
.subckt differentiator in out  gain=-1 rvalue=1k cvalue=1pf
*eopamp  outOpamp  0  opamp   inOpamp  0
eopamp  outOpamp  0  inOpamp  0 1e12
*eopamp  outOpamp  0  inOpamp  0 1e12 max=supp min=-supp
cint in  inOpamp  cvalue
rint inOpamp outOpamp rvalue
egain vsmooth 0 outOpamp 0 gain
rout  vsmooth 0 1e12

*rc filter to smooth the output
rsmooth vsmooth out 75
csmooth out  0   1pf
.ends
