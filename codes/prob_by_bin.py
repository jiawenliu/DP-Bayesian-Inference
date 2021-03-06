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


def LAPLACE_CDF(interval, scale):
	if interval[0] >= 0.0:
		return (1 - 0.5 * math.exp( (-interval[1]*1.0/scale))) - (1 - 0.5 * math.exp( (-interval[0]/scale)))
	else:
		return (0.5 * math.exp( (interval[1]*1.0/scale))) - (0.5 * math.exp( (interval[0]/scale)))


#############################################################################
#SUM UP the prob within the same bin
#############################################################################
def exp_distribution_over_candidates(dataobs, prior, epsilon, mech):
	n = sum(dataobs)
	Bayesian_Model = BayesInferwithDirPrior(prior, n, epsilon)
	Bayesian_Model._set_observation(dataobs)

	Bayesian_Model._set_candidate_scores()
	Bayesian_Model._set_local_sensitivities()
	if mech == "exp":

		Bayesian_Model._set_up_exp_mech_with_GS()
	elif mech == "gamma":
		Bayesian_Model._set_up_exp_mech_with_gamma_SS()
	else:
		Bayesian_Model._set_up_exp_mech_with_LS()

	exp_prob = {}

	for i in range(len(Bayesian_Model._candidates)):
		z = Bayesian_Model._candidates[i]._pointwise_sub(prior)
		if mech == "exp":
			exp_prob[str(z._alphas)] = Bayesian_Model._GS_probabilities[i]
		elif mech == "gamma":
			exp_prob[str(z._alphas)] = Bayesian_Model._gamma_SS_probabilities[i]
		else:
			exp_prob[str(z._alphas)] = Bayesian_Model._LS_probabilities[i]


		
	# print exp_prob
	
	return exp_prob

def calculate_prob_exp(bins, Bayesian_Model, mech):
	exp_prob = exp_distribution_over_candidates(Bayesian_Model._observation_counts, Bayesian_Model._prior, Bayesian_Model._epsilon, mech)
	prob_by_bin = []
	for key,item in bins.items():
		p = 0.0
		for c in item:
			p += exp_prob[str(c._pointwise_sub(Bayesian_Model._prior)._alphas)]

		prob_by_bin.append((-Bayesian_Model._candidate_scores[item[0]], p))
	print prob_by_bin
	prob_by_bin.sort()
	t, exp = zip(*prob_by_bin)
	return exp

# def calculate_prob_exp(bins, Bayesian_Model, mechanism_parameter, sensitivity, savename):

# 	#############################################################################
# 	#CALCULATING THE UNOMARLIZED PROBABILITY OF EACH BIN
# 	#############################################################################

# 	probability_distance_pairs_in_exp =[]

# 	nomalizer = 0.0

# 	for key,item in bins.items():
# 		distance = -Bayesian_Model._candidate_scores[item[0]]
		
# 		#THE PROBABILITY OF THIS BIN
# 		prob = (len(item) * math.exp(Bayesian_Model._epsilon * Bayesian_Model._candidate_scores[item[0]]/(mechanism_parameter * sensitivity)))

# 		probability_distance_pairs_in_exp.append((distance, prob, [i._alphas for i in item]))

# 		nomalizer += prob

# 	#############################################################################
# 	#NOMARLIZING PROBABILITY
# 	#############################################################################

# 	probability_distance_pairs_in_exp = [(t[0],t[1]/nomalizer,t[2]) for t in probability_distance_pairs_in_exp]


# 	probability_distance_pairs_in_exp.sort()

# 	#############################################################################
# 	#SORT AND SPLIT THE PROBABILITY FROM PAIRS #WRITE DATAS INTO FILE
# 	#############################################################################

# 	# f_exp = open("datas/discrete_prob/data_" + str(Bayesian_Model._observation_counts) + savename, "w")

# 	# f_exp.write("Candidates_of_the_same_steps&Hellinger Distance&Probabilities \n")

# 	# for triple in probability_distance_pairs_in_exp:
# 	# 	#WRITE DATAS INTO FILE
# 	# 	f_exp.write(str(triple[2]) + "&" + str(triple[0]) + "&" + str(triple[1]) + "\n")
	
# 	# f_exp.close()


# 	t, exp, _ = zip(*probability_distance_pairs_in_exp)

# 	return exp

#############################################################################
#CALCULATE the Laplace prob within the same bin
#############################################################################

