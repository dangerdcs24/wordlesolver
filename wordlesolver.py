import random
import math
import argparse
import os
import pickle

guessExpectation = {
	1: 1,
	2: 1.5,
	3: 1.75,
	4: 1.9375,
	5: 2.025,
	6: 2.25,
	7: 2.5,
	8: 2.5,
	9: 2.5,
	10: 2.5
}

# result is an array of length 5, where each element is an int: 0 means not in target (grey),
# 1 means in target wrong position (yellow), 2 means in target in correct position (green)

# Solves the wordle given a target word to guess
def solve_wordle(target, saveResults):
	currentDir = os.path.abspath(os.path.dirname(__file__))
	words = load_wordle_dictionary(currentDir + '/words.txt')
	# 12972 total words of length 5
	possibilities = load_wordle_dictionary(currentDir + '/possibilities.txt')
	# test_stuff()
	success = False
	guesses = []
	for round in range(0,6):
		bestGuess = compute_guess(words, possibilities, round, 'greedy')
		result = fetch_result(bestGuess, target)
		guesses.append(bestGuess)
		possibilities = reduce_possibilities(bestGuess, result, possibilities)
		print('guess: ' + bestGuess)
		print('result: ' + str(result))
		print('possibilities length: ' + str(len(possibilities)))
		print('possibilities: ' + str(possibilities))
		print('--------------------------------------------')
		if result == [2,2,2,2,2]:
			success = True
			break
	report_success(success, guesses)
	report_analytics(possibilities, target)
	if saveResults:
		results = load_results(currentDir)
		print('results before this word ---------------')
		print(results)
		if success:
			results[len(guesses)] = results[len(guesses)] + 1
		else:
			results['failures'] = results['failures'] + 1
		print('results after this word---------------')
		print(results)
		save_results(currentDir, results)


def load_results(currentDir):
    with open(currentDir + '/results.pkl', 'rb') as f:
        return pickle.load(f)


def save_results(currentDir, results):
	with open(currentDir + '/results.pkl', 'wb') as f:
		pickle.dump(results, f)


# load dictionary of words
def load_wordle_dictionary(filename):
	with open(filename) as file:
		words = file.readlines()
		words = [line.rstrip().lower() for line in words]
	words = [word for word in words if len(word) == 5]
	return words


# given a guess, a result in the format described above, and a list of remaining possibilities,
# this function returns a reduced list of possibilities given the new information acquired by
# the result from the guess
def reduce_possibilities(guess, result, possibilities):
	# GREY:
	# Hone in on total letter counts
	# The number of grey results can indicate how many of that letter are in the target.
	# Compare number of grey results to the number of times that letter is in the guess
	# if number of grey results > 0:
	# 	number of times letter is in guess - number of grey results = number of times letter is in target
	# else number of grey results == 0:
	# 	number of times letter is in target >= number of times letter is in guess
	for i in range(0,5):
		letterIndices = [idx for idx, char in enumerate(guess) if char == guess[i]]
		letterCnt = len(letterIndices)
		greyCnt = len([result[idx] for idx in letterIndices if result[idx] == 0])
		if greyCnt > 0:
			letterInTargetCnt = letterCnt - greyCnt
			possibilities = [possibility for possibility in possibilities \
				if possibility.count(guess[i]) == letterInTargetCnt]
		else:
			letterInTargetAtLeastCnt = letterCnt
			possibilities = [possibility for possibility in possibilities \
				if possibility.count(guess[i]) >= letterInTargetAtLeastCnt]
	
	# YELLOW:
	# Hone in on letter positioning
	# Letter is not in that position
	#
	# GREEN:
	# Hone in on letter positioning
	# Letter is in that position
	for i in range(0,5):
		if result[i] == 0:
			possibilities = [possibility for possibility in possibilities if possibility[i] != guess[i]]
		if result[i] == 1:
			possibilities = [possibility for possibility in possibilities if possibility[i] != guess[i]]
		elif result[i] == 2:
			possibilities = [possibility for possibility in possibilities if possibility[i] == guess[i]]

	return possibilities


# Computes a result given a guess and a target word, returns result in the results format described above
def fetch_result(guess, target):
	return compute_result(guess, target)


# Computes a result given a guess and a target word, returns result in the results format described above
def compute_result(guess, target):
	targetMatchIdxs = []
	result = [0,0,0,0,0]
	for i in range(0,5):
		if guess[i] == target[i]:
			result[i] = 2
			targetMatchIdxs.append(i)
	for i in range(0,5):
		if guess[i] != target[i]:
			targetIndices = [idx for idx, char in enumerate(target) if char == guess[i] and idx not in targetMatchIdxs]
			if len(targetIndices) > 0:
				targetMatchIdxs.append(targetIndices[0])
				result[i] = 1
			else:
				result[i] = 0
	return result


