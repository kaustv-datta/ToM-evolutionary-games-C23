import numpy as np
import math

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

	v = np.squeeze(i*OBuyer*np.ones([np.size(OSeller), np.size(OBuyer)]))
	v[np.transpose(OSeller[None]) > OBuyer] = PENALTY

	if i<0:
		return np.transpose(v)

	return v


def U(v, p):
	return v.dot(p)


class ToMAgent:
	# General Methods and Fields for ToM agents

	def __init__(self, n_deltas, n_contexts, outer, context = lambda offerSeller, offerBuyer : offerSeller - offerBuyer):

		self.outer = outer
		self.direction = None
		self.computeContext = context

		self.possibleDeltas = np.arange(1/(n_deltas+1), 1 , 1/(n_deltas+1))
		self.n_deltas = n_deltas
		self.n_contexts = n_contexts

	def __call__(self, offerSeller, offerBuyer, context):
		# Get optimal action to do
		pass

	def setDirection(self, newDirection, opponent=None):
		self.direction = newDirection

	def play(self, opponent):
		# Play full bargaining with opponent
		# print("self:", self.direction, "other: ", opponent.direction)
		self.setDirection(1 if self.outer.owner > 0 else -1, opponent) # when it has a nest aka is a seller
		opponent.setDirection( -1*self.direction, self)

		#print("self:", self.direction, "other: ", opponent.direction)

		if self.direction < 0:
			return opponent.play(self)

		# The seller handles the trade (if I get here I am the seller)
		my_offer = 1.0
		opponent_offer = 0.0
		#print("opponent offer:", opponent_offer)
		#print("my offer:", my_offer)

		while(my_offer > opponent_offer):

			# Get binned context
			context = self.computeContext(my_offer, opponent_offer)
			context = math.floor(context*(self.n_contexts-1))

			# Compute next offers for agents
			opponent_new, deltaOpponent = opponent(my_offer, opponent_offer, context)
			my_new, deltaMe = self(my_offer, opponent_offer, context)

			if opponent_offer>=1 or opponent_offer<0 or my_offer<=0 or my_offer>1:
				return None

			# Learn
			opponent.learn(deltaMe, deltaOpponent, context)
			self.learn(deltaMe, deltaOpponent, context)

			# Update offer values
			opponent_offer = opponent_new
			my_offer = my_new

			#print("opponent offer:", opponent_offer, " action: ", deltaOpponent)
			#print("my offer:", my_offer, " action: ", deltaMe)
		#print("/////////////////////////////////////////////////////////")

		# Add stop condition if offer of buyer is lower then the minimum price of the seller.
		# If this is the case there is no exchange
		if opponent_offer*opponent.outer.wealth <= self.outer.owner:
			#print("\tNOT CONCLUDED")
			return None

		#print("\t CONCLUDED!!!!")

		return opponent_offer

class ToM0(ToMAgent):
	# 0-order ToM agent

	def __init__(self, n_deltas, n_contexts, outer, context = lambda offerSeller, offerBuyer : offerSeller - offerBuyer):

		super(ToM0, self).__init__(n_deltas, n_contexts, outer, context)
		self.beliefs = Beliefs0(n_deltas, n_contexts)

	def __call__(self, offerSeller, offerBuyer, context):

		# Compute p dist over opponent's actions
		p = self.beliefs(context)

		# Get value of each agent-opponent action pair
		v = V(offerSeller - self.possibleDeltas, offerBuyer + self.possibleDeltas, self.direction)

		# Compute optimal action (the index of the delta to use)
		action = np.argmax(U(v, p))
		# Return offer with respect to optimal action
		# print((offerSeller if self.direction>0 else offerBuyer), " - ", self.direction, "*", self.possibleDeltas[action])
		return (offerSeller if self.direction>0 else offerBuyer) -self.direction*self.possibleDeltas[action], action

	def learn(self, deltaSeller, deltaBuyer, context):

		if self.direction > 0:
			self.beliefs.observe(deltaBuyer, context)
		else:
			self.beliefs.observe(self.n_deltas -1 -deltaSeller, context)


class ToM1(ToMAgent):
	# 1-order ToM agent

	def __init__(self, n_deltas, n_contexts, outer, context = lambda offerSeller, offerBuyer : offerSeller - offerBuyer):

		super(ToM1,self).__init__(n_deltas, n_contexts, outer, context)
		self.model = ToM0(n_deltas, n_contexts, None, None)

	def setDirection(self, newDirection, opponent):
		super(ToM1, self).setDirection(newDirection, opponent)
		self.model.outer = opponent
		self.model.setDirection(-1*self.direction)

	def __call__(self, offerSeller, offerBuyer, context):

		# Predict action of opponent
		opponent_action, _ = self.model(offerSeller, offerBuyer, context)

		if self.direction>0:
			sellerDeltas = self.possibleDeltas-offerSeller
			buyerDeltas = opponent_action
		else:
			buyerDeltas = self.possibleDeltas+offerBuyer
			sellerDeltas = opponent_action

		# Compute values for each of your actions
		v = V(sellerDeltas, buyerDeltas, self.direction)

		# Compute optimal action (the index of the delta to use)
		action = np.argmax(v)
		# Return offer with respect to optimal action
		# print((offerSeller if self.direction>0 else offerBuyer), " - ", self.direction, "*", self.possibleDeltas[action])
		return (offerSeller if self.direction>0 else offerBuyer)-self.direction*self.possibleDeltas[action], action

	def learn(self, deltaSeller, deltaBuyer, context):

		self.model.learn(deltaSeller, deltaBuyer, context)

