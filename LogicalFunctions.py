from z3 import *
import collections
import csv
from random import randint, random, randrange
import time
import cProfile


# Runs the Demski algorithm for generating a logical prior
# @knowledgeBase	 : a list of z3 instances corresponding to the
#                     given axiom scheme
# @variables         : the list of z3 variables involved
# @statementOfInterest: the variable to generate a prior probability on
# @secondsToRun      : how much time to spend running the alg
# @return            : a list of lists, where each element
#                      of the larger list gives variables corresponding
#                      to a consistent model
def DemskiPrior(knowledgeBase, variables, statementOfInterest, secondsToRun) :

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
		remKeys            = variables.keys()


		for i in range(0,len(variables)) :
			nextKeyIndex = randrange(len(remKeys))
			nextKey      = remKeys[nextKeyIndex]
			nextVarlist  = variables[nextKey]
			nextVar      = nextVarlist[0]
			nextVarType  = nextVarlist[1]

			# Begin bool case
			if nextVarType == 'bool' :
				probability = nextVarlist[2]
				# Randomly add the variable or its negation
				if (random() < probability) :
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
			# End bool case

			# Begin uniform case
			if nextVarType == 'unif' :
				satisfied = False
				while not(satisfied) :
					varValue = randint(nextVarlist[2], nextVarlist[3])
					T.push()
					T.add(nextVar == varValue)
					if (T.check() == sat) :
						satisfied = True
					else :
						T.pop()

			remKeys.pop(nextKeyIndex)

		# Supports arbitrary statements but slower
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
	reservedNames = ['not', 'and', 'or', 'implies', 'xor', '=', '==',
					 'bool', 'Bool', 'boolean', 'Boolean',
					 'Unif', 'unif', 'uniform', 'Uniform']
	for variableString in variableNames :
		varDeclaration = variableString.split()

		# Either assign the default probability (.5) or that specified
		# defaults bool cases
		isBool = False
		if len(varDeclaration) == 1 :
			probability = .5
			variableName = variableString
			isBool = True
		elif len(varDeclaration) == 2 :
			probability = float(varDeclaration[1])
			variableName = varDeclaration[0]
			isBool = True

		# Explicit bool parsing cases
		if varDeclaration[0] in ['bool', 'Bool', 'boolean', 'Boolean'] :
			if len(varDeclaration) == 1 :
				sys.exit("insufficient arguments when declaring " + varDeclaration[0])
			if len(varDeclaration) == 2 :
				probability = .5
				variableName = varDeclaration[1]
			elif len(varDeclaration) == 3 :
				probability = float(varDeclaration[2])
				variableName = varDeclaration[1]
			isBool = True

		if isBool :
			z3Instance = Bool(variableName)
			argList = [probability]
			varType = 'bool'

		# Integer variable parsing cases
		if varDeclaration[0] in ['Unif', 'unif', 'uniform', 'Uniform'] :
			if len(varDeclaration) != 4 :
				sys.exit("""uniform variables are declared with the following form:
					        unif VarName 0 10
					        this error occurred when parsing""" + variableString)

			variableName = varDeclaration[1]
			lowerBound   = int(varDeclaration[2])
			upperBound   = int(varDeclaration[3])
			argList      = [lowerBound, upperBound]
			z3Instance   = Int(variableName)
			varType      = 'unif'


		if variableName.lower() in reservedNames :
			print("Error in parsing variable names")
			sys.exit(variableName + " is a reserved name")
			return()
		key = variableName
		variables[variableName] = [z3Instance, varType] + argList

	return(variables)



