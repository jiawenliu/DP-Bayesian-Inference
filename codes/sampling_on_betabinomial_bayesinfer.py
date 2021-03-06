import numpy
import matplotlib.pyplot as plt
from copy import deepcopy
import random
import math
import scipy
from scipy.stats import beta
from fractions import Fraction
import operator
import time
from matplotlib.patches import Polygon
import statistics
from decimal import *
from scipy.special import gammaln
from dirichlet import dirichlet
from dpbayesinfer_Betabinomial import BayesInferwithDirPrior



#############################################################################
#PLOT THE SAMPLING RESULTS BY 4-QUANTILE BOX PLOTS
#############################################################################

def plot_error_box(data, xlabel, xstick, title, legends, colors):
	l = len(legends)
	plt.figure(figsize=(0.5*len(data),9))
	medianprops = dict(linestyle='--', linewidth=3.0, color='lightblue')
	# meanlineprops = dict(linestyle='--', linewidth=2.5, color='purple')
	bplot = plt.boxplot(data, notch=1, widths=0.4, sym='+', showfliers=False, vert=2, whis=1.2, patch_artist=True, medianprops=medianprops)#, meanprops=meanlineprops, meanline=True,showmeans=True)
	plt.xlabel(xlabel,fontsize=15)
	plt.ylabel('Hellinger Distance',fontsize=15)
	#ax.set_xlim(0.5, len(errors) + 0.5)


	plt.xticks([i*l + (l+1)/2.0 for i in range(len(xstick))],xstick,rotation=40,fontsize=12)
	plt.title(title,fontsize=15)

	for i in range(1, len(bplot["boxes"])/l + 1):
		for j in range(l):
			box = bplot["boxes"][l * (i - 1) + j]
			box.set(color=colors[j], linewidth=1.5)
			box.set(facecolor=colors[j] )
	plt.legend([bplot["boxes"][i] for i in range(l)], legends, loc='best')
	plt.grid()
	plt.show()


#############################################################################
#PLOT THE MEAN SAMPLING RESULTS IN SCATTER 
#############################################################################


def plot_mean_error(x,y_list,xstick,xlabel, ylabel, title):
	plt.figure(figsize=(11,8))
	i = 0	
	for i in range(len(y_list)):
		plt.plot(x, y_list[i],'o-',label=ylabel[i])

	plt.xticks(x,xstick,rotation=70,fontsize=12)
	plt.title(title,fontsize=20)
	plt.xlabel(xlabel,fontsize=15)	
	plt.ylabel('Average Hellinger Distance ',fontsize=15)
	plt.grid()
	plt.legend()
	plt.show()

#############################################################################
#SAMPLING UNDER DIFFERENT DATASIZE 
#############################################################################

def accuracy_VS_datasize(epsilon,delta,prior,observations,datasizes):
	data = []
	mean_error = [[],[],[],[],[],[]]
	for i in range(len(datasizes)):
		observation = observations[i]
		Bayesian_Model = BayesInferwithDirPrior(prior, sum(observation), epsilon, delta, 0.2)
		Bayesian_Model._set_observation(observation)
		print("start" + str(observation))
		Bayesian_Model._experiments(500)
		print("finished" + str(observation))

		for j in range(len(mean_error)):
			mean_error[j].append(Bayesian_Model._accuracy_mean[Bayesian_Model._keys[j]])

		# data.append(Bayesian_Model._accuracy[Bayesian_Model._keys[3]])
		# data.append(Bayesian_Model._accuracy[Bayesian_Model._keys[0]])
		# data.append(Bayesian_Model._accuracy[Bayesian_Model._keys[4]])
		# a = statistics.median(Bayesian_Model._accuracy[Bayesian_Model._keys[3]])
		# b = statistics.median(Bayesian_Model._accuracy[Bayesian_Model._keys[0]])
		# c = statistics.median(Bayesian_Model._accuracy[Bayesian_Model._keys[4]])


	print('Accuracy / prior: ' + str(prior._alphas) + ", delta: " 
		+ str(delta) + ", epsilon:" + str(epsilon))

	# print mean_error

	plot_mean_error(datasizes, mean_error, datasizes, 
		"Different Datasizes", 
		[r"$\mathsf{LSDim}$",
		r"$\mathsf{LSHist}$",
		r"$\mathsf{LSZhang}$",
		r"$\mathsf{EHDS}$",
		r"$\mathsf{EHD}$",
		r"$\mathsf{EHDL}$"], "")
	
	# plot_error_box(data,"Different Datasizes",datasizes,"Accuracy VS. Data Size",
	# 	[r'$\mathcal{M}^{B}_{\mathcal{H}}$',"LapMech (sensitivity = 2)", "LapMech (sensitivity = 3)"],
	# 	['lightblue', 'navy', 'red'])
	return


