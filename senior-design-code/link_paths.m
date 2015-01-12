function [current_path,res_probs_update] = link_paths(path_part,current_path,m_old, n_old, m_new,n_new,current_res_probs, lower_res_probs)
    %path_part - array of all the different path parts
    %m_old, n_old - dimensions of higher resolution array
    %m_new, n_new - dimensions of newer resolution arrays
    %current_res_probs - arrays of probabilities in current resolution
    %higher_res_probs - arrays of probabilities in lower resolution
    
    %create larger probability matrix
    res_probs_update = zeros(m_old*m_new, n_old*n_new);
    high_res_path = [];
    for i = 1:length(current_path(:,1))
        %put probabilities in right spot in res_probs_update
        current_point = current_path(i,:);
        scaled_probs = lower_res_probs(current_point(2),current_point(1))*current_res_probs(:,:,i); % scales to make everything probabilities
        res_probs_update((current_point(2)-1)*m_old*m_new+1:current_point(2)*m_old*m_new, (current_point(1)-1)*n_old*n_new+1:current_point(1)*n_old*n_new) = scaled_probs;
        
        %update path
        %get path part that isn't zero
        [good_rows,good_col] = find(path_part(:,:,i)>0);
        good_path = path_part(good_rows,good_col);
        %calculate indeces in larger matrix
        index_update = ones(size(good_path));
        index_update(:,1)  = (current_point(2)-1)*m_old*m_new + 1;
        index_update(:,2) = (current_point(1)-1)*n_old*n_new + 1;
        high_res_path = [high_res_path; (good_path + index_update)];
    end
    current_path = high_res_path; % update current path at the end
end
