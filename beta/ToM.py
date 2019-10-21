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


def V(OSeller, OBuyer):

	n = max(np.size(OSeller), np.size(OBuyer))
	i = -1 if np.size(OSeller)>1 else 1

	v = i*OBuyer*np.ones(n)
	v[OSeller > OBuyer] = PENALTY

	return v