#############################################################################
#SAMPLING UNDER DIFFERENT PRIORS 
#############################################################################


def accuracy_VS_prior(sample_size,epsilon,delta,priors,observation):
	data = []
	mean_error = [[],[],[],[],[]]
	for prior in priors:
		Bayesian_Model = BayesInferwithDirPrior(prior, sample_size, epsilon, delta)
		Bayesian_Model._set_observation(observation)
		Bayesian_Model._experiments(1000)
		data.append(Bayesian_Model._accuracy[Bayesian_Model._keys[3]])
		data.append(Bayesian_Model._accuracy[Bayesian_Model._keys[0]])
		data.append(Bayesian_Model._accuracy[Bayesian_Model._keys[4]])
		mean_error[0].append(Bayesian_Model._accuracy_mean[Bayesian_Model._keys[3]])
		mean_error[1].append(Bayesian_Model._accuracy_mean[Bayesian_Model._keys[0]])
		mean_error[2].append(Bayesian_Model._accuracy_mean[Bayesian_Model._keys[4]])

	print('Accuracy / observation: ' + str(observation) + ", delta: " + str(delta) + ", epsilon:" + str(epsilon))
		
	plot_error_box(data,r"Different Priors on $\theta$",[r"$\mathsf{beta}$" + str(i._alphas) for i in priors],
		"Accuracy VS. Prior Distribution",
		[r'$\mathcal{M}_{\mathcal{H}}$',"LapMech (sensitivity = 1)", "LapMech (sensitivity = 2)"],
		['navy', 'red', 'green'])
	return


#############################################################################
#SAMPLING UNDER DIFFERENT PRIORS 
#############################################################################


def accuracy_VS_mean(sample_size,epsilon,delta,prior):
	data = []
	xstick = []
	temp = BayesInferwithDirPrior(prior, sample_size, epsilon, delta)
	temp._set_candidate_scores()
	observations = temp._candidates
	for i in range(len(observations)):
		observations[i]._minus(prior)
	for observation in observations:

		Bayesian_Model = BayesInferwithDirPrior(prior, sample_size, epsilon, delta)
		Bayesian_Model._set_observation(observation._alphas)
		Bayesian_Model._experiments(500)
		data.append(Bayesian_Model._accuracy[Bayesian_Model._keys[3]])
		data.append(Bayesian_Model._accuracy[Bayesian_Model._keys[0]])
		xstick.append(str(observation._alphas) + "/ExpMech")
		xstick.append(str(observation._alphas) + "/Laplace")

	plot_error_box(data,"Different Prior Distributions",xstick,"Accuracy VS. Prior Distribution")

	return

#############################################################################
#SAMPLING UNDER DIFFERENT PRIORS 
#############################################################################

def accuracy_VS_dimension(sample_sizes, epsilon, delta):
	data = []
	xstick = []
	for n in sample_sizes:
		for d in range(2,5):
			observation = [n for i in range(d)]
			prior = Dir([1 for i in range(d)])
			Bayesian_Model = BayesInferwithDirPrior(prior, n*d, epsilon, delta)
			Bayesian_Model._set_observation(observation)
			Bayesian_Model._experiments(500)
			data.append(Bayesian_Model._accuracy[Bayesian_Model._keys[3]])
			data.append(Bayesian_Model._accuracy[Bayesian_Model._keys[0]])
			xstick.append(str(observation) + "/ExpMech")
			xstick.append(str(observation) + "/Laplace")


	plot_error_box(data,"Different Prior Distributions",xstick,"Accuracy VS. Prior Distribution")

	return

#############################################################################
#SAMPLING UNDER DIFFERENT PRIORS 
#############################################################################


