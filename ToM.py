import numpy as np
import math

PENALTY = -4


def V(OSeller, OBuyer, i=-1):
    """Method to compute the discrete value function for a set of possible future offers

            Arguments:
                    OSeller {integer or numpy.array of integers} -- single seller offer or all possible offers, taken into account
                    OBuyer {integer or numpy.array of integers} -- single buyer offer or all possible offers, taken into account
                    i {-1 or 1} -- point of view (if -1 value is computed for buyer, if 1 for seller)

            Returns:
                    numpy.array of doubles -- value function of cartesian product of all given offers (of seller and buyer),
                    each row is a possible action of the acting agent, each column a possible action of the opponent
            """
    v = np.squeeze(
        i * OBuyer * np.ones([np.size(OSeller), np.size(OBuyer)]))
    v[np.squeeze(np.transpose(OSeller[None]) > OBuyer)] = PENALTY

    if i < 0:
        return np.transpose(v)

    return v


def U(v, p):
    """Method computing the expected value of offers

            Arguments:
                 v {numpy.array} -- matrix or vector representing value function for agent
                p {numpy.array} -- vector representing probability distribution of future actions of the opponent

            Returns:
                 numpy.array -- vector of expected values for each possible action of the agent
             """

    return v.dot(p)


class Beliefs0:
    """Zero order beliefs"""

    def __init__(self, n_deltas, n_contexts):
        """Constructor for zero order beliefs

                Arguments:
                        Beliefs {Beliefs0 object} -- constructed object
                        n_deltas {integer} -- number of bins for deltas interval
                        n_contexts {integer} -- number of bins for contexts interval
                """

        self.b = np.ones([n_contexts, n_deltas])

    def __call__(self, context, delta=None):
        """Get probability of a(ll) delta(s) bin(s) given a context bin

                Arguments:
                        self {Beliefs0 object} -- beliefs on which method is called
                        context {integer} -- index of context bin
                        delta {integer} -- optional, index of delta's bin

                Returns:
                        __call__(self, context, delta):
                        double -- the probability of the given delta, for the given context

                        __call__(self, context):
                        numpy.array of doubles -- the probability of each possible delta bin for the given context
                """

        p = self.b[context]
        s = np.sum(p)

        if not delta:
            return p / s

        return p[delta] / s

    def observe(self, context, delta):
        """Update beliefs

                Arguments:
                        self {Beliefs0 object} -- beliefs on which method is called
                        context {integer} -- index of observed context bin
                        delta {integer} -- index of observed delta bin
                """
        self.b[context, delta] += 1


class ToMAgent:
	"""Super class containing general methods for any order of theory of mind"""

	def __init__(self, n_deltas, n_contexts, outer, context = lambda offerSeller, offerBuyer : offerSeller - offerBuyer):
		"""General constructor for any order of theory of mind

		Arguments:
			self {ToMAgent object} -- constructed object
			n_deltas {integer} -- number of bins for deltas interval
			n_contexts {integer} -- number of bins for contexts interval
			outer {Agent.Agent} -- agent containing ToMAgent object
			context {lambda (double, double) -> double} -- function defining how context is computed from the offer of the seller and the buyer
		"""

		self.outer = outer
		self.direction = None
		self.computeContext = context

		self.possibleDeltas = np.arange(1/(n_deltas+1), 1 , 1/(n_deltas+1))
		self.n_deltas = n_deltas
		self.n_contexts = n_contexts

	def __call__(self, offerSeller, offerBuyer, context):
		"""Method to get the agent's action (agent performs a decision)

		Arguments:
			self {ToMAgent} -- agent performing the action
			offerSeller {dobule} -- offer made by seller in previous round
			offerBuyer {dobule} -- offer made by buyer in previous round
			context {integer} -- index of current context's bin

		Returns:
			double -- offer made
			integer -- index of delta bin used
		"""
		pass

	def learn(self, deltaSeller, deltaBuyer, context):
		"""Method to updated agent's beliefs

		Arguments:
			self {ToMAgent} -- agent whose beliefs are being updated
			deltaSeller {integer} -- index of bin of delta used by the seller
			deltaBuyer {integer} -- integer of bin of delta used by the buyer
			context {integer} -- integer of bin of current context
		"""
		pass

	def setDirection(self, newDirection, opponent=None):
		"""Setter for direction field

		Arguments:
			self {ToMAgent} -- agent whose direction is being set
			newDirection {-1 or 1} -- new value of direction field
			opponent {ToMAgent} -- opponent (other end of direction)
		"""

		self.direction = newDirection

        # Add stop condition if offer of buyer is lower then the minimum price of the seller.
        # If this is the case there is no exchange
        if opponent_offer * opponent.outer.wealth <= self.outer.owner:
            return None

        return opponent_offer


