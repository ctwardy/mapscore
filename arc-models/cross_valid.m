%cross validation for a general category, just load different sets of
%distances into the first two lines
clear all; close all;

load categories.mat;
categories = who; %gives list of variables
lognorm_result = zeros(length(categories),1);
logcauchy_result = zeros(length(categories),1);
avg_avg_lognorm_like = zeros(10,length(categories));
avg_avg_logcauchy_like = zeros(10,length(categories));
avg_lognorm_like = zeros(10,1);
avg_logcauchy_like = zeros(10,1);
plot_x = linspace(0.2, 4, 10000);
for k = 1:length(categories)
    

    current_set = eval(categories{k});
    if length(current_set)>25
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
            test_mean(i,j,k)= mean(test_set);
            test_std(i,j,k) = std(test_set);
            test_ipp_ind = find(test_set ==0);%need to know which of the test set is found at ipp to assign appropriate likelihoods
            test_non_ipp_ind = find(test_set ~= 0);
            train_set(Test_indeces) = [];%get rid of the test set.
            train_non_ipp = find(train_set ~=0);
            train_ipp_ind = find(train_set == 0);
            ipp_prob = length(train_ipp_ind)/length(train_set);
            scale = 1-ipp_prob;
            log_train_set= log(train_set(train_non_ipp));%can't take log(0)
            mu = mean(log_train_set);
            sig = std(log_train_set);
            %do the lognormal formula using the stuff to get the likelihood for each of
            %the test distances, have to scale the lognormal by 1-ipp prob for
            %conditional stuff
            
            log_norm = 1./(test_set(test_non_ipp_ind)*sqrt(2*pi));
            log_norm = log_norm.*(exp(-1*((log(test_set(test_non_ipp_ind))-mu).^2)/(2*(sig^2))));
            log_norm = scale*log_norm;
            lognorm_loglikelihood(test_ipp_ind) = log(ipp_prob);%assigning probabilities to points found at ipp, should give a lot.
            lognorm_loglikelihood(test_non_ipp_ind) = log(log_norm);
            avg_lognorm_like(i) = mean(lognorm_loglikelihood);

            %want to compare with log cauchy
            logcauchy_loglikelihood = zeros(size(Test_indeces));
            test_set(test_ipp_ind)= .02;
            train_set(train_ipp_ind) = .02;
            log_train_set = log(train_set);
            x0 = median(log_train_set); %location parameter
            y = .5*iqr(log_train_set);  %scale parameter
            
            log_cauchy = 1./(pi*test_set(:)*y.*(1 + ((log(test_set(:)) -x0)/y).^2));

            logcauchy_loglikelihood = log(log_cauchy);
            avg_logcauchy_like(i) = mean(logcauchy_loglikelihood);            
        end
        avg_avg_lognorm_like(j,k) = mean(avg_lognorm_like);
        avg_avg_logcauchy_like(j,k) = mean(avg_logcauchy_like);
        
    end
    
    figure();
    hold on
        
    title(categories(k))
    plot(test_set(test_non_ipp_ind), log_norm, test_set, log_cauchy,'r')%plots the last test set of each category
    lognorm_result(k) = mean(avg_avg_lognorm_like(:,k));
    str = strcat(categories{k} , '_crossvalid_lognormal');
    save(str,'lognorm_result');
    logcauchy_result(k) = mean(avg_avg_logcauchy_like(:,k));
    str2 = strcat(categories{k} , '_crossvalid_logcauchy'); 
    save(str2,'logcauchy_result');
    end
end


%create boxplots of every applicable category
unused_ind = [];
for i =1:length(categories)
    if (avg_avg_lognorm_like(1,i) ==0)
        unused_ind = [unused_ind i];
    end
end
lognorm_result(unused_ind) = [];
logcauchy_result(unused_ind) = [];
avg_avg_lognorm_like(:,unused_ind)= [];
avg_avg_logcauchy_like(:,unused_ind) = [];
categories(unused_ind) = [];%getting rid of unused indeces.
%sort the categories in ascending order for the boxplots

[sort_lognorm, norm_ind] = sort(lognorm_result);
[sort_logcauchy, cauchy_ind] = sort(logcauchy_result);
sort_norm = zeros(size(avg_avg_lognorm_like));
sort_cauchy = zeros(size(avg_avg_logcauchy_like));
cat_sort_norm = categories(norm_ind);
cat_sort_cauchy = categories(cauchy_ind);
sort_norm = avg_avg_lognorm_like(:,norm_ind);
sort_cauchy = avg_avg_logcauchy_like(:,cauchy_ind);%don't need for loop to do this

figure();
hold on;
boxplot(sort_cauchy,'labels',cat_sort_cauchy,'labelorientation','inline');
title('Log Likelihood -log cauchy');

figure();
hold on;
boxplot(sort_norm,'labels', cat_sort_norm,'labelorientation','inline');
title('Log Likelihood-lognormal distribution');
