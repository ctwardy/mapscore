function [best_path,best_path_sum] = hill_climbing(m,n,probs,prob_detect,C,spt, ept)
    %m,n - dimensions of matrix
    %probs - array of probability that the subject is in location
    %prob_detect - probability that searcher will see subject
    %C - total cost i.e. number of cells that can be visited
    %spt, ept - starting and ending points, respectively
    tic
    i_best_path = zeros(C,2,10); %for storing the best path
    i_path_sum = zeros(1,10);
    path_sum_start = zeros(1,10);
    for i = 1:10 
        probs_current = probs;
        %first find random starting path with length less than or equal to C
        l = C+1;
        while l>C 
        current_path = gen_rand_path(spt,ept,m,n);
        l = length(current_path(:,1));
        end
        %compute first path sum
        path_sum = 0;
        for j = 1:length(current_path(:,1))
            path_sum = path_sum + prob_detect*probs_current(current_path(j,2), current_path(j,1));
            probs_current(current_path(j,2), current_path(j,1)) = probs_current(current_path(j,2), current_path(j,1))*(1-prob_detect);
        end
        path_sum_start(i) = path_sum;
        %hill climbing loop:  two rules:  add a node, replace a node
        for a = 1:100     
            if length(current_path(:,1))<C %add the highest valid probability node into the path
                [path_sum_new, new_path, probs_update] = add_node(current_path, probs_current, path_sum, m,n,prob_detect);
            else %can't add a node because length of path = C, so go through each node and figure out the best way to switch
                [path_sum_new, new_path, probs_update] = replace_node(current_path, probs, probs_current,m,n, prob_detect);
            end
            delta_p = path_sum_new - path_sum;
            if delta_p > 0 %new path is a better sum
                path_sum = path_sum_new; %take new path/new path sum
                current_path = new_path;
                probs_current = probs_update;
            end %if the old path was better, don't update anything
        end
        i_path_sum(i) = path_sum; %store the current path sum
        i_best_path(:,:,i) = current_path; %store the current path for access later
    end

    best_path_sum = max(i_path_sum);
    best_i = find(i_path_sum == best_path_sum);
    best_path = i_best_path(:,:,best_i);
    best_path_start = path_sum_start(best_i);
%     disp('best hill climbing path is:')
%     disp(best_path);
%     disp('best hill climbing sum is:')
%     disp(best_path_sum);

    toc
