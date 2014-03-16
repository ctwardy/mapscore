#children eucdist
import os
import sys

import math #want the math library for the 
import numpy
import scipy.misc

fname= "C:/Users/Eric Cawi/Documents/Sar"
distances =[[0.4,0.8,2.4,5.6], [0.1,0.2,0.6,2.0], [0.1,0.2,0.6,2.0], [0.4,1.2,2.0,5.1],\
[0.1,0.5,0.9,2.3], [0.1,0.4,0.9,4.1], [0.3,0.8,2.0,4.5],\
 [0.5,1.0,2.0,7.0], [0.1,0.5,1.3,5.0], [0.5,1.3,4.5,10.0],\
 [0.5,1.0,2.0,5.6], [0.3,1.0,3.0,6.2], [1.5,2.0,3.0,7.4],\
[0.5,1.3,3.0,13.3],[0.4,0.8,2.0,6.2]]
cat_list = ["Child_1_3_Dry","Child_1_3_temperate_mountainous","Child_1_3_else",\
"Child_4_6_dry", "Child_4_6_temperature_mountainous",\
"Child_4_6_else", "Child_7_9_dry",  "Child_7_9_temperature_mountainous",\
"Child_7_9_else","Child_10_12_dry", "Child_10_12_temperature_mountainous",\
"Child_10_12_else", "Child_13_15_dry", "Child_13_15_temperature_mountainous",\
"Child_13_15_else"]
mean_list = [0.024424394, -0.315906488, -0.01235441, 0.383159187, -0.364501639,\
	-0.03288938, 0.077082908, 0.35309571, 0.250700222, 1.127894452, \
0.625782573, 0.293698202, 0.843143089, 1.135429768, 0.438267833]
stdev_list = [1.115701619, 1.375214308, 1.37931074, 1.115285789, 1.071310929, \
	1.526816248, 1.869920265, 1.319448938, 1.211225499, 1.080614521, \
1.059808558, 1.261038675, 1.613561718, 1.206598012, 1.334012835]

dist_array = numpy.zeros((5001,5001))
lognormal_array = numpy.zeros((5001,5001))
#make euclidean distances
for x in range(5001):
	dx = abs(2501 - x)*5
	for y in range(5001):
		dy = abs(2501 - y)*5
		euc_dist = math.sqrt(dx*dx + dy*dy)#straightline distance from central cell
		dist_array[y,x] = euc_dist #x is column index, y is row index
lognormal_array = numpy.log(dist_array) #elementwise log
for i in range(len(distances)):
	print i
	png_name = fname + "/lognormal_pngs/" + cat_list[i] + ".png"
	#compute normal distribution on logarithm of distances
	scaling = 1/(stdev_list[i]*math.sqrt(2*math.pi))
	temp_array = numpy.subtract(lognormal_array,mean_list[i])
	temp_array = numpy.square(temp_array)
	temp_array = numpy.negative(temp_array)
	temp_array = numpy.divide(temp_array,2*(stdev_list[i]*stdev_list[i]))
	temp_array = numpy.exp(temp_array)
	temp_array = numpy.multiply(temp_array,scaling)#final output is normal distribution of log of distances
	temp_array = numpy.exp(temp_array) #transform back into regular space
	temp_array = numpy.log2(temp_array)#transform the guys to integersfor the png
	temp_array = numpy.multiply(temp_array.astype(int),5)
	temp_array = numpy.add(temp_array,255)
	scipy.misc.imsave(png_name, temp_array)
	
	
	



	
	
	


