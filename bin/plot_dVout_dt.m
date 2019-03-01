% Copyright 2019 Juergen Maier

% Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

% The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

% THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

% author: Juergen Maier
% mail: juergen.maier@tuwien.ac.at


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% plot_dVout_dt
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% read derivative of output voltage from csv file, create a contour
% plot and then save the resulting graph
% this script is designed to be run on the command line

function plot_dVout_dt(inPath, outPath)
  inFileName = strcat(inPath,'dVout_dt.csv');
  C = dlmread(inFileName,';',1,0);

  X = C(1,:);
  X = X(1:find(X,1,'last'));
  Y = C(2,:);
  Y = Y(1:find(Y,1,'last')+1);
  Z = C(3:end,1:length(X));

  maxVal = max(max(Z));
  minVal = min(min(Z));

  h =figure;
  hold on;
  
  % use minVal/20 and maxVal/20 to get closer to the metastable,
  % these are empirical values and might be adapted if required
  range = linspace(minVal,minVal/20,10);
  range2 = linspace(maxVal/20,maxVal,10);
  levels = [range, range2];
  
  contourf(X,Y,Z,levels,'k');
  
  ylabel('V_{out} [V]');
  xlabel('V_{in} [V]');
  zlabel('d/dt (V_{out}) [a.u.]');
  view(0,90);
  colorbar;
  set(gca,'FontSize',20)

  % draw (meta-)stable line, since it is stored in one continuous stream
  % put the middle part shall be printed dashed it has to be determined
  % at first
  
  inFileName = strcat(inPath,'meta_line.csv');
  D = dlmread(inFileName,';',1,0);

  [v,idxTop] = max(D(1:size(D(:,1))/2,1));
  [v,idxBot] = min(D(size(D(:,1))/2:end,1));
  idxBot = idxBot + size(D(:,1))/2;
  
  plot(D(1:idxTop,1), D(1:idxTop,2), 'k', 'LineWidth', 2)
  plot(D(idxTop:idxBot,1), D(idxTop:idxBot,2), '--k', 'LineWidth', 2)
  plot(D(idxBot:end,1), D(idxBot:end,2), 'k', 'LineWidth', 2)
  
  outFileName = strcat(outPath,'dVout.png');
  saveas(h,outFileName,'png')
  
