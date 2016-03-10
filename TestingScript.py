# Dan Weinand
# Senior Project 
# 2/12/16

# Script for testing the functionality of the logical prior
# generation algorithms.

import csv
import LogicalFunctions as LF
import time

# Set-up output file writer
outputFileName = 'TestResults/' + time.strftime('%m%d%H%S', time.gmtime()) + '.csv'
with open(outputFileName, 'wb') as outputFile:

	resWriter = csv.writer(outputFile, delimiter=' ')

    # Loop through all example files
	initialLowerBounds  = [0,   .33, .43, .46, .25, .4, 0, 0]
	initialUpperBounds  = [1.1, .47, .57, .54, .35, .6, .1, 1]
	numModelsLowerBound = [0,   260, 260, 440, 260, 100, 50, 50]
	for k in range(0,8) :
		exampleFile = 'ExampleInput' + str(k) + '.csv'
		result = LF.ParseInputFile(exampleFile, 10)
		consistentPaths  = result[0]
		numModels = result[1]
		initialSOICount  = result[2]
		updatedSOICount  = result[3]

		numUpdatedModels = len(consistentPaths)
		probability = round(float(initialSOICount)/numModels,4)
		updatedProbability = round(float(initialSOICount)/numModels,4)

		if (probability > initialUpperBounds[k]) :
			print(exampleFile + "'s result was too high")
		elif (probability < initialLowerBounds[k]) :
			print(exampleFile + "'s result was too low")

		if (numModels < numModelsLowerBound[k]) :
			print(exampleFile + "'s generated fewer models than typical")
			print("Generated: " + str(numModels) + " models")
			print("Typical is: " + str(numModelsLowerBound[k]) + "+ models")

		resWriter.writerow([exampleFile,
			str(numModels), str(probability),
			str(numUpdatedModels), str(updatedProbability)])

	print('Testing done')
