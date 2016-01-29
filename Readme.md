# Priors for Logical Sentences #

## Usage ##
The [z3 python package](https://github.com/Z3Prover/z3) must be installed and on the path for the code to run.

Currently, this project contains an implementation of [Demski's algorithm](agi-conference.org/2012/wp-content/uploads/2012/12/paper_70.pdf) for the approximation of logical priors. Given a properly formatted input, ParseInputFile will run the approximation algorithm for a specified length of time and print a proportion corresponding the prior probability for the sentence of interest.

An input file can be described with the following grammar:

- File = VariableLine \n KnowledgeLine \n S \n KnowledgeLine
- VariableLine = V [P] {,V [P]}
- V = 'letter' {'non-parens or comma Unicode character'}
- P = [0].DN
- D = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
- N = DN | D
- KnowledgeLine = [S {,S}]
- S = DeclaredV | S BinOp S | Not S
- DeclaredV = 'a V which occurred in VariableLine'
- BinOp = and | or | implies | xor | iff | == 

Or in other words, the first line of the file declares the binary variables which will be used, the second line declares the logical sentences which are known to be true (note that this set must be consistent), and the third line declares the sentence for which a probability is desired. The fourth line declares new knowledge which should be updated on after the prior has been generated.

The P which follows each variable declared in the first line describes the naive prior probability assigned to the truth of that variable. If left blank, it is set to .5 by default.

The S located by itself on the third line is the sentence of interest which will have a probability calculated by the algorithm and printed.

### Monty Hall Example ###
To help illustrate how the program works, we will use it on the familiar Monty Hall logic problem. This is generally described as follows:

You are on a gameshow. There are 3 doors. Behind 2 doors is a goat, and the remaining door has a car behind it. You want to win the car. You are first allowed to pick one door. The host then reveals one of the two doors which you did not pick (and always reveals a goat). You are then given the option to switch from the door you first chose to the remaining door. Should you do so?

To translate that into logical sentences we will have 10 variables. These will be car1, car2, car3 (corresponding to which door the car is behind), pick1, pick2, pick3 (which door is chosen), reveal1, reveal2, and reveal3 (which door is revealed). The last variable will be explained later.

The problem tells us that exactly one door contains the car so: (car1 xor (car2 or car3)) and (not(car2 and car3)).

Exactly one door is picked: (pick1 xor (pick2 or pick3)) and (not(pick2 and pick3)).

Exactly one door is revealed: (reveal1 xor (reveal2 or reveal3)) and (not(reveal2 and reveal3)).

If a door is picked or contains the car, then it is not revealed: (pick1 or car1) implies not reveal1.

Given these inputs (ExampleInput1.csv), the Demski algorithm assigns approximately a 36% probability to the door you originally choose containing the car. This is quite close to the 1/3 probability which is typically cited as the solution. The use of a prior probability is reasonable here, as the host's behavior could significantly modify the probability that the car was behind a given door.

As an example of this, imagine the host reveals door 2 whenever they can. This corresponds to the logical statement '(not (pick2 or car2)) implies reveal2'. You pick door 1 and the host reveals door 2. What is the probability that the car is behind door 1? ExampleInput2.csv corresponds to this situation and when run assigns ~50% probability to the car being behind door 1. To understand if this is reasonable, note that if the host revealed door 3 then the probability the car was behind door 1 would be 0%.

## To-Dos ##

- Allow multiple variables to have their probability calculated simultaneously
- Allow for questions of conditional probabilities
- Flesh out Monty Hall problem with examples of different known host behavior (ideally requires above get done)
- Time-outs
	- Shortcut loops when possible
	- User controlled preferences for how to spend time
	- Optimize time on most productive branches
- Weighted sampling for very low prior probabilities
- User specified order of variable determination?
- Real and integer variables
	- Allow user to specify prior distribution of variable
	- Allow for quantifier variables (to be used in 'for all X' type statements)
- Figure out how to do learning/updating
	- Option 1: keep track of all consistent models in a list. Conditioning acts by selecting only those models in the list where the evidence is true. Problems: requires storing a bunch of models and the number of models will probably rapidly go to zero (necessitating rerunning the original algorithm) so this wouldn't change the big O runtime.
	- Option 2: rerun the algorithm every time new information is received. Problems: super slow and not really how a 'prior' is supposed to function.
	- Option 3: something clever. Problems: requires thinking of something clever.
- Hutter algorithm
	- Better understand the algorithm
	- Figure out if it could be approximated
- Tree structure optimizations
- Add test file to check that priors are within bounds
- Add explicit grammars for input/output