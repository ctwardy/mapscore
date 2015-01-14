function greedy_path = greedy_algorithm(probs,prob_detect,spt,C)
%probs - probability array
%prob_detect - probability of detection
%spt - starting point 
%C- percentage of cells coverable
%performs a greedy algorithm given starting point and probability of
%detection, no fixed ending point
[m,n] = size(probs);
num_cells = C;

search_value_temp = probs; %going to be changing this matrix so i set the thing
current_x = zeros(num_cells,1);
current_y = zeros(num_cells,1);
current_x(1) = spt(1);
current_y(1) = spt(2);
search_value_temp(current_y(1), current_x(1)) = search_value_temp(current_y(1), current_x(1))*(1 - prob_detect); %subtracting some probability from the first cell

for k = 2:1:num_cells
    [neighbors_x, neighbors_y] = get_neighbors(current_x(k-1), current_y(k-1), m, n);
    current_neighbors = [neighbors_x neighbors_y];
    neighbor_prob = zeros(size(neighbors_x));
    for i = 1:length(neighbors_x)
        neighbor_prob(i) = search_value_temp(current_neighbors(i,2),current_neighbors(i,1));
    end
    best_neighbor = find(neighbor_prob == max(neighbor_prob));
    next_x = current_neighbors(best_neighbor,1);
    next_y = current_neighbors(best_neighbor,2);
    if length(next_x)>1 %if there are two equal probability cells in the neighbors list just pick one randomly
        p = randperm(length(next_x), 1);
        current_x(k) = next_x(p);
        current_y(k) = next_y(p);
    else 
        current_x(k) = next_x;
        current_y(k) = next_y;
    end;
    %update search probability by (1-probdetect) * p to reflect searching
    %that cell
    search_value_temp(current_y(k), current_x(k)) = search_value_temp(current_y(k), current_x(k))*(1 - prob_detect);
end

greedy_path = [current_x current_y];




