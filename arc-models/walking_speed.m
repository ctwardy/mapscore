function map = walking_speed(elev,R,num_it,fname)
%creates a map simulating hiker movement as gas
%elev-elevation
%R - reference matrix in terms of [cells/degree,top latitude, west
%longitude
%num_it - number of iterations
%fname - file to which final image is saved

%first, calculate the slope function
[ASPECT, SLOPE, gradN, gradE] = gradientm(elev, R);
%calculate walking speed using tobler's formula
speed_mat = 6*exp(-3.5*abs(tand(SLOPE)+.05));
%scale speed matrix down to [0,.25]
speed_mat = .25*speed_mat/max(max(speed_mat));

%downsample things to make managable calculations
speed_mat = downsample(downsample(speed_mat,3)',3)';
%set up last known point
[m,n] = size(speed_mat);
con = zeros(m,n);
con(ceil(m/2),ceil(n/2)) = 1;
%run the iterations
con_2 = gas_move(con,speed_mat,[ceil(m/2) ceil(n/2)],[],num_it);
%upsample
con_2 = con_2/sum(sum(con_2));%normalizing
map = con_2;
figure(); imagesc(map);
%create and resize png to 5000 by 5000
im_map = imresize(map,[5000,5000]);
%write image to file
im_map = mat2gray(im_map);
imwrite(im_map,fname);
end
