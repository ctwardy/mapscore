function map = walking_speed(data1,data2,R1,num_it,elev_flag,elev_weight,land_flag,land_weight,fname)
%creates a map simulating hiker movement as gas
%data1 - elevation data
%data2 - land cover data
%R - reference matrix in terms of [cells/degree,top latitude, west
%longitude] or georeference object
%num_it - number of iterations
%elev_flag = doing based on elevation
%land_flag - doing calculation based on land cover
%elev/land weight - weight for combination, if applicabfunction map = walking_speed(data1,data2,R1,num_it,elev_flag,elev_weight,land_flag,land_weight,landclass,fname)
%creates a map simulating hiker movement as gas
%data1 - elevation data
%data2 - land cover data
%R - reference matrix in terms of [cells/degree,top latitude, west
%longitude] or georeference object
%num_it - number of iterations
%elev_flag = doing based on elevation
%land_flag - doing calculation based on land cover
%elev/land weight - weight for combination, if applicable
%fname- desired file location name
%first, calculate the slope function
if elev_flag==1 && land_flag==0;
    figure(); imagesc(data1); title('elevation data')
    [ASPECT, SLOPE, gradN, gradE] = gradientm(data1, R1);
%calculate walking speed using tobler's formula
    speed_mat1 = 6*exp(-3.5*abs(tand(SLOPE)+.05));
%scale speed matrix down to [0,.25]
    speed_mat1 = .25*speed_mat1/max(max(speed_mat1));
elseif land_flag ==1&&elev_flag==0;
    %convert land cover to impedance
    speed_mat1 = land2speed(data2,landclass);%using speed mat 1 in case of only using one dataset
    figure(); imagesc(speed_mat1);title('impedance data')
    
elseif land_flag ==1 && elev_flag==1;
    %use two speed matrices
    figure(); imagesc(data1);title('elevation data')
    [ASPECT, SLOPE, gradN, gradE] = gradientm(data1, R1);
%calculate walking speed using tobler's formula
    speed_mat1 = 6*exp(-3.5*abs(tand(SLOPE)+.05));
    %scale speed matrix down to [0,.25]
    speed_mat1 = .25*speed_mat1/max(max(speed_mat1));
    %calculate second speed matrix, assumed to be land cover
    figure(); imagesc(speed_mat1);title('elevation data')
    
    speed_mat2 = land2speed(data2,landclass);%using speed mat 1 in case of only using one dataset
    figure(); imagesc(speed_mat2);title('impedance data')
    %resize one matrix to the size of the other
    speed_mat2 = imresize(speed_mat2,size(speed_mat1));
    %combine speed matrix
    speed_mat1 = elev_weight*speed_mat1 + land_weight*speed_mat2;

end
%downsample
speed_mat1 = downsample(downsample(speed_mat1,4)',4)';
%set up last known point
[m,n] = size(speed_mat1);
con = zeros(m,n);
con(ceil(m/2),ceil(n/2)) = 1;
%run the iterations
con_2 = gas_move(con,speed_mat1,[ceil(m/2) ceil(n/2)],[],num_it);
%upsample
con_2 = con_2/sum(sum(con_2));%normalizing
map = con_2;
figure(); imagesc(map);
%create and resize png to 5000 by 5000
im_map = imresize(map,[5001,5001]);
%write image to file
im_map = mat2gray(im_map);
imwrite(im_map,fname);

endle
%first, calculate the slope function
if elev_flag==1 && land_flag==0;
    figure(); imagesc(data1); title('elevation data')
    [ASPECT, SLOPE, gradN, gradE] = gradientm(data1, R1);
%calculate walking speed using tobler's formula
    speed_mat1 = 6*exp(-3.5*abs(tand(SLOPE)+.05));
%scale speed matrix down to [0,.25]
    speed_mat1 = .25*speed_mat1/max(max(speed_mat1));
    %downsample
    speed_mat1 = downsample(downsample(speed_mat1,4)',4)';
elseif land_flag ==1&&elev_flag==0;
    %convert land cover to impedance
    speed_mat1 = land2speed(data2);%using speed mat 1 in case of only using one dataset
    figure(); imagesc(speed_mat1);title('impedance data')
    
elseif land_flag ==1 && elev_flag==1;
    %use two speed matrices
    figure(); imagesc(data1);title('elevation data')
    [ASPECT, SLOPE, gradN, gradE] = gradientm(data1, R1);
%calculate walking speed using tobler's formula
    speed_mat1 = 6*exp(-3.5*abs(tand(SLOPE)+.05));
    %scale speed matrix down to [0,.25]
    speed_mat1 = .25*speed_mat1/max(max(speed_mat1));
    %calculate second speed matrix, assumed to be land cover
    speed_ma%downsample
    speed_mat1 = downsample(downsample(speed_mat1,4)',4)';t2 = land2speed(data2);%using speed mat 1 in case of only using one dataset
    figure(); imagesc(speed_mat2);title('impedance data')
    %resize one matrix to the size of the other
    speed_mat2 = imresize(speed_mat2,size(speed_mat1));
    %combine speed matrix
    speed_mat1 = elev_weight*speed_mat1 + land_weight*speed_mat2;
    %downsample
    speed_mat1 = downsample(downsample(speed_mat1,4)',4)';
end
%set up last known point
[m,n] = size(speed_mat1);
con = zeros(m,n);
con(ceil(m/2),ceil(n/2)) = 1;
%run the iterations
con_2 = gas_move(con,speed_mat1,[ceil(m/2) ceil(n/2)],[],num_it);
%upsample
con_2 = con_2/sum(sum(con_2));%normalizing
map = con_2;
figure(); imagesc(map);
%create and resize png to 5000 by 5000
im_map = imresize(map,[5001,5001]);
%write image to file
im_map = mat2gray(im_map);
imwrite(im_map,fname);

end
