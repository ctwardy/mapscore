function [fx] = S(x)
    %f(x) for kadane's probability function
    %computes suml(pl*exp(sumj(xlj*log(alphalj))
    %x is the matrix of continuous variables given by [n1,n2,...nL] is the
    %effort put into each search area, since with simplifications j isn't
    %needed
    %pl, alphal are taken as global varables
    global alphal pl
    eIl = exp(x.*log(alphal));% e^(sumj(n*log(alphal
    fx = sum(pl.* eIl);

    
