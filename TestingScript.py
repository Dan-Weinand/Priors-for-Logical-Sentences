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
	for k in range(1,5) :
		exampleFile = 'ExampleInput' + str(k) + '.csv'
		result = LF.ParseInputFile(exampleFile, 10)
		consistentPaths  = result[0]
		numModels = result[1]
		initialSOICount  = result[2]
		updatedSOICount  = result[3]

		numUpdatedModels = len(consistentPaths)
		probability = round(float(initialSOICount)/numModels,4)
		updatedProbability = round(float(initialSOICount)/numModels,4)

		resWriter.writerow([exampleFile,
			str(numModels), str(probability),
			str(numUpdatedModels), str(updatedProbability)])

	print('Testing done')
