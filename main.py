from utils import make_random_task, visualize
from solver import solve_qubo
from qubo import make_qubo, decode_result

times, deadlines, profits = make_random_task(num_jobs = 4, max_time = 5)
Q = make_qubo(times, deadlines, profits)
spins, energy = solve_qubo(Q, engine = "pulp")
results, score = decode_result(times, deadlines, profits, spins)
print("Total score is %d" % score)
visualize(results, save = "schedule.png")
