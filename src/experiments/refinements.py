from paco.solver import paco
import numpy as np

def refine_bounds(bpmn, initial_bounds, num_refinements = 10):
	parse_tree = None
	execution_tree = None
	pending_choices = None
	pending_natures = None

	total_results = []

	intervals = [ [0.0, bound_value] for bound_value in initial_bounds ]
	# Perform refinements
	for iteration in range(num_refinements):
		for current_impact in range(len(intervals)):
			print("Intervals: ", intervals)
			test_bounds = []
			for i in range(len(intervals)):
				test_bounds.append(intervals[i][1])

			#Ask professor
			#test_bounds[current_impact] = (intervals[current_impact][0] + intervals[current_impact][1]) / 2
			print("test_bounds: ", test_bounds)

			# Test these bounds
			text_result, result, times = paco(bpmn, np.array(test_bounds), parse_tree=parse_tree, pending_choices=pending_choices, pending_natures=pending_natures, execution_tree=execution_tree, search_only=True)

			expected_impacts = result.get("expected_impacts")
			parse_tree = result.get("parse_tree")
			pending_choices = result.get("pending_choices")
			pending_natures = result.get("pending_natures")
			execution_tree = result.get("execution_tree")

			times.update({"Iteration" : iteration,
						  "Status" : "Fail" if expected_impacts is not None else "Success",
						  "Bounds" : test_bounds})
			total_results.append(times)

			# Update interval based on result
			if expected_impacts is not None:  # Property satisfied
				intervals[current_impact][1] = (intervals[current_impact][0] + intervals[current_impact][1]) / 2
			else:  # Property not satisfied
				intervals[current_impact][0] = (intervals[current_impact][0] + intervals[current_impact][1]) / 2

	return total_results
	# Print progress
	#print_refinement_progress(iteration, current_impact, intervals, test_bounds, result['result']) if verbose else None

	# Extract final upper bounds
	'''
	final_bounds = {
		impact_name: interval[1]
		for impact_name, interval in intervals.items()
	}
	'''