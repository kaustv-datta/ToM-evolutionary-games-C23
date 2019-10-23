import numpy as np

PENALTY = -4

class Beliefs0:

	def __init__(self, n_deltas, n_contexts):

		self.b = np.ones([n_contexts, n_deltas])

	def __call__(self, context, delta=None):

		p = self.b[context]
		s = np.sum(p)

		if not delta:
			return p/s

		return p[delta]/s


	def observe(self, context, delta):
		self.b[context, delta] += 1


def V(OSeller, OBuyer, i=-1):

	v = i*OBuyer*np.ones([np.size(OSeller), np.size(OBuyer)])
	v[OSeller.T > OBuyer] = PENALTY

	if i<0:
		return v.T

	return v


def U(v, p):
	return v.dot(p)


class ToMAgent:
	# General Methods and Fields for ToM agents

	def __init__(self, n_deltas, n_contexts, directon, context = lambda offerMe, offerOther : offerMe - offerOther):

		self.direction = direction
		self.computeContext = context

		self.possibleDeltas = np.arange(0, 1 + 1/n_deltas, n_deltas)
		self.n_contexts = n_contexts

	def __call__(self, offerSeller, offerBuyer):
		# Get optimal action to do
		pass

	def play(self, opponent):
		# Play full bargaining with opponent
		if self.direction < 0:
			if opponent.direction < 0: # Two buyers
				return None
			return opponent.play(self)

		# The seller handles the trade (if I get here I am the seller)
		my_offer = 1.0
		opponent_offer = 0.0

		while(my_offer > opponent_offer): # Add stop condition in case my_offer gets lower than buying price

			opponent_new = opponent(my_offer, opponent_offer)
			my_new = self(my_offer, opponent_offer)

			opponent_offer = opponent_new
			my_offer = my_new



class ToM0(ToMAgent):
	# 0-order ToM agent

	def __init__(self, n_deltas, n_contexts, directon, context = lambda offerMe, offerOther : offerMe - offerOther):

		super(self, ToM0).__init__(n_deltas, n_contexts, direction, context)
		self.beliefs = Beliefs0(n_deltas, n_contexts)

	def __call__(self, offerSeller, offerBuyer):

		# Get binned context
		context = self.direction*self.computeContext(prevOffer, prevOfferOther)
		context = int(context/self.n_contexts)

		# Compute p dist over opponent's actions
		p = self.beliefs(context)

		# Get value of each agent-opponent action pair
		v = V(self.__possibleDeltas+offerSeller, self.__possibleDeltas+offerBuyer, self.direction)

		# Compute optimal action (the index of the delta to use)
		action = np.argmax(U(v, p))
		# Return offer with respect to optimal action
		return (offerSeller if self.direction else offerBuyer) + self.__possibleDeltas[action]