def calculate_prob_lap(bins, Bayesian_Model, sensitivity, savename):
	
	#############################################################################
	#SENSITIVITY SETTING
	#############################################################################
	
	# f_lap = open("datas/discrete_prob/data_" + str(Bayesian_Model._observation_counts) + savename, "w")
	
	# f_lap.write("Candidates_of_the_same_steps, Hellinger Distance, Probabilities \n")

	
	#############################################################################
	#CALCULATING THE LAPLACE PROB
	#############################################################################
	
	probability_distance_pairs_in_lap = []

	for key,item in bins.items():
		p1 = 0.0
		for r in item:
			t1 = 1.0
			#THE LAPLACE PROBABILITY OF THIS BIN
			for j in range(len(r._alphas) - 1):
				a = r._alphas[j] - Bayesian_Model._posterior._alphas[j]
				t1 = t1 * LAPLACE_CDF((a,a+1), sensitivity/Bayesian_Model._epsilon)
			p1 += t1

		probability_distance_pairs_in_lap.append((-Bayesian_Model._candidate_scores[item[0]],p1,[i._alphas for i in item]))
	

	#############################################################################
	#SORT AND SPLIT THE PROBABILITY FROM BINS WRITEINTO FILE
	#############################################################################
	probability_distance_pairs_in_lap.sort()

	for i in range(len(probability_distance_pairs_in_lap)):
		e = probability_distance_pairs_in_lap[i]

	# 	f_lap.write(str(e[2]) + "&" + str(e[0]) +"&" + str(e[1]) + "\n")

	# f_lap.close()

	t, lap, _ = zip(*(probability_distance_pairs_in_lap))

	#############################################################################
	#TAIL PROBABILITY
	#############################################################################
	lap = list(lap)

	lap[-1] = 1.0 - sum(lap[:-1])

	return t,lap


#############################################################################
#CALCULATING THE DISCRETE PROBABILITIES
#############################################################################

def row_discrete_probabilities(sample_size, epsilon,delta,prior,observation):

	Bayesian_Model = BayesInferwithDirPrior(prior, sample_size, epsilon, delta)
	Bayesian_Model._set_observation(observation)
	print Bayesian_Model._observation_counts

	Bayesian_Model._set_candidate_scores()
	Bayesian_Model._set_local_sensitivities()
	Bayesian_Model._set_up_exp_mech_with_gamma_SS()
	Bayesian_Model._set_up_exp_mech_with_SS()
	Bayesian_Model._set_up_exp_mech_with_GS()
	Bayesian_Model._set_up_exp_mech_with_LS()


	#############################################################################
	#SPLIT THE BINS
	#############################################################################
	
	Candidate_bins_by_step = {}
	probability_distance_pairs_in_exp =[]

	nomalizer = 0.0

	sorted_scores = sorted(Bayesian_Model._candidate_scores.items(), key=operator.itemgetter(1))
	counter = 0
	while counter < len(sorted_scores):
		flage = counter
		key = str(sorted_scores[flage][1])
		Candidate_bins_by_step[key] = []
		# parameters_of_bin = []
		while counter < len(sorted_scores) and sorted_scores[flage][1] == sorted_scores[counter][1]:
			Candidate_bins_by_step[key].append(sorted_scores[counter][0])
			# parameters_of_bin.append(sorted_scores[counter][0]._alphas)
			counter += 1
		# print parameters_of_bin
		print key


	#############################################################################
	#SPLIT THE BINS
	#############################################################################
	
	# Candidate_bins_by_step = {}
	# for r in Bayesian_Model._candidates:
	# 	if str(sorted(r._alphas)) not in Candidate_bins_by_step.keys():
	# 		Candidate_bins_by_step[str(sorted(r._alphas))] = []
	# 		for c in Bayesian_Model._candidates:
	# 			if set(c._alphas) == set(r._alphas):
	# 				Candidate_bins_by_step[str(sorted(r._alphas))].append(c)

			


	#############################################################################
	#SUM UP the prob within the same bin
	#############################################################################

	# exp = calculate_prob_exp(Candidate_bins_by_step, Bayesian_Model, mechanism_parameter = 4, 
	# 	sensitivity = Bayesian_Model._SS, savename = "_exp.txt")


	#############################################################################
	#SUM UP the prob within the same bin
	#############################################################################

	exp_gamma = calculate_prob_exp(Candidate_bins_by_step, Bayesian_Model,
		"gamma")


	#############################################################################
	#SUM UP the prob within the same bin
	#############################################################################
	exp_LS = calculate_prob_exp(Candidate_bins_by_step, Bayesian_Model,
		"local")

	#############################################################################
	#SUM UP the prob within the same bin
	#############################################################################
	exp_GS = calculate_prob_exp(Candidate_bins_by_step, Bayesian_Model,
		"exp")
	
	#############################################################################
	#SETTING THE SENSITIVITY
	#############################################################################
	
	if (len(prior._alphas) == 2):
		sensitivity1 = 1.0
		sensitivity2 = 2.0
	else:
		sensitivity1 = 2.0
		sensitivity2 = len(prior._alphas)*1.0


	#############################################################################
	#CALCULATE the Laplace prob within the same bin
	#############################################################################
	
	step,lap_1 = calculate_prob_lap(Candidate_bins_by_step, Bayesian_Model, 
		sensitivity = sensitivity1, savename = "_lap_1.txt")

	step,lap_2 = calculate_prob_lap(Candidate_bins_by_step, Bayesian_Model, 
		sensitivity = sensitivity2, savename = "_lap_2.txt")

	print step, exp_gamma, lap_1, lap_2
	# return


	#############################################################################
	#PLOT the prob within the same bin
	#############################################################################

	#############################################################################
	#LABELS SETTING
	#############################################################################

	labels = [
		r'Alg 5 - $\mathsf{EHDS}$ ',
		r"Alg 4 - $\mathsf{EHDL}$",
		r"Alg 3 - $\mathsf{EHD}$",
		r'Alg 1 - $\mathsf{LSDim}$ (sensitivity = '+ str(sensitivity2) +')', 
		r'Alg 2 - $\mathsf{LSHist}$ (sensitivity = '+ str(sensitivity1) +')']


	#############################################################################
	#PLOTTING
	#############################################################################

	plt.figure()
	plt.plot(step, lap_2, '-',color = 'lightblue', label=(labels[3]))
	
	plt.plot(step, lap_1,'-', color = 'navy', label=(labels[4]))

	plt.plot(step, exp_GS, '-', label=(labels[2]))

	plt.plot(step, exp_LS, '-', label=(labels[1]))

	plt.plot(step, exp_gamma, '-', label=(labels[0]))






	# plt.plot(step, exp,  label=(labels[0]))

	# plt.plot(step, exp_new, label=(labels[1]))

	# plt.plot(step, exp_LS,  label=(labels[2]))

	# plt.plot(step, exp_GS,  label=(labels[3]))

	# plt.plot(step, lap_1, color = 'navy', label=(labels[4]))

	# plt.plot(step, lap_2, color = 'lightblue', label=(labels[5]))

	#############################################################################
	#PLOT FEATURE SETTING
	#############################################################################

	plt.xlabel("c / Hellinger distance from true posterior")
	plt.ylabel("Pr[H(BI(x),r) = c]")
	plt.title("Accuracy with Data size "+str(sample_size), fontsize=15)
	plt.legend()
	plt.grid()
	plt.show()