# Determines what word to guess next
# strategy is passed in: right now strategies are 'random' which chooses a random word, and 'greedy'
def compute_guess(words, possibilities, round, strategy):
	if len(possibilities) == 0:
		print('uh oh... we have reduced all possibilities and not guessed the word!!! Guessing abode as default')
		return 'abode'
	if strategy == 'random':
		randomIdx = random.randint(0, len(possibilities) - 1)
		print(len(possibilities))
		print(randomIdx)
		return possibilities[randomIdx]
	elif strategy == 'greedy':
		return compute_greedy_guess(words, possibilities, round)
	# elif strategy == 'recursive':
	# 	return compute_recursive_guess(words, possibilities, round)
	else:
		return 'abode'


# None of this is going to work
# def compute_recursive_guess(words, possibilities, round):
# 	for target in possibilities:
# 		compute_expected_guess_total(words, possibilities, target)


# def compute_expected_guess_total(words, possibilities, target):
# 	if len(possibilities) == 0:
# 		raise ValueError('GAAAAHHHHHH!!!!')
# 	# ------- base cases -------
# 	if len(possibilities) == 1:
# 		return 1
# 	if len(possibilities) == 2:
# 		return 1.5
# 	# -------- recursive cases ----------
# 	# select best word and best non-possible word that reduce the expected possibilities the most
# 	bestWord = None
# 	bestPossibleWord = None
# 	bestExpectedPossibilitesTotal = 10000000
# 	bestExpectedPossibilitiesAmongPossibleWords = 1000000
# 	for word in words:
# 		result = compute_result(word, target)
# 		possibilityCnt = len(reduce_possibilities(word, result, possibilities))
# 		if possibilityCnt < bestExpectedPossibilitesTotal:
# 			bestExpectedPossibilitesTotal = possibilityCnt
# 			bestWord = word
# 		if word in possibilities and possibilityCnt < bestExpectedPossibilitiesAmongPossibleWords: 
# 			bestExpectedPossibilitiesAmongPossibleWords = possibilityCnt
# 			bestPossibleWord = word
# 	# now recursively probe the tree with the best possible word and best total word as branches
# 	# for the tree at each step
# 	bestWordExpectedGuessTotal = 0
# 	bestPossibleWordExpectedGuessTotal = 0
# 	if bestWord == target:
# 		bestWordExpectedGuessTotal = 1
# 	else:
# 		result = compute_result(bestWord, target)
# 		bestWordPossibilities = reduce_possibilities(bestWord, result, possibilities)
# 		bestWordExpectedGuessTotal = 1 + compute_expected_guess_total(words, bestWordPossibilities, target)
# 	if bestWord == bestPossibleWord:
# 		bestPossibleWordExpectedGuessTotal = bestWordExpectedGuessTotal
# 	elif bestPossibleWord == target:
# 		bestPossibleWordExpectedGuessTotal = 1
# 	else:
# 		result = compute_result(bestPossibleWord, target)
# 		bestPossibleWordPossibilities = reduce_possibilities(bestPossibleWord, result, possibilities)
# 		bestPossibleWordExpectedGuessTotal = 1 + compute_expected_guess_total(words,
# 			bestPossibleWordPossibilities, target)
# 	if bestPossibleWordExpectedGuessTotal < bestWordExpectedGuessTotal:
# 		return bestPossibleWordExpectedGuessTotal
# 	else:
# 		return bestWordExpectedGuessTotal



