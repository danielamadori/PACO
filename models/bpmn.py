# File: PACO_MVC_REFACTORED/models/bpmn.py
def compute_bound(expression):
	"""
	Compute the bound based on the BPMN expression.
	For demonstration, returns the number of words in the expression.
	Replace with your actual logic.
	"""
	if not expression:
		return 0
	return len(expression.split())
