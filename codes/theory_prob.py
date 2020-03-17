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


# class TheoryProbs(object):
# 	def __init__(self, dataobs, prior, eps):
		
def LAPLACE_CDF(interval, scale):
	if interval[0] >= 0.0:
		return (1 - 0.5 * math.exp( (-interval[1]*1.0/scale))) - (1 - 0.5 * math.exp( (-interval[0]/scale)))
	else:
		return (0.5 * math.exp( (interval[1]*1.0/scale))) - (0.5 * math.exp( (interval[0]/scale)))

def list2key(l):
	return ':'.join(map(str, l))

def lap_distribution_over_candidates(dataobs, prior, eps, sensitivity = 1.0):
	lap_prob = {}

	n = sum(dataobs)

	k = dataobs[0]

	############### the expected error when the noises are valid######
	for t in range(- k, n - k + 1):
		c = [k + t, n - k - t]
		lap_prob[list2key(c)] = 0.5 * LAPLACE_CDF((t, t+1), sensitivity/eps) + 0.5 * LAPLACE_CDF((-t, -t + 1), sensitivity/eps)

	r = 0.5 * (1 - sum(lap_prob.values()) )
	############### the expected error when the noises are not valid######
	# lap_prob[str([0,n])] += 0.5 * (0.5 - LAPLACE_CDF((- k, 0.0), sensitivity/eps)) +  0.5 * (0.5 - LAPLACE_CDF((0.0, k + 1), sensitivity/eps))

	# lap_prob[str([n,0])] += 0.5 * (0.5 - LAPLACE_CDF((0.0, n - k + 1), sensitivity/eps)) + 0.5 * (0.5 - LAPLACE_CDF((-(n - k), 0.0), sensitivity/eps))
	lap_prob[list2key([0,n])] += r
	lap_prob[list2key([n,0])] += r

	print sensitivity, lap_prob

	return lap_prob

def lap_distribution_over_candidates_naive(dataobs, prior, eps, sensitivity = 2.0):
	lap_prob = {}

	n, tra, trb = sum(dataobs), dataobs[0], dataobs[1]


	############### the expected error when the noises are valid######
	for a in range(0, n + 1):
		for b in range(0, n + 1):
			a_, b_ = a - tra , b - trb
			lap_prob[list2key([a, b])] = LAPLACE_CDF((a_, a_ + 1), sensitivity/eps) * LAPLACE_CDF((b_, b_ + 1), sensitivity/eps)
			if a == 0:
				lap_prob[list2key([a, b])] += (0.5 - LAPLACE_CDF((a_, 0), sensitivity/eps)) * LAPLACE_CDF((b_, b_ + 1), sensitivity/eps)
			if a == n:
				lap_prob[list2key([a, b])] += (0.5 - LAPLACE_CDF(( 0, a_ + 1), sensitivity/eps)) * LAPLACE_CDF((b_, b_ + 1), sensitivity/eps)
			if b == 0:
				lap_prob[list2key([a, b])] += LAPLACE_CDF((a_, a_ + 1), sensitivity/eps) * (0.5 - LAPLACE_CDF((b_, 0.0), sensitivity/eps))
			if b == n:
				lap_prob[list2key([a, b])] +=LAPLACE_CDF((a_, a_ + 1), sensitivity/eps) * (0.5 - LAPLACE_CDF((0, b_ + 1), sensitivity/eps))
	############### the expected error when the noises are not valid######
	# lap_prob[str([0,n])] = (0.5 - LAPLACE_CDF((- tra, 0.0), sensitivity/eps)) * (0.5 - LAPLACE_CDF((0.0, trb + 1), sensitivity/eps))

	# lap_prob[str([n,0])] = (0.5 - LAPLACE_CDF((0.0, n - tra + 1), sensitivity/eps)) + 0.5 * (0.5 - LAPLACE_CDF((-trb, 0.0), sensitivity/eps))
	r = 0.5 * (1 - sum(lap_prob.values()) )
	lap_prob[list2key([0,n])] += r
	lap_prob[list2key([n,0])] += r
	

	print sensitivity, lap_prob

	return lap_prob

