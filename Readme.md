# Priors for Logical Sentences #

## Usage ##
The z3 python package must be installed and on the path for the code to run.


The input to ParseInputFile should be in the form of a comma separated value sheet. The lines should be organized as follows:

1. Declaration of variables. Variables are case sensitive and can contain alphanumeric characters, numbers, and special characters other than (, ), or comma. Variables may not contain spaces. Reserved and disallowed words are: 'not', 'and', 'or', 'implies', 'xor', 'iff', '=', and '=='. You can add a number strictly between 0 and 1 after a variable to specify the meta-prior probability on the variable.
2. Declaration of background knowledge. Each item should be a logical sentence only involving the declared variable names.
3. The sentence of interest. AKA, the sentence which should have a prior probability calculated.
4. (To-Do) the sentence to condition on.

### Monty Hall Example ###
To help illustrate how the program works, we will use it on the familiar Monty Hall logic problem. This is generally described as follows:

You are on a gameshow. There are 3 doors. Behind 2 doors is a goat, and the remaining door has a car behind it. You want to win the car. You are first allowed to pick one door. The host then reveals one of the two doors which you did not pick (and always reveals a goat). You are then given the option to switch from the door you first chose to the remaining door. Should you do so?

To translate that into logical sentences we will have 10 variables. These will be car1, car2, car3 (corresponding to which door the car is behind), pick1, pick2, pick3 (which door is chosen), reveal1, reveal2, and reveal3 (which door is revealed). The last variable will be explained later.

The problem tells us that exactly one door contains the car so: (car1 xor (car2 or car3)) and (not(car2 and car3)).

Exactly one door is picked: (pick1 xor (pick2 or pick3)) and (not(pick2 and pick3)).

Exactly one door is revealed: (reveal1 xor (reveal2 or reveal3)) and (not(reveal2 and reveal3)).

If a door is picked or contains the car, then it is not revealed: (pick1 or car1) implies not reveal1.

Given these inputs (ExampleInput1.csv), the Demski algorithm assigns approximately a 36% probability to the door you originally choose containing the car. This is quite close to the 1/3 probability which is typically cited as the solution. The use of a prior probability is reasonable here, as the host's behavior could significantly modify the probability that the car was behind a given door.

As an example of this, imagine the host reveals door 2 whenever they can. You pick door 1 and the host reveals door 2. What is the probability that the car is behind door 1? ExampleInput2.csv corresponds to this situation and when run assigns ~50% probability to the car being behind door 1. To understand if this is reasonable, note that if the host revealed door 3 then the probability the car was behind door 1 would be 0%.

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