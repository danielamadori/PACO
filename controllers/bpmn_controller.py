# File: PACO_MVC_REFACTORED/controllers/bpmn_controller.py
def store_expression_data(store_data, expression, compute_bound_func):
	"""
	Update store data with the BPMN expression and computed bound.
	"""
	if expression:
		store_data['expression'] = expression
		store_data['bound'] = compute_bound_func(expression)
	return store_data

def store_duration_data(store_data, duration):
	"""
	Update store data with the duration.
	"""
	if duration:
		store_data['duration'] = duration
	return store_data

def store_details_data(store_data, impacts, delay, probabilities):
	"""
	Update store data with the details.
	"""
	if impacts and delay is not None and probabilities is not None:
		store_data['details'] = {
			'impacts': impacts,
			'delay': delay,
			'probabilities': probabilities
		}
	return store_data
