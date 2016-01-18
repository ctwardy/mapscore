function speed_mat = land2speed(data,land_cover_class)
%converts the land cover data to impedance values
%land cover class has two columns, 1 is the values taken by the raster. The second is impedance values. In my case i'm scaling down to [0,.25] for the gas model
temp = data;
for i = 1:length(land_cover_class(:,1))
    inds = find(data == land_cover_class(i,1));% find all of the points that have a particular classification
    temp(inds) = land_cover_class(i,2); %reset all of the data
end
%get rid of any border values by setting unknown things to 0 go
inds = find(temp>.25);
temp(inds) = 0;
speed_mat = temp;
end
