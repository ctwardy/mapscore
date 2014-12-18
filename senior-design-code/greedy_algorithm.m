%greedy path finding algorithm for search and rescue
%first, load in the array of probabilities, for this example i just picked
%a matrix from a uniform distribution between 0 and 1 and then turn that
%into probabilities that sum to 1
function best_sum = greedy_algorithm(m,n,probs,prob_detect)
%starting off with 4x4 matrix for simplicity
 %turn the example set into probabilities. 
%set a cost for the search, here it is arbitrarily 75% of cells that the quad can cover,
%can determine this through flight time, etc
tic
num_cells = ceil(m*n*0.75);

path_sum = zeros(m,n);
current_x = zeros(m,n,num_cells);
current_y = zeros(m,n,num_cells); %this will keep track of the path for each starting point
%to find the best path moving through only some of the cells,we want to know the best starting point
for x = 1:1:n
    for y = 1:1:m %first two loops desginate going through the different starting points
        search_value_temp = probs; %going to be changing this matrix so i set the thing
        current_x(y,x,1) = x;
        current_y(y,x,1) = y;
        path_sum(y,x) =prob_detect*search_value_temp(y, x);%initialize path probability sum, using probability of detection because we might miss
        search_value_temp(current_y(y,x,1), current_x(y,x,1)) = search_value_temp(current_y(y,x,1), current_x(y,x,1))*(1 - prob_detect); %subtracting some probability from the first cell
        
        for k = 2:1:num_cells
            
            [neighbors_x, neighbors_y] = get_neighbors(current_x(y,x,k-1), current_y(y,x,k-1), n, n);
            current_neighbors = [neighbors_x neighbors_y];

            neighbor_prob = zeros(size(neighbors_x));
            for i = 1:length(neighbors_x)
                neighbor_prob(i) = search_value_temp(current_neighbors(i,2),current_neighbors(i,1));
            end
            best_neighbor = find(neighbor_prob == max(neighbor_prob));
            next_x = current_neighbors(best_neighbor,1);
            next_y = current_neighbors(best_neighbor,2);
            if length(next_x)>1 %if there are two equal probability cells in the neighbors list just pick one randomly
                p = ranperm(length(next_x), 1);
                current_x(y,x,k) = next_x(p);
                current_y(y,x,k) = next_y(p);
            else 
                current_x(y,x,k) = next_x;
                current_y(y,x,k) = next_y;
            end;
            path_sum(y,x) = path_sum(y,x) + prob_detect*search_value_temp(current_y(y,x,k), current_x(y,x,k)); %update the path sum
            search_value_temp(current_y(y,x,k), current_x(y,x,k)) = search_value_temp(current_y(y,x,k), current_x(y,x,k))*(1 - prob_detect);
        end
    end
end
[best_start_y, best_start_x] = find(path_sum == max(max(path_sum)));
if length(best_start_x)>1
    p = randperm(length(best_start_x),1);
    best_start_x = best_start_x(p);
    best_start_y = best_start_y(p);
end
best_sum = path_sum(best_start_y, best_start_x);
best_pathx = zeros(num_cells,1);
best_pathy = zeros(num_cells,1);
best_pathtempx = current_x(best_start_y, best_start_x, :);
best_pathtempy = current_y(best_start_y, best_start_x, :);
toc
for i =1:num_cells
    best_pathx(i) = best_pathtempx(1,1,i);
    best_pathy(i) = best_pathtempy(1,1,i);
end
best_path = [best_pathx best_pathy];
% display(sprintf('the best greedy path sum is: %d',best_sum))
% display(sprintf('the best greedy starting point is %d , %d', best_start_x, best_start_y))
% display(sprintf('the best greedy path found is: '));
% display(best_path)
toc

%needed, vectorize for loops to make the program scaleable to a larger array,
%firgure out higher level algorithm to get the effort put into cells
