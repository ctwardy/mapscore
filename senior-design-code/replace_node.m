function [path_sum_new, new_path, probs_update] = replace_node(current_path, probs, current_probs,m,n,prob_detect)
    %function to replace the kth element of the path.  parameters:
    %current_path: array representing column, row elements of the current
    %path.  probs:  array of probabilities at the area needed to recompute path sum, current_probs m,n: dimensions of
    %array, k, current spot on the path
    new_point_choice = zeros(size(current_path));
    best_probs = zeros(length(current_path(1,:)),1);
    for k = 2:(length(current_path(:,1))-1)
        current_xy = current_path(k,:);
        next_xy = current_path(k+1,:); %previous point on path
        previous_xy = current_path(k-1,:); %next point on path
        [nnx,nny] = get_neighbors(next_xy(1), next_xy(2),m,n); %don't need neighbors of current point because that's being gotten rid of 
        next_neighbors = [nnx nny];
        [npx,npy] = get_neighbors(previous_xy(1), previous_xy(2),m,n);
        prev_neighbors = [npx npy] ;
        valid_choices = intersect(next_neighbors, prev_neighbors,'rows');%the idea is that the new in between point should be a neighbor of both points
        %choose valid choices as in "add_node"
        n_probs = zeros(length(valid_choices(:,1)),1);
        for i = 1: length(valid_choices(:,1))
            n_probs(i) = current_probs(valid_choices(i,2), valid_choices(i,1));%have to look at the current probs
        end
        a = find(n_probs == max(n_probs));
        new_point_choice(k,:) = valid_choices(a(1),:);
        best_probs(k) = probs(new_point_choice(k,2), new_point_choice(k,1));
    end
    best_point = find(best_probs == max(best_probs));
    if length(best_point)>1
        best_point = best_point(1);%pick the first best choice if there are more than one
    end
    %update probability
    new_path = [current_path(1:best_point-1,:); new_point_choice(best_point,:); current_path(best_point+1:end,:)];
    %have to update the path sum  the same way as in the first loop because
    %if a point is replaced it doesn't factor into the whole sum
    path_sum_new = 0;
    probs_update = probs;
    for j = 1:length(current_path(:,1))
        path_sum_new = path_sum_new + prob_detect*probs(new_path(j,2), new_path(j,1));
        probs_update(new_path(j,2), new_path(j,1)) = probs(new_path(j,2), new_path(j,1))*(1-prob_detect);
    end
end
