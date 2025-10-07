import random


def sample_expected_impact(root_dict, track_choices=False):

	def merge_impacts(impact1, impact2):
		return [a + b for a, b in zip(impact1, impact2)]

	def scale_impacts(impacts, scale):
		return [scale*impact for impact in impacts]

	choices_made = {}

	def process_node(node):
		# Base case: if node is a task, return its impacts (or empty dict if none)
		if node["type"] == "Task":
			return node['impact']

		# Recursive cases based on node type
		if node["type"] == "sequential":
			head_impacts = process_node(node["sx_child"])
			tail_impacts = process_node(node["dx_child"])
			return merge_impacts(head_impacts, tail_impacts)

		elif node["type"] == "parallel":
			first_impacts = process_node(node["sx_child"])
			second_impacts = process_node(node["dx_child"])
			return merge_impacts(first_impacts, second_impacts)

		elif node["type"] == "choice":
			# Randomly choose between true and false branches
			is_true = random.choice([True, False])
			chosen_branch = node["sx_child"] if is_true else node["dx_child"]

			# Record the choice if tracking is enabled
			if track_choices:
				choices_made[f"choice{node['id']}"] = is_true

			return process_node(chosen_branch)

		elif node["type"] == "nature":
			# Calculate probability-weighted impacts for both branches
			true_impacts = scale_impacts(
				process_node(node["sx_child"]),
				node["probability"]
			)
			false_impacts = scale_impacts(
				process_node(node["dx_child"]),
				1 - node["probability"]
			)
			return merge_impacts(true_impacts, false_impacts)

		raise ValueError(f"Unknown node type: {node['type']}")

	impacts = process_node(root_dict)

	if track_choices:
		return impacts, choices_made
	return impacts