%test cases for small matrices on greedy and hill climbing, which can be
%verified by hand to ensure algorithms are working
clear all; close all;

m = 5;
n = 5;
prob_detect = .9;
spt = [1 1];
ept = [5 5];

C = floor(m*n*.75); %total number of cells drone can travel to
best_hill_path = zeros(C,2,3);
best_hill_sum = zeros(1,3);
best_greedy_path = zeros(C,2,3);
best_greed_sum = zeros(1,3);
%%magic square matrix
search_value = magic(m);
probs = search_value/sum(sum(search_value)); %turn the example set into probabilities.
[best_hill_path(:,:,1),best_hill_sum(1)] = hill_climbing(m,n,probs,prob_detect,C,spt, ept);
%compare to greedy algorithm for the same set of probabilities
[best_greedy_path(:,:,1),best_greedy_sum(1)] = greedy_algorithm(m,n,probs,prob_detect);
    
search_value = gallery('cauchy',1:m,1:n);
probs = search_value/sum(sum(search_value)); %turn the example set into probabilities.
[best_hill_path(:,:,2),best_hill_sum(2)] = hill_climbing(m,n,probs,prob_detect,C,spt, ept);
%compare to greedy algorithm for the same set of probabilities
[best_greedy_path(:,:,2),best_greedy_sum(2)] = greedy_algorithm(m,n,probs,prob_detect);

%circular bivariate normal distribution, ro = 0, mu = 0, sigma = 1 for x
%and y
y = linspace(-1,1,m);
x = linspace(-1,1,n);
[xx,yy] = meshgrid(x,y);
mu = [0 0];
sig = [1 0; 0 1];
search_value = mvnpdf([xx(:),yy(:)],mu, sig);
search_value = reshape(search_value, length(y), length(x));
probs = search_value/sum(sum(search_value)); %turn the example set into probabilities.
[best_hill_path(:,:,3),best_hill_sum(3)] = hill_climbing(m,n,probs,prob_detect,C,spt, ept);
%compare to greedy algorithm for the same set of probabilities
[best_greedy_path(:,:,3),best_greedy_sum(3)] = greedy_algorithm(m,n,probs,prob_detect);
hill_avg = mean(best_hill_sum);
greedy_avg = mean(best_greedy_sum);
