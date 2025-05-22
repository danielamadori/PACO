import random

from model.etl import get_petri_net


def update_petri_net(bpmn, step:int):
	petri_net, petri_net_dot, execution_tree_petri_net, actual_execution_tree_petri_net = get_petri_net(bpmn, step)
	return petri_net, petri_net_dot, actual_execution_tree_petri_net



import random
import string

def random_label(length=3):
	return ''.join(random.choices(string.ascii_uppercase, k=length))

def random_distribution_dict(num_entries):
	keys = [random_label() for _ in range(num_entries)]
	values = [random.uniform(0.1, 1.0) for _ in keys]
	total = sum(values)
	return {k: round(v / total, 2) for k, v in zip(keys, values)}

def generate_pending_gateway(num_gateways=5):
	pending_gateway = {}
	for i in range(num_gateways):
		gateway_type = random.choice(["C", "N"])
		gateway_id = f"{gateway_type}{i+1}"
		num_choices = random.randint(2, 5)
		pending_gateway[gateway_id] = random_distribution_dict(num_choices)
	return pending_gateway


def simulate_execution(bpmn, step:int):
	#_, _, actual_execution_tree_petri_net = update_petri_net(bpmn, step)

	pending_gateway = generate_pending_gateway()

	probability = round(random.uniform(0.01, 0.99), 10)
	execution_time = random.randint(5, 30)

	impacts = {
		"Cost": round(random.uniform(5.0, 50.0), 1),
		"Time": round(random.uniform(10.0, 60.0), 1),
		"CO2": round(random.uniform(1.0, 10.0), 1)
	}

	expected_values = {
		"Cost": round(impacts["Cost"] * random.uniform(0.1, 0.5), 1),
		"Time": round(impacts["Time"] * random.uniform(0.1, 0.5), 1),
		"CO2": round(impacts["CO2"] * random.uniform(0.1, 0.9), 1)
	}

	return {
		"gateway_decisions": pending_gateway,
		"impacts": impacts,
		"expected_impacts": expected_values,
		"execution_time": execution_time,
		"probability": probability
	}