# Parses a single sentence of the knowledge base
# @words	 : a list of words in the sentence. Each word should be
#              either a variable, operator, or parens
# @wordIndex : which word in the list should be parsed next
# @variables : a list the z3 variables declared in the csv file
# @return    : a z3 instance. When called on the whole sentence with
#              wordIndex 0, the z3 instance will be the sentence's
parseResult = collections.namedtuple("ParseResult", ['nextIndex', 'Instance'])
def ParseKnowledgeSentence(words, wordIndex, variables, varNames) :

	while len(words) > wordIndex :
		word = words[wordIndex]
		#print(word)
		wordIndex += 1
		if word in varNames :
			lastInstance = variables[word][0]

		else :

			if (word == "not") or (word == "Not") :
				recResult = ParseKnowledgeSentence(words, wordIndex, variables, varNames)
				wordIndex = recResult.nextIndex
				result = parseResult(nextIndex = wordIndex, Instance = Not(recResult.Instance))
				return(result)
					


			elif word ==  "(" :
				recResult = ParseKnowledgeSentence(words, wordIndex, variables, varNames)
				wordIndex = recResult.nextIndex

				lastInstance = recResult.Instance

			elif word == ")" :
				result = parseResult(Instance = lastInstance, nextIndex = wordIndex)
				return(result)

			elif word in ["implies", "Implies", "->"] :
				recResult = ParseKnowledgeSentence(words, wordIndex, variables, varNames)
				result = parseResult(nextIndex = recResult.nextIndex, Instance = Implies(lastInstance, recResult.Instance))
				return(result)
			elif word in ["and", "And", "&"] :
				recResult = ParseKnowledgeSentence(words, wordIndex, variables, varNames)
				result = parseResult(nextIndex = recResult.nextIndex, Instance = And(lastInstance, recResult.Instance))
				return(result)			
			elif word in ["or", "Or", "||"] :
				recResult = ParseKnowledgeSentence(words, wordIndex, variables, varNames)
				result = parseResult(nextIndex = recResult.nextIndex, Instance = Or(lastInstance, recResult.Instance))
				return(result)
			elif word in ["Xor", "xor"] :
				recResult = ParseKnowledgeSentence(words, wordIndex, variables, varNames)
				result = parseResult(nextIndex = recResult.nextIndex, Instance = Xor(lastInstance, recResult.Instance))
				return(result)
			elif word in ["=", "==", "iff"] :
				recResult = ParseKnowledgeSentence(words, wordIndex, variables, varNames)
				nextInstance = (lastInstance == recResult.Instance)
				result = parseResult(nextIndex = recResult.nextIndex, Instance = nextInstance)
				return(result)
			elif word in ["!=", "<>"] :
				recResult = ParseKnowledgeSentence(words, wordIndex, variables, varNames)
				nextInstance = (lastInstance != recResult.Instance)
				result = parseResult(nextIndex = recResult.nextIndex, Instance = nextInstance)
				return(result)	
			elif word == ">" :
				recResult = ParseKnowledgeSentence(words, wordIndex, variables, varNames)
				result = parseResult(nextIndex = recResult.nextIndex, Instance = (lastInstance > recResult.Instance))
				return(result)
			elif word == "<" :
				recResult = ParseKnowledgeSentence(words, wordIndex, variables, varNames)
				result = parseResult(nextIndex = recResult.nextIndex, Instance = (lastInstance < recResult.Instance))
				return(result)
			elif word == ">=" :
				recResult = ParseKnowledgeSentence(words, wordIndex, variables, varNames)
				result = parseResult(nextIndex = recResult.nextIndex, Instance = (lastInstance >= recResult.Instance))
				return(result)
			elif word == "<=" :
				recResult = ParseKnowledgeSentence(words, wordIndex, variables, varNames)
				result = parseResult(nextIndex = recResult.nextIndex, Instance = (lastInstance <= recResult.Instance))
				return(result)
			elif RepresentsInt(word) :
				lastInstance = int(word)
			else :
				print("Error parsing background knowledge ")
				sys.exit(word + " is neither variable nor operator")
				return()

	result = parseResult(Instance = lastInstance, nextIndex = 0)
	return(result)


# Wrapper for ParseKnowledgeSentence
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
	variableNames = variables.keys()
	result = ParseKnowledgeSentence(spacedSentence.split(), 0, variables, variableNames)
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


	variables = ParseVariables(variableRow)

	sentences = rows.next()
	backgroundKnowledge = []
	for sentence in sentences :
		if sentence == '' :
			pass
		else :
			backgroundKnowledge.append(ParseSentence(sentence,variables))

	statementOfInterest = ParseSentence(rows.next(),variables)
	relevantVars = transClosure(backgroundKnowledge, statementOfInterest)
	if (len(relevantVars) < len(variables)) :
		print("Warning: not all variables declared are in the transitive closure with the sentence of interest")

	result = DemskiPrior(backgroundKnowledge, variables, statementOfInterest, secondsToRun)
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

# Returns true if s can be coerced to an integer
def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False


# Wrapper to let Z3 instances to be used in python hash tables
class AstRefKey:
    def __init__(self, n):
        self.n = n
    def __hash__(self):
        return self.n.hash()
    def __eq__(self, other):
        return self.n.eq(other.n)
    def __repr__(self):
        return str(self.n)

def askey(n):
    assert isinstance(n, AstRef)
    return AstRefKey(n)

def get_vars(f):
    r = set()
    def collect(f):
      if is_const(f): 
          if f.decl().kind() == Z3_OP_UNINTERPRETED and not askey(f) in r:
              r.add(askey(f))
      else:
          for c in f.children():
              collect(c)
    collect(f)
    return r

# Find the transitive closure of variables which are logically
# connected to the sentence of interest
def transClosure(backgroundKnowledge, SOI) :

	connectedVars = set(get_vars(SOI))
	newConnections = True
	while newConnections :
		newConnections = False
		for sentence in backgroundKnowledge :

			# Add variables in sentences connected to variables
			# already in our set, but only there are new vars to add.
			sentenceSet = set(get_vars(sentence))
			if (connectedVars & sentenceSet) :
				if (connectedVars.issuperset(sentenceSet)) :
					pass
				else :
					connectedVars = connectedVars.union(sentenceSet)
					newConnections = True

	return(connectedVars)






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