class ToM0(ToMAgent):

    def __init__(
            self,
            n_deltas,
            n_contexts,
            outer,
            context=lambda offerSeller,
                           offerBuyer: offerSeller -
                                       offerBuyer):
        """General constructor for any order of theory of mind

                Arguments:
                        self {ToM0 object} -- constructed object
                        n_deltas {integer} -- number of bins for deltas interval
                        n_contexts {integer} -- number of bins for contexts interval
                        outer {Agent.Agent} -- agent containing ToMAgent object
                        context {lambda (double, double) -> double} -- function defining how context is computed from the offer of the seller and the buyer
                """

        super(ToM0, self).__init__(n_deltas, n_contexts, outer, context)
        self.beliefs = Beliefs0(n_deltas, n_contexts)

    def __call__(self, offerSeller, offerBuyer, context):
        """Method to get the agent's action (agent performs a decision)

                Arguments:
                        self {ToMAgent} -- agent performing the action
                        offerSeller {dobule} -- offer made by seller in previous round
                        offerBuyer {dobule} -- offer made by buyer in previous round
                        context {integer} -- index of current context's bin

                Returns:
                        double -- offer made
                        integer -- index of delta bin used
                """

        # Compute p dist over opponent's actions
        p = self.beliefs(context)

        # Get value of each agent-opponent action pair
        v = V(offerSeller - self.possibleDeltas, offerBuyer + self.possibleDeltas, self.direction)

        # Compute optimal action (the index of the delta to use)
        action = np.argmax(U(v, p))
        # Return offer with respect to optimal action
        return (offerSeller if self.direction > 0 else offerBuyer) - \
               self.direction * self.possibleDeltas[action], action

    def learn(self, deltaSeller, deltaBuyer, context):
        """Method to updated agent's beliefs

                Arguments:
                        self {ToMAgent} -- agent whose beliefs are being updated
                        deltaSeller {integer} -- index of bin of delta used by the seller
                        deltaBuyer {integer} -- integer of bin of delta used by the buyer
                        context {integer} -- integer of bin of current context
                """

        if self.direction > 0:
            self.beliefs.observe(context, deltaBuyer)
        else:
            self.beliefs.observe(context, self.n_deltas - 1 - deltaSeller)


class ToM1(ToMAgent):

    def __init__(
            self,
            n_deltas,
            n_contexts,
            outer,
            context=lambda offerSeller, offerBuyer: offerSeller - offerBuyer):
        """General constructor for any order of theory of mind

                Arguments:
                        self {ToM1 object} -- constructed object
                        n_deltas {integer} -- number of bins for deltas interval
                        n_contexts {integer} -- number of bins for contexts interval
                        outer {Agent.Agent} -- agent containing ToMAgent object
                        context {lambda (double, double) -> double} -- function defining how context is computed from the offer of the seller and the buyer
                """

        super(ToM1, self).__init__(n_deltas, n_contexts, outer, context)
        self.model = ToM0(n_deltas, n_contexts, None, None)

    def setDirection(self, newDirection, opponent):
        """Setter for direction field

                Arguments:
                        self {ToMAgent} -- agent whose direction is being set
                        newDirection {-1 or 1} -- new value of direction field
                        opponent {ToMAgent} -- opponent (other end of direction)
                        """

        super(ToM1, self).setDirection(newDirection, opponent)

        self.model.outer = opponent
        self.model.setDirection(-1 * self.direction)

    def __call__(self, offerSeller, offerBuyer, context):
        """Method to get the agent's action (agent performs a decision)

                Arguments:
                        self {ToMAgent} -- agent performing the action
                        offerSeller {dobule} -- offer made by seller in previous round
                        offerBuyer {dobule} -- offer made by buyer in previous round
                        context {integer} -- index of current context's bin

                Returns:
                        double -- offer made
                        integer -- index of delta bin used
                """

        # Predict action of opponent
        opponent_action, _ = self.model(offerSeller, offerBuyer, context)

        if self.direction > 0:
            sellerDeltas = self.possibleDeltas - offerSeller
            buyerDeltas = opponent_action
        else:
            buyerDeltas = self.possibleDeltas + offerBuyer
            sellerDeltas = opponent_action

        # Compute values for each of your actions
        v = V(sellerDeltas, buyerDeltas, self.direction)

        # Compute optimal action (the index of the delta to use)
        action = np.argmax(v)
        # Return offer with respect to optimal action
        return (offerSeller if self.direction > 0 else offerBuyer) - \
               self.direction * self.possibleDeltas[action], action

    def learn(self, deltaSeller, deltaBuyer, context):
        """Method to updated agent's beliefs

                Arguments:
                        self {ToMAgent} -- agent whose beliefs are being updated
                        deltaSeller {integer} -- index of bin of delta used by the seller
                        deltaBuyer {integer} -- integer of bin of delta used by the buyer
                        context {integer} -- integer of bin of current context
                """

        self.model.learn(deltaSeller, deltaBuyer, context)
