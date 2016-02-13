from z3 import *
import collections
import csv
from random import randint, random
import time
import cProfile


# Runs the Demski algorithm for generating a logical prior
# @knowledgeBase	 : a list of z3 instances corresponding to the
#                     given axiom scheme
# @variables         : the list of z3 variables involved
# @probabilities     : list of meta-priors on the variables
# @statementOfInterest: the variable to generate a prior probability on
# @secondsToRun      : how much time to spend running the alg
# @return            : a list of lists, where each element
#                      of the larger list gives variables corresponding
#                      to a consistent model
def DemskiPrior(knowledgeBase, variables, probabilities, statementOfInterest, secondsToRun) :

	consistentPaths = list()
	stopTime = time.time() + secondsToRun
	numLoops = 0
	# Check if knowledge base is consistent
	T = Solver()
	for sentence in knowledgeBase :
		T.add(sentence)
	if (T.check() == unsat) :
		sys.exit("Background knowledge not consistent")

	# Demski prior generation algorithm
	###################################

	interestCount = 0
	while time.time() < stopTime :
		numLoops += 1
		thisPath = list()


		#Add the original knowledge base
		T.reset()
		for sentence in knowledgeBase :
			T.add(sentence)
		remainingVariables = list(variables)
		remainingProbabilities = list(probabilities)


		for i in range(0,len(variables)) :
			nextVarIndex = randint(0,len(remainingVariables)-1)
			nextVar = remainingVariables[nextVarIndex]
			# Randomly add the variable or its negation
			if (random() < remainingProbabilities[nextVarIndex]) :
				T.push()
				T.add(nextVar)

				if (T.check() == unsat) :
					T.pop()
					T.add(Not(nextVar))
					thisPath.append(Not(nextVar))
				else :
					thisPath.append(nextVar)

			else :
				T.push()
				T.add(Not(nextVar))

				if (T.check() == unsat) :
					T.pop()
					T.add(nextVar)
					thisPath.append(nextVar)
				else :
					thisPath.append(Not(nextVar))
			

			remainingVariables.pop(nextVarIndex)
			remainingProbabilities.pop(nextVarIndex)
		T.add(statementOfInterest)
		if (T.check() == sat) :
			interestCount += 1

		consistentPaths.append(thisPath)


	# Old-test for functionality
	#print("" + str(round(float(interestCount)/numLoops,4)))
	return((consistentPaths,interestCount))

# Given a list of consistent model paths from a prior algorithm,
# and a sentence to compute the probability on along with some new knowledge,
# outputs the updated probability of the sentence being true.
# @consistentPaths       : a list of lists of z3 variables or their negations
# @sentenceOfInterest    : a z3 sentence
# @newKnowledgeSentences : a list of z3 sentences
# @returns               : a list of lists of z3 variables or their negations 
def consumptiveUpdate(consistentPaths, sentenceOfInterest, newKnowledgeBase) :

	stillConsistentPaths = []
	# Number of models consistent with the sentence of interest
	SOIcount = 0

	T = Solver()
	for sentence in newKnowledgeBase :
		T.add(sentence)
	if (T.check() == unsat) :
		sys.exit("Background knowledge not consistent on updating")

	# Recheck the consistency of all paths based on new knowledge
	for path in consistentPaths :
		T.reset()
		for sentence in newKnowledgeBase :
			T.add(sentence)
		for var in path :
			T.add(var)

		# Only keep consistent models
		if (T.check() == sat) :
			stillConsistentPaths.append(path)

			T.push()
			T.add(sentenceOfInterest)
			if (T.check() == sat) :
				SOIcount = SOIcount + 1

	# Old code for testing correctness
	#print("Probability true on updating was: " + str(float(SOIcount)/len(stillConsistentPaths)))


	return((stillConsistentPaths,SOIcount))