def exp_distribution_over_candidates(dataobs, prior, epsilon, mech):
	n = sum(dataobs)
	Bayesian_Model = BayesInferwithDirPrior(prior, n, epsilon)
	Bayesian_Model._set_observation(dataobs)

	Bayesian_Model._set_candidate_scores()
	Bayesian_Model._set_local_sensitivities()
	if mech == "exp":
		Bayesian_Model._set_up_exp_mech_with_GS()
	elif mech == "gamma":
		Bayesian_Model._gamma = 0.25
		Bayesian_Model._epsilon = epsilon * 8.0/5
		Bayesian_Model._set_up_exp_mech_with_gamma_SS()

	exp_prob = {}

	for i in range(len(Bayesian_Model._candidates)):
		z = Bayesian_Model._candidates[i]._pointwise_sub(prior)
		if mech == "exp":
			exp_prob[list2key(z._alphas)] = Bayesian_Model._GS_probabilities[i]
		elif mech == "gamma":
			exp_prob[list2key(z._alphas)] = Bayesian_Model._gamma_SS_probabilities[i]

		
	# print exp_prob
	
	return exp_prob



def get_steps(dataobs, prior, epsilon):
	n = sum(dataobs)
	# Bayesian_Model = BayesInferwithDirPrior(prior, n, epsilon)
	# Bayesian_Model._set_observation(dataobs)

	# Bayesian_Model._set_candidate_scores()

	# cpara = []
	# for c in Bayesian_Model._candidates:
	# 	cpara.append(str(c._minus(prior)._alphas))
	
	cpara = []
	
	for a in range(0, n + 1):
		for b in range(0, n + 1):
			cpara.append(list2key([a,b]))

	return cpara


def list_of_map(keys, maps):
	lists = []
	print "key:", keys
	for m in maps:
		l = []
		for k in keys:
			if k in m:
				l.append(m[k])
			else:
				l.append(0.0)
		lists.append(l)
	return lists


def plot_2d(y, xstick, labels, title):
	plt.figure()
	x = range(len(xstick))
	for i in range(len(y)):
		x_, y_ = [], []
		for j in range(len(y[i])):
			if y[i][j] != 0:
				y_.append(y[i][j])
				x_.append(x[j])
		plt.plot(x_, y_, "o-", label=labels[i])
	plt.xlabel(r"different dataset: $[k, n- k]$")
	plt.xticks(x,xstick,rotation=70,fontsize=6)
	plt.title(title)
	plt.legend(loc='best',fontsize=6)
	plt.grid()
	plt.show()


def gen_dataset(v, n):
	return [int(n * i) for i in v]


def gen_datasets(v, n_list):
	return [gen_dataset(v,n) for n in n_list]


def gen_datasizes(r, step):
	return [i*step for i in range(r[0]/step,r[1]/step + 1)]


def gen_priors(r, step, d):
	return [dirichlet([step*i for j in range(d)]) for i in range(r[0]/step,r[1]/step + 1)]


if __name__ == "__main__":

	datasize = 2
	epsilon = 1.0
	delta = 0.00000001
	prior = dirichlet([1,1])
	dataobs = [10, 10]
	# datasizes = gen_datasizes((50, 200), 50)

	lap_prob = lap_distribution_over_candidates(dataobs, prior, epsilon, 1.0)
	lap_prob_2 = lap_distribution_over_candidates(dataobs, prior, epsilon, 2.0)
	exp_prob = exp_distribution_over_candidates(dataobs, prior, epsilon, "exp")
	exp_prob2 = exp_distribution_over_candidates(dataobs, prior, epsilon, "gamma")
	lap3 = lap_distribution_over_candidates_naive(dataobs, prior, epsilon)
	steps = get_steps(dataobs, prior, epsilon)

	plot_2d(list_of_map(steps, [lap_prob, lap_prob_2, lap3, exp_prob, exp_prob2]),
		steps, [r"$\mathsf{LSHist}$", r"$\mathsf{LSDim}$", r"$\mathsf{LSDimNa}$", r"$\mathsf{EHD}$", r"$\mathsf{EHDS}$"], "prob of each candidates with data: "+str(dataobs)+", eps: " + str(epsilon))