# the greedy algorithm is an intelligent greedy algorithm that determines which word to guess
# by choosing to guess the word that is likely to create the largest reducrtion
# in the number of possibilities.
# when there is less than 10 possible words left, the greedy algorithm starts to consider guessing
# only possible words, but compares that against guessing the word that will result in the greatest
# reduction of possibilities. It attempts to guess which guess will result in the lowest number of
# guesses until the target word is found.
def compute_greedy_guess(words, possibilities, round):
	if round == 0:
		return 'roate'
	# base case
	if len(possibilities) <= 2:
		randomIdx = random.randint(0, len(possibilities) - 1)
		return possibilities[randomIdx]
	bestWord = None
	bestPossibleWord = None
	bestExpectedPossibilitesTotal = 10000000
	bestExpectedPossibilitiesAmongPossibleWords = 1000000
	for word in words:
		totalPossibilityCnt = 0
		for target in possibilities:
			result = compute_result(word, target)
			possibilityCnt = len(reduce_possibilities(word, result, possibilities))
			totalPossibilityCnt = totalPossibilityCnt + possibilityCnt
		expectedPossibilityCnt = totalPossibilityCnt / len(possibilities)
		if expectedPossibilityCnt < bestExpectedPossibilitesTotal:
			bestExpectedPossibilitesTotal = expectedPossibilityCnt
			bestWord = word
		if word in possibilities and expectedPossibilityCnt < bestExpectedPossibilitiesAmongPossibleWords: 
			bestExpectedPossibilitiesAmongPossibleWords = expectedPossibilityCnt
			bestPossibleWord = word
	if bestPossibleWord == bestWord:
		return bestPossibleWord
	else:
		print('best possible word dilemna!')
		print('best word: ' + bestWord)
		print('best expected possibilities: ' + str(bestExpectedPossibilitesTotal))
		print('best possible word: ' + bestPossibleWord)
		print('best expected possibilities for possible word: ' + str(bestExpectedPossibilitiesAmongPossibleWords))
		print('possibilities length: ' + str(len(possibilities)))
		print('possibilities: ' + str(possibilities))
		# if len(possibilites) > 10:
		if bestExpectedPossibilitiesAmongPossibleWords > 3.5:
			return bestWord
		if round == 5:
			# if this is the last round, gotta guess a possible word
			return bestPossibleWord
		expectedGuessesFromPossibleWord = 0
		expectedGuessesFromNotPossibleWord = 0
		for target in possibilities:
			bestWordResult = compute_result(bestWord, target)
			bestPossibleWordResult = compute_result(bestPossibleWord, target)
			bestWordPossibilities = reduce_possibilities(bestWord, bestWordResult, possibilities)
			bestPossibleWordPossibilities = reduce_possibilities(bestPossibleWord, bestPossibleWordResult, possibilities)
			if target == bestPossibleWord:
				expectedGuessesFromPossibleWord = expectedGuessesFromPossibleWord + 1
			else:
				expectedGuessesFromPossibleWord = expectedGuessesFromPossibleWord + \
					1 + expected_guesses_with_n_possibilities_left(len(bestPossibleWordPossibilities))
			expectedGuessesFromNotPossibleWord = expectedGuessesFromNotPossibleWord + \
				+ 1 + expected_guesses_with_n_possibilities_left(len(bestWordPossibilities))
		expectedGuessesFromPossibleWord = expectedGuessesFromPossibleWord / len(possibilities)
		expectedGuessesFromNotPossibleWord = expectedGuessesFromNotPossibleWord / len(possibilities)
		print('expected guesses from possible word: ' + str(expectedGuessesFromPossibleWord))
		print('expected guesses from not possible word: ' + str(expectedGuessesFromNotPossibleWord))
		if round == 4 and expectedGuessesFromPossibleWord == expectedGuessesFromNotPossibleWord \
			and expectedGuessesFromPossibleWord == 2:
			return bestWord
		elif expectedGuessesFromPossibleWord <= expectedGuessesFromNotPossibleWord:
			return bestPossibleWord
		else:
			return bestWord


def expected_guesses_with_n_possibilities_left(n):
	if n > 5:
		print('woah... calling expected guesses with n > 4, did not expect this to happen')
		print('n: ' + str(n))
	return guessExpectation[n]


def report_success(success, guesses):
	if success:
		print('SUCCESS!!!')
		print('guessed the wordle in ' + str(len(guesses)) + ' guesses!')
	else:
		print('FAILURE!!!')
		print('could not guess the wordle in 6 guesses  :(')
	print('guesses: ' + str(guesses))


def report_analytics(possibilities, target):
	print('possibilities length: ' + str(len(possibilities)))
	print('possibilities: ' + str(possibilities))
	print('target word: ' + target)


def test_stuff():
	# test variables
	target = "hello"
	testdict = ["aaaaa", "aaaab", "aaaba", "aaabb", "aabaa", "aabab", "aabba", "aabbb",
		"abaaa", "abaab", "ababa", "ababb", "abbaa", "abbab", "abbba", "abbbb",
		"baaaa", "baaab", "baaba", "baabb", "babaa", "babab", "babba", "babbb",
		"bbaaa", "bbaab", "bbaba", "bbabb", "bbbaa", "bbbab", "bbbba", "bbbbb",]
	print(len(possibilities))
	# test logic
	possibilities = reduce_possibilities("snoop", [0,1,2,0,0], possibilities)
	print(len(possibilities))
	print(possibilities)
	print(compute_result("agave", "laiev"))


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Solve a wordle')
	parser.add_argument('--targetWord', type=str,
        help='the target word that the program will try to guess')
	parser.add_argument('--saveResults', action="store_true")

	args = parser.parse_args()
	solve_wordle(args.targetWord, args.saveResults)