def discrete_probabilities_from_file(filenames,labels,savename):
	
	#############################################################################
	#READ the prob from file
	#############################################################################

	probabilities_by_steps = []
	steps = []
	for file in filenames:
		f = open(file, "r")
		f.readline()
		s = []
		prob = []
		for line in f:
			l = line.strip("\n").split("&")
			prob.append(float(l[-1]))
			s.append(float(l[-2]))
		probabilities_by_steps.append(prob)
		steps = s

	#############################################################################
	#PLOT the prob within the same bin
	#############################################################################

	plt.figure()
	colors = ["b","r","g"]

	for i in range(len(filenames)):
		plt.plot(steps[-100:], probabilities_by_steps[i][-100:], colors[i], label=(labels[i]))
		# plt.plot(T, approximate_bounds, 'g^', label=('Expmech_SS zApproximate Bound'))
	plt.xlabel("c / (steps from correct answer, in form of Hellinger Distance)")
	plt.ylabel("Pr[H(BI(x),r) = c]")
	plt.title("Discrete Probabilities")
	plt.legend()
	plt.grid()
	plt.show()


	#############################################################################
	#GENERATING DATA SIZE AND CONRRESPONDING PARAMETER
	#############################################################################

def gen_dataset(v, n):
	return [int(n * i) for i in v]


def gen_datasets(v, n_list):
	return [gen_dataset(v,n) for n in n_list]


def gen_datasizes(r, step):
	return [i*step for i in range(r[0]/step,r[1]/step + 1)]


def gen_priors(r, step, d):
	return [dirichlet([step*i for j in range(d)]) for i in range(r[0]/step,r[1]/step + 1)]


if __name__ == "__main__":

	#############################################################################
	#SETTING UP THE PARAMETERS
	#############################################################################
	datasize = 4
	epsilon = 1.0
	delta = 0.00000001
	prior = dirichlet([1,1])
	dataset = [2,2]

	#############################################################################
	#SETTING UP THE PARAMETERS WHEN DOING GROUPS EXPERIMENTS
	#############################################################################
	
	datasizes = gen_datasizes((600,600),50)
	percentage = [0.5,0.5]
	datasets = gen_datasets(percentage, datasizes)
	priors = [dirichlet([1,1])] + gen_priors([5,20], 5, 2) + gen_priors([40,100], 20, 2) + gen_priors([150,300], 50, 2) + gen_priors([400,400], 50, 2)

	#############################################################################
	#DO PLOTS BY COMPUTING THE PROBABILITIES FOR GROUP EXPERIMENTS
	#############################################################################

	# for i in range(len(datasizes)):
	# 	row_discrete_probabilities(datasizes[i],epsilon,delta,prior,datasets[i])

	#############################################################################
	#DO PLOTS BY COMPUTING THE PROBABILITIES
	#############################################################################

	row_discrete_probabilities(datasize,epsilon,delta,prior,dataset)

	#############################################################################
	#DO PLOTS BY READING THE PROB FROM FILES
	#############################################################################



	