# Parses variable names into z3 variables
# @variableNames : a list of strings, each of which is the name
#                  for a variable
# @return        : two dictionaries with keys the variable strings and
#                  values as z3 boolean variables/corresponding meta-
#                  prior probabilities (respectively)
def ParseVariables(variableNames) :
	variables = {}
	probabilities = {}
	reservedNames = ['not', 'and', 'or', 'implies', 'xor', '=', '==']
	for variableString in variableNames :
		nameAndProb = variableString.split()
		# Either assign the default probability (.5) or that specified
		if len(nameAndProb) == 1 :
			probability = .5
			variableName = variableString
		else :
			probability = float(nameAndProb[1])
			variableName = nameAndProb[0]


		if variableName.lower() in reservedNames :
			print("Error in parsing variable names")
			sys.exit(variableName + " is a reserved name")
			return()
		key = variableName
		z3Instance = Bool(variableName)
		variables[variableName] = z3Instance
		probabilities[variableName] = probability

	return((variables,probabilities))




# Parses a single sentence of the knowledge base
# @words	 : a list of words in the sentence. Each word should be
#              either a variable, operator, or parens
# @wordIndex : which word in the list should be parsed next
# @variables : a list the z3 variables declared in the csv file
# @return    : a z3 instance. When called on the whole sentence with
#              wordIndex 0, the z3 instance will be the sentence's
parseResult = collections.namedtuple("ParseResult", ['nextIndex', 'Instance'])
def ParseKnowledgeSentence(words, wordIndex, variables) :

	while len(words) > wordIndex :
		word = words[wordIndex]
		#print(word)
		wordIndex += 1
		if word in variables :
			lastInstance = variables[word]

		else :

			if (word == "not") or (word == "Not") :
				recResult = ParseKnowledgeSentence(words, wordIndex, variables)
				wordIndex = recResult.nextIndex
				result = parseResult(nextIndex = wordIndex, Instance = Not(recResult.Instance))
				return(result)
					


			elif word ==  "(" :
				recResult = ParseKnowledgeSentence(words, wordIndex, variables)
				wordIndex = recResult.nextIndex

				lastInstance = recResult.Instance

			elif word == ")" :
				result = parseResult(Instance = lastInstance, nextIndex = wordIndex)
				return(result)

			elif word == "implies" or word == "Implies" :
				recResult = ParseKnowledgeSentence(words, wordIndex, variables)
				result = parseResult(nextIndex = recResult.nextIndex, Instance = Implies(lastInstance, recResult.Instance))
				return(result)
			elif word == "and" or word == "And" :
				recResult = ParseKnowledgeSentence(words, wordIndex, variables)
				result = parseResult(nextIndex = recResult.nextIndex, Instance = And(lastInstance, recResult.Instance))
				return(result)			
			elif word == "or" or word == "Or" :
				recResult = ParseKnowledgeSentence(words, wordIndex, variables)
				result = parseResult(nextIndex = recResult.nextIndex, Instance = Or(lastInstance, recResult.Instance))
				return(result)
			elif word == "Xor" or word == "xor" :
				recResult = ParseKnowledgeSentence(words, wordIndex, variables)
				result = parseResult(nextIndex = recResult.nextIndex, Instance = Xor(lastInstance, recResult.Instance))
				return(result)
			elif word == "=" or word == "=="  or word == 'iff' :
				recResult = ParseKnowledgeSentence(words, wordIndex, variables)
				nextInstance = And(Implies(lastInstance, recResult.Instance),Implies(recResult.Instance,lastInstance))
				result = parseResult(nextIndex = recResult.nextIndex, Instance = nextInstance)
				return(result)				
			else :
				print("Error parsing background knowledge ")
				sys.exit(word + " is neither variable nor operator")
				return()

	result = parseResult(Instance = lastInstance, nextIndex = 0)
	return(result)

