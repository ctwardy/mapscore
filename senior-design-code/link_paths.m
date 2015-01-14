function [linked_path] = link_paths(path_part,current_path, m_current,n_current)
    %path_part - array of all the different path parts
    %current_path - path of the lower resolution
    %m_current, n_current - dimensions of newer resolution arrays
    %stitches path together from path parts and current path
    high_res_path = [];
    for i = 1:length(current_path(:,1))
        current_point = current_path(i,:);
        %get path part that isn't zero
        p = path_part(:,:,i);
        [good_rows,good_col] = find(p ~= 0);
        good_path = p(1:length(good_rows)/2,:)
        %calculate indeces in larger matrix
        index_update = ones(size(good_path));
        index_update(:,1)  = (current_point(1)-1)*m_current;
        index_update(:,2) = (current_point(2)-1)*n_current;
        good_path + index_update
        high_res_path = [high_res_path; (good_path + index_update)];
    end
    linked_path = high_res_path; % update current path at the end
end