def accuracy_VS_prior_mean(sample_size,epsilon,delta,priors,observations):
	data = []
	xlabel = []
	for prior in priors:
		for observation in observations:
			Bayesian_Model = BayesInferwithDirPrior(prior, sample_size, epsilon, delta)
			Bayesian_Model._set_observation(observation)
			Bayesian_Model._experiments(300)
			data.append(Bayesian_Model._accuracy[Bayesian_Model._keys[3]])
			data.append(Bayesian_Model._accuracy[Bayesian_Model._keys[0]])
			xstick.append(str(prior._alphas) + ", data:" + str(observation) + "/ExpMech")
			xstick.append(str(prior._alphas) + ", data:" + str(observation) + "/Laplace")

	plot_error_box(data,"Different Prior Distributions",xstick,"Accuracy VS. Prior Distribution")

	return
	


def accuracy_VS_gamma(epsilon,prior, data, gammas):
	mean_error = [[]]
	for g in gammas:
		Bayesian_Model = BayesInferwithDirPrior(prior, sum(data), epsilon, 0.1, g)
		Bayesian_Model._set_observation(data)
		print("start" + str(g))
		Bayesian_Model._experiments(1000)
		print("finished" + str(g))

		mean_error[0].append(Bayesian_Model._accuracy_mean[Bayesian_Model._keys[3]])


	print('Accuracy / prior: ' + str(prior._alphas) + ", delta: " 
		+ str(delta) + ", epsilon:" + str(epsilon))

	# print mean_error

	plot_mean_error(gammas, mean_error, gammas, 
		"Different Gammas for Smooth Sensitivity", 
		[r"$\mathsf{EHDS}$"], "")
	
	# plot_error_box(data,"Different Datasizes",datasizes,"Accuracy VS. Data Size",
	# 	[r'$\mathcal{M}^{B}_{\mathcal{H}}$',"LapMech (sensitivity = 2)", "LapMech (sensitivity = 3)"],
	# 	['lightblue', 'navy', 'red'])
	return

#############################################################################
#GENERATING DATA SIZE AND CONRRESPONDING PARAMETER
#############################################################################

def gen_dataset(v, n):
	return [int(n * i) for i in v]

def gen_datasets(v, n_list):
	return [gen_dataset(v,n) for n in n_list]

def gen_datasizes(r, step):
	return [(r[0] + i*step) for i in range(0,(r[1] - r[0])/step + 1)]

def gen_priors(r, step, d):
	return [dirichlet([step*i for j in range(d)]) for i in range(r[0]/step,r[1]/step + 1)]


if __name__ == "__main__":

#############################################################################
#SETTING UP THE PARAMETERS
#############################################################################

	datasize = 20
	epsilon = 0.1
	delta = 0.00000001
	prior = dirichlet([1,1])
	data = [10,10]


#############################################################################
#SETTING UP THE PARAMETERS WHEN DOING GROUPS EXPERIMENTS
#############################################################################
	epsilons = numpy.arange(5, 2, 0.1)
	datasizes = gen_datasizes((10,50),10) + gen_datasizes((100,500),100) + gen_datasizes((600,1000),200)# + gen_datasizes((1000,5000),1000)#[300] #[8,12,18,24,30,36,42,44,46,48]#,50,52,54,56,58,60,62,64,66,68,70,72,74,76,78,80]
	percentage = [0.5,0.5]
	datasets = gen_datasets(percentage, datasizes)
	priors = gen_priors([20,50], 10, 2) + gen_priors([100,200], 50, 2) + gen_priors([200,500], 100, 2) + gen_priors([600,2000], 200, 2)
	
	gammas = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

#############################################################################
#DOING PLOTS OF ACCURACY V.S. THE DATA SIZE
#############################################################################
	# accuracy_VS_gamma(epsilon, prior, data, gammas)
	
	accuracy_VS_datasize(epsilon,delta,prior,datasets,datasizes)

#############################################################################
#DOING PLOTS OF ACCURACY V.S. THE PRIOR
#############################################################################

	# accuracy_VS_prior(datasize,epsilon,delta,priors,dataset)

#############################################################################
#DOING PLOTS OF ACCURACY V.S. THE PRIOR AND MEAN
#############################################################################

	# accuracy_VS_prior_mean(sample_size,epsilon,delta,priors,observations)

#############################################################################
#DOING PLOTS OF ACCURACY V.S. THE MEAN
#############################################################################

	# accuracy_VS_mean(sample_size,epsilon,delta,prior)

#############################################################################
#DOING PLOTS OF ACCURACY V.S. THE EPSILON
#############################################################################

	# accuracy_VS_epsilon(sample_size,epsilons,delta,prior,observation)



	

