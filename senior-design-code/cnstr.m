%cost constraint function
function [c,ceq] = cnstr(x)
    global m_new n_new m_current n_current Cp
    %x is the variable representing effort of searching a search region
    %m_new/current, n_new/current are global variables from the big_path.m
    %code
    C = floor(Cp*m_new*n_new); %x should be m_new*n_new long
    c =sum(x*(m_current*n_current))-C; %assumes search areas have equal probability
    ceq = [];%not using this constraint
