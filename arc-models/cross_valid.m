%cross validation for a general category, just load different sets of
%distances into the first two lines
clear all; close all;

load categories.mat;
categories = who; %gives list of variables
for k = 1:length(categories)
    avg_avg_lognorm_like = zeros(10,1);
    avg_avg_logcauch_like = zeros(10,1);

    current_set = eval(categories{k});
    if length(current_set)>20
    for j = 1:10
        p = cvpartition(length(current_set),'kfold',10); %make a new partition
        for i = 1:10
            train_set =current_set;
            %get test indeces (train indeces are the ones that aren't the test
            %indeces) for this run
            T = test(p,i);%gets this particular partition
            Test_indeces = find(T ==1);%
            lognorm_loglikelihood = zeros(size(Test_indeces));
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
            avg_lognorm_like = zeros(10,1);
            log_norm = (1-ipp_prob)*(1./(test_set(test_non_ipp_ind)*mu*sqrt(2*pi))).*exp(-1*((log(test_set(test_non_ipp_ind))-mu).^2)/(2*sig^2));
            lognorm_loglikelihood(test_ipp_ind) = log(ipp_prob);%assigning probabilities to points found at ipp, should give a lot.
            lognorm_loglikelihood(test_non_ipp_ind) = log(log_norm);
            avg_lognorm_like(i) = mean(lognorm_loglikelihood);
            
            %want to compare with log cauchy
            logcauchy_loglikelihood = zeros(size(Test_indeces));
            avg_logcauchy_like = zeros(10,1);
            x0 = median(log_train_set); %location parameter
            y = .5*iqr(log_train_set);  %scale parameter
            log_cauchy = (1-ipp_prob)*1./(pi*test_set(test_non_ipp_ind)*y.*(1 + ((log(test_set(test_non_ipp_ind)) -x0)/y).^2));
            logcauchy_loglikelihood(test_ipp_ind) = log(ipp_prob);
            logcauchy_loglikelihood(test_non_ipp_ind) = log(log_cauchy);
            avg_logcauchy_like(i) = mean(logcauchy_loglikelihood);            
        end
        avg_avg_lognorm_like(j) = mean(avg_lognorm_like);
        avg_avg_logcauchy_like(j) = mean(avg_logcauchy_like);
    end
    
    lognorm_result = mean(avg_avg_lognorm_like);
    str = strcat(categories{k} , '_crossvalid_lognormal');
    save(str,'lognorm_result');
    logcauchy_result = mean(avg_avg_logcauchy_like);
    str2 = strcat(categories{k} , '_crossvalid_logcauchy'); 
    save(str2,'logcauchy_result');
    end
end


