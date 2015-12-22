from z3 import *
from random import randint

A = Bool('A')
B = Bool('B')
C = Bool('C')

# The set of variables
Variables = [A,B,C]


# Check if knowledge base is consistent
T = Solver()
T.add(B,Not(B))
if (T.check() == unsat) :
	sys.exit("Background knowledge not consistent")


# Demski prior generation algorithm
###################################
numLoops = 100

cCount = 0
for k in range(0,numLoops) :


	#Add the original knowledge base
	T = Solver()
	T.add(Implies(A,B))
	remainingVariables = list(Variables)


	for i in range(0,len(Variables)) :
		nextVar = randint(0,len(remainingVariables)-1)

		# Randomly default to adding the variable or its negation
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
	T.add(C)
	if (T.check() == sat) :
		cCount += 1



print("Proportion was " + str(cCount) + "/" + str(numLoops))

