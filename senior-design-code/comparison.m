%hill climbing
clear all; close all;

m = 5;
n = 5;
prob_detect = .9;
spt = [1 1];
ept = [4 5];

C = floor(m*n*.75); %total number of cells drone can travel to
for i = 1:30
    search_value = rand(m,n);
    probs = search_value/sum(sum(search_value)); %turn the example set into probabilities.
    best_hill_sum(i) = hill_climbing(m,n,probs,prob_detect,C,spt, ept);
    %compare to greedy algorithm for the same set of probabilities
    best_greedy_sum(i) = greedy_algorithm(m,n,probs,prob_detect);
    i
end
hill_avg = mean(best_hill_sum);
greedy_avg = mean(best_greedy_sum);
