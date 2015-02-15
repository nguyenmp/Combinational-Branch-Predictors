#!/usr/bin/python
import sys

class local_predictor():
    def __init__(self, num_entries, history_bits, counter_bits):
        self.num_entries = num_entries
        self.history_bits = history_bits
        self.counter_bits = counter_bits
        self.histories = [0] * self.num_entries
        self.counters = [2 ** (self.counter_bits) - 1] * (2 ** self.history_bits)

    def get_prediction(self, pc):
        index = (pc >> 2) % self.num_entries
        history = self.histories[index]
        counter = self.counters[history]
        return counter >> (self.counter_bits - 1)

    def update(self, pc, branch_outcome):
        index = (pc >> 2) % self.num_entries
        history = self.histories[index]
        counter = self.counters[history]
        counter += 1 if branch_outcome == 1 else -1
        if counter < 0:
            counter = 0;
        elif counter >= 2 ** self.counter_bits:
            counter = 2 ** self.counter_bits - 1
        self.counters[history] = counter;

        history = (history << 1 | branch_outcome) & (2 ** (self.history_bits) - 1)
        self.histories[index] = history

class singlebit_bimodal_predictor():
    def __init__(self, num_entries):
	self.num_entries = num_entries
	self.bimod_table = [0]*self.num_entries

    def get_prediction(self, pc):
	index = (pc>>2) % self.num_entries
	return self.bimod_table[index]

    def update(self, pc, branch_outcome):
	index = (pc>>2) % self.num_entries
	self.bimod_table[index] = branch_outcome


def main():
    predictor = local_predictor(1024, 8, 2)
    #predictor = singlebit_bimodal_predictor(1024);
    correct_predictions = 0
    total_predictions = 0
    _ = sys.stdin.readline()  # throw away first line
    for line in sys.stdin:
	# get the two feilds and convert them to integers
	[pc, branch_outcome] = [int(x,0) for x in line.split()]
	this_prediction = predictor.get_prediction(pc)
	total_predictions += 1
	if this_prediction == branch_outcome:
	    correct_predictions += 1
	predictor.update( pc, branch_outcome );
    # print out the statistics
    print predictor.__class__.__name__, 100*correct_predictions / float(total_predictions)

if __name__ == "__main__":
   main()
