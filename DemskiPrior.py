from z3 import *
from random import randint


def DemskiPrior(knowledgeBase, variables, variableOfInterest) :


	# Check if knowledge base is consistent
	T = Solver()
	for sentence in knowledgeBase :
		T.add(sentence)
	if (T.check() == unsat) :
		sys.exit("Background knowledge not consistent")

	T = Solver()
	# Demski prior generation algorithm
	###################################
	numLoops = 100

	interestCount = 0
	for k in range(0,numLoops) :


		#Add the original knowledge base
		T.reset()
		for sentence in knowledgeBase :
			T.add(sentence)
		remainingVariables = list(variables)


		for i in range(0,len(variables)) :
			nextVar = randint(0,len(remainingVariables)-1)

			# Randomly add the variable or its negation
			if (randint(0,1) > 0) :
				T.push()
				T.add(remainingVariables[nextVar])

				if (T.check() == unsat) :
					T.pop()
					T.add(Not(remainingVariables[nextVar]))

			else :
				T.push()
				T.add(Not(remainingVariables[nextVar]))

				if (T.check() == unsat) :
					T.pop()
					T.add(remainingVariables[nextVar])
			

			remainingVariables.pop(nextVar)
		T.add(variableOfInterest)
		if (T.check() == sat) :
			interestCount += 1



	print("Proportion was " + str(interestCount) + "/" + str(numLoops))

