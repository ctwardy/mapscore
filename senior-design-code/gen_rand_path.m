function rand_path = gen_rand_path(spt, ept,m,n)
    %function to generate random starting path
    rand_path = spt;
    x = spt(1);
    y  = spt(2);
    current_end = spt;
    while isempty(intersect(ept,current_end,'rows'))
        [x_neighbors,y_neighbors] = get_neighbors(x, y, m,n);
        k = randi([1 length(x_neighbors)],1);
        x = x_neighbors(k); %update x and y
        y = y_neighbors(k);
        current_end = [x y];
        rand_path = [rand_path; current_end];
        
    end
end