# Wrapper for the function above
def ParseSentence(sentence, variables) :
	sentenceIndex = 0
	spacedSentence = ''
	#Pad the parentheses with spaces for easier parsing
	for char in sentence :

		if char == '(' or char == ')' :
			spacedSentence = spacedSentence + ' ' + char + ' '
		else :
			spacedSentence = spacedSentence + char

		sentenceIndex += 1
	result = ParseKnowledgeSentence(spacedSentence.split(), 0, variables)
	return(result.Instance)

# Parse the csv file and print the prior probability using Demski's alg
# @csvFileName  : a string specifying the variables, background knowledge
#                 and statement(s) of interest
# @secondsToRun : how many seconds to run Demski's algorithm for.
#				  The time taken to pre-process the file is not
#				  included
# @return       : A triple of the consistent models, the number of times
#                 the sentence of interest was true in these models,
#                 and the number of times it was true after updating.
def ParseInputFile(csvFileName, secondsToRun) :
	csvFile = open(csvFileName, 'rb')
	rows = csv.reader(csvFile, delimiter=',')
	variableRow = rows.next()

	# TO-DO figure out a way to do this without going from a dictionary
	#       to a set of lists
	varTuple = ParseVariables(variableRow)
	variables = varTuple[0]
	probabilities = varTuple[1]

	sentences = rows.next()
	backgroundKnowledge = []
	for sentence in sentences :
		if sentence == '' :
			pass
		else :
			backgroundKnowledge.append(ParseSentence(sentence,variables))

	variableList = []
	probabilityList = []
	for variableName in variables.keys() :
		variableList.append(variables[variableName])
		probabilityList.append(probabilities[variableName])
	# End relevant TO-DO section

	statementOfInterest = ParseSentence(rows.next(),variables)
	result = DemskiPrior(backgroundKnowledge, variableList, probabilityList, statementOfInterest, secondsToRun)
	consistentPaths = result[0]
	initialSOICount = result[1]
	numInitialModels = len(consistentPaths)

	# TO-DO add separate method for updating that way
	# it can be done in response to new info.
	updatedKnowledgeSentences = next(rows, None)
	if updatedKnowledgeSentences :
		updatedKnowledge = backgroundKnowledge
		for sentence in updatedKnowledgeSentences :
			if sentence == '' :
				pass
			else :
				updatedKnowledge.append(ParseSentence(sentence,variables))
		result = consumptiveUpdate(consistentPaths, statementOfInterest, updatedKnowledge)
		consistentPaths = result[0]
		updatedSOICount = result[1]
	else :
		updatedSOICount = initialSOICount
	return((consistentPaths, numInitialModels, 
		initialSOICount, updatedSOICount))




# Tests for functionality
#variableNs = ['A', "asdf'ldkj", "oRd", "A12", "B'"]

#result1 = ParseVariables(variableNs)
#print(type(result1['A']))
#print("Above should be type instance")

#result2 = ParseSentence("  (B' implies A )or( (not ( not ( not ( A ) ) ) ) and B' )", result1)
#print(result2)
#result3 = ParseSentence("(A or B') implies not oRd", result1)
#print(result3)

"""
# Monty hall
print('Given random host behavior and we picked door 1:')
print('The door is behind door 1 with probability below')
ParseInputFile('ExampleInput1.csv', 30)
#cProfile.run("ParseInputFile('ExampleInput1.csv', 30)")

#print('')

# First Monty hall variant
print('Given the host tries to reveal door 2, he does this time, and we picked door 1:')
print('The door is behind door 1 with the probability given below:')
ParseInputFile('ExampleInput2.csv', 30)

# Showcase meta-priors
#ParseInputFile('ExampleInput3.csv', 2)

print('') 

# Third Monty hall variant, shows updating
print('Given the host tries to reveal door2, he has yet to reveal, and we picked door1')
print('the door is behind door 1 with the probability given on first line:')
print('Updating based on host revealing door 2 given on second line')
ParseInputFile('ExampleInput4.csv', 15)
"""