function [spt,ept] = endpts(dx_old, dy_old, dx_new, dy_new,m, n)
    %dx_old, dy_old - which direction is it coming from
    %dx_new, dy_new - which direction is it going
    %m, n - dimensions of array
    
    %spt if statements - depend on old values
    if (dx_old == 0) && (dy_old ==0) %starting point of path, arbitrarily start at top middle
        spt = [floor(n/2),1];
    elseif (dx_old > 0) && (dy_old == 0) %coming from the left
        spt = [1, floor(m/2)];
    elseif (dx_old < 0) && (dy_old == 0) %coming from the right
        spt = [n,floor(m/2)];    
    elseif (dx_old > 0) && (dy_old < 0) %coming from the bottom left
        spt = [1,m];
    elseif (dx_old > 0) && (dy_old > 0) %coming from the top left
        spt = [1,1];
    elseif (dx_old < 0) && (dy_old < 0) %coming from the bottom right
        spt = [n,m];
    elseif (dx_old < 0) && (dy_old > 0) %coming from the top right
        spt = [n,1];
    elseif (dx_old == 0) && (dy_old < 0) %coming from the bottom
        spt = [floor(n/2),m];
    elseif (dx_old == 0) && (dy_old > 0) %coming from the top
        spt = [floor(n/2),1];
    end
    %ept if statements - depend on new values
    if (dx_new > 0) && (dy_new == 0) %going right
        ept = [n,floor(m/2)];
    elseif (dx_new < 0) && (dy_new == 0) %going left
        ept = [1,floor(m/2)];    
    elseif (dx_new > 0) && (dy_new > 0) %going bottom right
        ept = [n,m];
    elseif (dx_new > 0) && (dy_new < 0) %going top left
        ept = [1,1];
    elseif (dx_new < 0) && (dy_new > 0) %going bottom left
        ept = [1,m];
    elseif (dx_new < 0) && (dy_new < 0) %going top right
        ept = [n,1];
    elseif (dx_new == 0) && (dy_new < 0) %going top
        ept = [floor(n/2),1];
    elseif (dx_new == 0) && (dy_new > 0) %going bottom
        ept = [floor(n/2),m];
    elseif (dx_new == 0) && (dy_new ==0) %hit end of path, will do greedy
        ept = [0,0];
    end
end
