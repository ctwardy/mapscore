function [path_sum_new, new_path, probs_update] = add_node(current_path,current_probs, path_sum, m,n,prob_detect)
    %this function will insert a point in between the current x,y position
    %and the next x,y position in the path or between the previous node and
    %current node.  Parameters:  current_path:  the current path of the
    %unit, probs:  the array of probability distributions
    %get neighbors of the different points, path_sum:  current path sum,
    %m,n: dimensions of array, k: current step on the path
    %get the current point on the path and it's immediate neighbors
    new_point_choice = zeros(size(current_path));
    best_probs = zeros(length(current_path(1,:)),1);
    
    for k = 2:(length(current_path(:,1))-1)
        current_xy = current_path(k,:);
        next_xy = current_path(k+1,:); %next point on path
        previous_xy = current_path(k-1,:); %previous point on path
        [ncx,ncy] = get_neighbors(current_xy(1), current_xy(2), m,n);
        neighbors = [ncx ncy];
        [nnx,nny] = get_neighbors(next_xy(1), next_xy(2),m,n);
        next_neighbors = [nnx nny];
        [npx,npy] = get_neighbors(previous_xy(1), previous_xy(2),m,n);
        prev_neighbors = [npx npy];
        v1 = intersect(neighbors,next_neighbors,'rows');
        v2 = intersect(neighbors,prev_neighbors,'rows');
        valid_choices = union(v1,v2,'rows'); %the choices for the new point based on the old points
        %get intersection of all three arrays as valid points
        %look at the probabilities of the 
        n_probs = zeros(length(valid_choices(:,1)),1);
        for p = 1: length(valid_choices(:,1))
            n_probs(p) = current_probs(valid_choices(p,2), valid_choices(p,1));
        end
        a = find(n_probs == max(n_probs));
        new_point_choice(k,:) = valid_choices(a,:);
        best_probs(k) = current_probs(new_point_choice(k,2), new_point_choice(k,1));
    end
    best_point = find(best_probs == max(best_probs));
    if length(best_point)>1
        best_point = best_point(1);%pick the first best choice if there are more than one
    end
    %update path sum new
    current_probs(new_point_choice(best_point,2), new_point_choice(best_point,1));
    path_sum_new = path_sum + prob_detect*current_probs(new_point_choice(best_point,2), new_point_choice(best_point,1));
    probs_update = current_probs;
    probs_update(new_point_choice(best_point,2), new_point_choice(best_point,1)) = (1-prob_detect)*probs_update(new_point_choice(best_point,2), new_point_choice(best_point,1));%reflect that the new point has been visited in the probabilities matrix
    %update new path
    current_xy = current_path(best_point,:); %the current point that yielded the new best point
    [ncx,ncy] = get_neighbors(current_xy(1), current_xy(2), m,n);
    neighbors = [ncx ncy];
    previous_xy = current_path(best_point-1,:); %previous point on path
    [npx,npy] = get_neighbors(previous_xy(1), previous_xy(2),m,n);
    prev_neighbors = [npx npy];    
    v = intersect(neighbors,prev_neighbors,'rows');
    if ~isempty(intersect(v,new_point_choice(best_point,:), 'rows')) %check to see if it's between the kth point and the previous neighbor
        new_path = [current_path(1:best_point-1,:) ; new_point_choice(best_point,:); current_path(best_point:end,:)];
    else %if not,it's between the current point and the next point in the path
        new_path = [current_path(1:best_point,:); new_point_choice(best_point,:); current_path(best_point+1:end,:)];
    end
end
