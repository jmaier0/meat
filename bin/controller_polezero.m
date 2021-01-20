
% Copyright 2021 Christian Hartl-Nesic

% Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

% The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

% THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

% author: Christian Hartl-Nesic
% mail: christian.hartl@tuwien.ac.at


function controller_polezero(inPath, outPath)

  files = strcat(inPath, 'pz_*.dat');
  output = strcat(outPath, 'controller_PID.txt');

  %Range for computing the root-locus plot
  K_P_range=[0,5];
  %Design optimal controller, if possible
  find_K_P=true;

  files=dir(files);
  output=fopen(output,'w+');
  f=logspace(1,14,1000);
  for j=1:size(files,1)
    [p,z]=importfile_polezero([files(j).folder,'/',files(j).name]);
    
    G=tf(poly(z),poly(p));
    V=freqresp(G,0);
    G=-(1/V)*G;

    [m,p]=bode(G,f);
    m=20*log10(m);
    figure(1);
    clf;
    subplot(2,2,1);
    semilogx(f,m(:));
    grid on;
    subplot(2,2,3);
    semilogx(f,p(:));
    grid on;

    subplot(2,2,[2,4]);
    rlocus(G,linspace(K_P_range(1),K_P_range(2),1000));
    [r,k]=rlocus(G,linspace(K_P_range(1),K_P_range(2),10000));
    is_stabilizable=any(all(real(r)<0,1));

    %Necessary condition for Hurwitz polynomial: All coefficients of the
    %polynomial have the same sign (either positive or negative).
    %Checking for positive
    upper_bound=[];
    lower_bound=[];
    b=flip(G.Numerator{1,1});
    a=flip(G.Denominator{1,1});
    for i=1:length(a)
      if(b(i)<0)
	upper_bound=[upper_bound,-a(i)/b(i)];
      elseif(b(i)>0)
	lower_bound=[lower_bound,-a(i)/b(i)];
      else %b==0
	if(a(i)<=0)
               %Inequality condition 0<P b+a is never satisfied. Therefore, this
               %case cannot deliver any stability conditions
          upper_bound=[];
          lower_bound=[];
          break;
	end
      end
    end
    upper_bound1=min(upper_bound);
    lower_bound1=max(lower_bound);
    if(upper_bound1<lower_bound1)
      lower_bound1=[];
      upper_bound1=[];
    end
    %Checking for negative
    upper_bound=[];
    lower_bound=[];
    b=flip(G.Numerator{1,1});
    a=flip(G.Denominator{1,1});
    for i=1:length(a)
      if(b(i)>0)
	upper_bound=[upper_bound,-a(i)/b(i)];
      elseif(b(i)<0)
	lower_bound=[lower_bound,-a(i)/b(i)];
      else %b==0
	if(a(i)>=0)
          %Inequality condition P b+a<0 is never satisfied. Therefore, this
          %case cannot deliver any stability conditions
          upper_bound=[];
          lower_bound=[];
          break;
	end
      end
    end
    upper_bound2=min(upper_bound);
    lower_bound2=max(lower_bound);
    if(upper_bound2<lower_bound2)
      lower_bound2=[];
      upper_bound2=[];
    end

    if(find_K_P && ...
       ((~isempty(lower_bound1) && ~isempty(upper_bound1)) ||...
	(~isempty(lower_bound2) && ~isempty(upper_bound2))))
      %Set initial guess for controller to 90% of upper bound
      if(~isempty(upper_bound1))
	K_P_0=0.9*upper_bound1;
      elseif(~isempty(upper_bound2))
	K_P_0=0.9*upper_bound2;
      end
      K_P_20percent=fzero(@(K_P)overshoot_ratio(K_P,G)-1.95,K_P_0);
      if(isnan(K_P_20percent))
       %If a gain with 20% overshoot was not found, look for a gain with
       %maximum overshoot
	K_P_20percent=fminsearch(@(K_P)-overshoot_ratio(K_P,G),K_P_0);
	K_P_name='K_P_opt';
      else
	K_P_name='K_P_20percent';
      end
    else
      K_P_name='K_P_';
      K_P_20percent=0;
    end
    
    s=sprintf('%s: %.5f < K_P < %.5f or %.5f < K_P < %.5f, is_stabilizable=%d, %s=%.5f, overshoot_ratio=%.5f\n',...
	      files(j).name,lower_bound1,upper_bound1,lower_bound2,upper_bound2,is_stabilizable,K_P_name,K_P_20percent,...
	      overshoot_ratio(K_P_20percent,G));
%    fprintf('%s',s);
    fprintf(output,'%s',s);
  end
  fclose(output);
end

function [res,lambda]=overshoot_ratio(K_P,G)
  try
    L=feedback(K_P*G,1);
    p=pole(L);
    %Find pole with largest imaginary part
    [~,i]=sort(abs(imag(p)),'desc');
    p=p(i);
    [~,i]=find(imag(p)~=0,1,'first');
    if(isempty(i))
      lambda=0;
      res=0;
    else
      %return the ratio imag(lambda)/real(lambda)
      lambda=p(i);
      res=abs(imag(lambda)/real(lambda));
    end
  catch
    lambda=0;
    res=0;
  end
end
