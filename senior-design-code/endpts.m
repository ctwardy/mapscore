function [spt,ept] = endpts(dx_old, dy_old, dx_new, dy_new,m, n)
    %dx_old, dy_old - which direction is it coming from
    %dx_new, dy_new - which direction is it going
    %m, n - dimensions of array
    
    %spt if statements - depend on old values
    if (dx_old == 0) && (dy_old ==0) %starting point of path, arbitrarily start at top
        spt = [1, floor(n/2)];
    elseif (dx_old > 0) && (dy_old == 0) %coming from the left
        spt = [floor(m/2),1];
    elseif (dx_old < 0) && (dy_old == 0) %coming from the right
        spt = [floor(m/2),n];    
    elseif (dx_old > 0) && (dy_old > 0) %coming from the bottom left
        spt = [m,1];
    elseif (dx_old > 0) && (dy_old < 0) %coming from the top left
        spt = [1,1];
    elseif (dx_old < 0) && (dy_old > 0) %coming from the bottom right
        spt = [m,n];
    elseif (dx_old < 0) && (dy_old < 0) %coming from the top right
        spt = [1,n];
    elseif (dx_old == 0) && (dy_old > 0) %coming from the bottom
        spt = [m,floor(n/2)];
    elseif (dx_old == 0) && (dy_old < 0) %coming from the top
        spt = [1,floor(n/2)];
    end
    %ept if statements - depend on new values

    if (dx_new > 0) && (dy_new == 0) %going right
        ept = [floor(m/2),n];
    elseif (dx_new < 0) && (dy_new == 0) %going left
        ept = [floor(m/2),1];    
    elseif (dx_new > 0) && (dy_new > 0) %going top right
        ept = [1,n];
    elseif (dx_new > 0) && (dy_new < 0) %going bottom left
        ept = [m,1];
    elseif (dx_new < 0) && (dy_new > 0) %going top left
        ept = [1,1];
    elseif (dx_new < 0) && (dy_new < 0) %going bottom right
        ept = [m,n];
    elseif (dx_new == 0) && (dy_new > 0) %going top
        ept = [1,floor(n/2)];
    elseif (dx_new == 0) && (dy_new < 0) %going bottom
        ept = [m,floor(n/2)];
    end
end
