function [SLJ,C] = S(p,alpha,c,L,J)
   %parameters p - probability arrays,  alpha-overlook probabilities for each location, c-cost of each cell, M
   %-nlj*clj in this case the values of M are equal as j increases, L- set of locations to do the sum over, J- number of times 
   %each location is searched. (L(i),J(i)) represents searching location
   %L(i) J(i) times
   %SLJ = overlook probability
   %C = total cost of the path
   %reshape input matrices to be column vectors, might be unnecessary but
   %not taking that chance
   [m,n] = size(p);
   p = reshape(p,n*m,1);
   alpha = reshape(alpha, n*m,1);
   c = reshape(c, n*m,1);
   %M = reshape(M, n*m,1); %don't have partial searches so commenting this out
   %take the parts that we need
   pl = p(L);
   alphal = alpha(L);
   cl = c(L);
   %Ml = M(L);
   %compute S((L,J)) assuming that the costs and overlook probabilities are
   %the same for every j and only probabilities are different
   Il = log(alphal); %since not worrying about M, don't need to divide by c
   eIlj = exp(J.*Il);%equivalent to e^(sum_j(Ml,j Il,j)) since the values are equal in J and M  = C 
   SLJ = sum(pl.* eIlj);
   C = sum(J.*cl); %total cost incurred by the path assuming it costs the same to search each cell
