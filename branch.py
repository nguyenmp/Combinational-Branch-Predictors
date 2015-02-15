#!/usr/bin/python
import sys

class global_predictor():
    def __init__(self, history_bits, counter_bits):
        self.global_history = 0
        self.history_bits = history_bits
        self.counter_bits = counter_bits
        self.counters = [2 ** (self.counter_bits - 1)] * (2 ** self.history_bits)

    def get_prediction(self, pc):
        index = self.global_history ^ ((pc >> 2) & (2 ** self.history_bits - 1))
        counter = self.counters[index]
        return counter >> (self.counter_bits - 1)

    def update(self, pc, branch_outcome):
        index = self.global_history ^ ((pc >> 2) & (2 ** self.history_bits - 1))
        
        # Update the counter
        counter = self.counters[index]
        counter += 1 if branch_outcome == 1 else -1
        if counter < 0:
            counter = 0;
        elif counter >= 2 ** self.counter_bits:
            counter = 2 ** self.counter_bits - 1
        self.counters[index] = counter;

        # Update global history
        self.global_history = (self.global_history << 1 | branch_outcome) & (2 ** (self.history_bits) - 1)


class local_predictor():
    def __init__(self, num_entries, history_bits, counter_bits):
        self.num_entries = num_entries
        self.history_bits = history_bits
        self.counter_bits = counter_bits
        self.histories = [0] * self.num_entries
        self.counters = [2 ** (self.counter_bits - 1)] * (2 ** self.history_bits)

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


class tournament_predictor():
    def __init__(self, num_entries, counter_bits):
        self.global_history = 0 
        self.num_entries = num_entries
        self.counter_bits = counter_bits
        self.counters = [2 ** (self.counter_bits - 1)] * (num_entries)
        self.g_predictor = global_predictor(12, 2)
        self.l_predictor = local_predictor(1024, 8, 2)

    def get_prediction(self, pc):
        counter = self.counters[self.global_history]
        if counter >> (self.counter_bits - 1) == 1:
            return self.g_predictor.get_prediction(pc)
        else:
            return self.l_predictor.get_prediction(pc)

    def update(self, pc, branch_outcome):
        g_prediction = self.g_predictor.get_prediction(pc)
        pgc = 1 if branch_outcome == g_prediction else 0

        l_prediction = self.l_predictor.get_prediction(pc)
        plc = 1 if branch_outcome == l_prediction else 0

        counter = self.counters[self.global_history]
        counter += (pgc - plc)
        if counter < 0:
            counter = 0;
        elif counter >= 2 ** self.counter_bits:
            counter = 2 ** self.counter_bits - 1 
        self.counters[self.global_history] = counter

        self.global_history = (self.global_history << 1 | branch_outcome) % self.num_entries
    
        self.g_predictor.update(pc, branch_outcome)
        self.l_predictor.update(pc, branch_outcome)


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

def main(which):
    if which == 0:
        predictor = tournament_predictor(1024, 2)
    elif which == 1:
        predictor = global_predictor(12, 2)
    elif which == 2:
        predictor = local_predictor(1024, 8, 2)
    else:
        predictor = singlebit_bimodal_predictor(1024);

    correct_predictions = 0
    total_predictions = 0
    _ = sys.stdin.readline()  # throw away first line

    hist = {}

    for line in sys.stdin:
        # get the two feilds and convert them to integers
        [pc, branch_outcome] = [int(x,0) for x in line.split()]
        this_prediction = predictor.get_prediction(pc)
        total_predictions += 1
        if this_prediction == branch_outcome:
            correct_predictions += 1
        else:
            hist[str(pc)] = 1 if str(pc) not in hist else hist[str(pc)] + 1
        predictor.update( pc, branch_outcome );
    # print out the statistics
    max_item = reduce(lambda x, y: x if x[1] > y[1] else y, hist.items())
    print "pc: " + format(int(max_item[0]), '#08x') + " misses: " + str(max_item[1])
    print predictor.__class__.__name__, 100*correct_predictions / float(total_predictions)

if __name__ == "__main__":
   main(int(sys.argv[1]))
