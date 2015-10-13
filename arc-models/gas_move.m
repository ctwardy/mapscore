function gas  = gas_move(con,speed_mat,src_vec, sink_vec,num_it)
%con- initial concentrations of the gas
%speed_mat- matrix of the max percentage transference,takes values between
%0 and .25-each cell can get rid of at most 25% of it's gas
%src_vec = locations of sources in the thing
%sink_vec= locations of sinks in the domain
%num_it- number of iterations to transfer
[m,n] = size(con);%also the size of speed matrix
if ~isempty(src_vec)
    src_inds = sub2ind([m,n],src_vec(:,1),src_vec(:,2));
end
if ~isempty(sink_vec)
    sink_inds = sub2ind([m,n],sink_vec(:,1),sink_vec(:,2));
end
for i = 1:num_it
    %create left, right, up, and down transition matrices, keeping in mind
    %the borders only have things from 2-3 directions
    left = speed_mat(1:m,1:n-1).*(con(1:m,1:n-1)-con(1:m,2:n));%represents the contribution of the cells coming from the left
    right = speed_mat(1:m,2:n).*(con(1:m,2:n)-con(1:m,1:n-1));%contribution of cells coming from the right
    up = speed_mat(1:m-1,1:n).*(con(1:m-1,1:n)-con(2:m,1:n));%contribution from the cells above
    down = speed_mat(2:m,1:n).*(con(2:m,1:n)-con(1:m-1,1:n));%contribution from the below cells
    %update concentration
    con(1:m,2:n) = con(1:m,2:n)+left;
    con(1:m,1:n-1) = con(1:m,1:n-1)+right;
    con(2:m,1:n) = con(2:m,1:n)+up;
    con(1:m-1,1:n)=con(1:m-1,1:n)+down;
    if ~isempty(src_vec)
        con(src_inds)=1;%fills up the source(s)
    end
    if ~isempty(sink_vec)
        con(sink_inds)=0;%drains sink
    end
end
%at the end number of desired iterations, gas is the final concentration
gas = con;


    
