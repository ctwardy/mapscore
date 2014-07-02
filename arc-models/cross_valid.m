%cross validation for a general category, just load different sets of
%distances into the first two lines
clear all; close all;
load hiker_dry_flat.mat;
current_set = hiker_dry_flat;
N = 10; %number of random test sets to be done
avg_log_like = zeros(N,1);
for i = 1:N
    
    train_set = current_set;
    Test_indeces = randi(length(current_set),floor(length(current_set)/10),1);%ten percent of the total set
    log_likelihood = zeros(size(Test_indeces));
    test_set = current_set(Test_indeces);
    test_ipp_ind = find(test_set ==0);%need to know which of the test set is found at ipp to assign appropriate likelihoods
    test_non_ipp_ind = find(test_set ~= 0);
    train_set(Test_indeces) = [];%get rid of the test set.
    train_non_ipp = find(train_set ~=0);
    train_ipp_ind = find(train_set == 0);
    ipp_prob = length(train_ipp_ind)/length(train_set);
    log_train_set= log(train_set(train_non_ipp));%can't take log(0)
    mu = mean(log_train_set);
    sig = std(log_train_set);
    %do the lognormal formula using the stuff to get the likelihood for each of
    %the test distances, have to scale the lognormal by 1-ipp prob for
    %conditional stuff

    log_norm = (1-ipp_prob)*(1./(test_set(test_non_ipp_ind)*mu*sqrt(2*pi))).*exp(-1*((log(test_set(test_non_ipp_ind))-mu).^2)/(2*sig^2));
    log_likelihood(test_ipp_ind) = log(ipp_prob);%assigning probabilities to points found at ipp, should give a lot.
    log_likelihood(test_non_ipp_ind) = log(log_norm);
    avg_log_like(i) = mean(log_likelihood);
    
end

mean(avg_log_like)

