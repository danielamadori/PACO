import os
import json
from jsonschema import validate, ValidationError

SCHEMA_DIR = os.path.dirname(__file__)
SCHEMAS = {}

for schema_file in os.listdir(SCHEMA_DIR):
	if not schema_file.endswith("_schema.json"):
		continue
	schema_name = schema_file.replace("_schema.json", "")
	with open(os.path.join(SCHEMA_DIR, schema_file), 'r') as f:
		SCHEMAS[schema_name.capitalize()] = json.load(f)

def validate_node(node_data: dict, impact_size: int = -1, non_cumulative_impact_size: int = -1):
	node_type = node_data['type']
	schema = SCHEMAS.get(node_type)

	if not schema:
		raise ValueError(f"Unsupported node type: {node_type}")

	try:
		validate(instance=node_data, schema=schema)
	except ValidationError as e:
		raise ValueError(f"Validation error in node {node_type} with id {node_data['id']}: {e}")

	if node_type == "Task":
		current_impact_size = len(node_data['impact'])
		current_non_cumulative_impact_size = len(node_data['non_cumulative_impact'])

		if impact_size < 0:
			impact_size = current_impact_size
		elif impact_size != current_impact_size:
			raise ValueError(
				f"Task {node_data['id']} has inconsistent impact size: {current_impact_size} (expected {impact_size})"
			)

		if non_cumulative_impact_size < 0:
			non_cumulative_impact_size = current_non_cumulative_impact_size
		elif non_cumulative_impact_size != current_non_cumulative_impact_size:
			raise ValueError(
				f"Task {node_data['id']} has inconsistent non_cumulative_impact size: "
				f"{current_non_cumulative_impact_size} (expected {non_cumulative_impact_size})"
			)

	if "sx_child" in node_data and node_data["sx_child"]:
		sx_impact_size, sx_non_cumulative_impact_size = validate_node(
			node_data["sx_child"], impact_size, non_cumulative_impact_size
		)

		if impact_size < 0:
			impact_size = sx_impact_size
		elif sx_impact_size != impact_size:
			raise ValueError(
				f"Sx child of node {node_data['id']} has inconsistent impact size: {sx_impact_size} (expected {impact_size})"
			)

		if non_cumulative_impact_size < 0:
			non_cumulative_impact_size = sx_non_cumulative_impact_size
		elif sx_non_cumulative_impact_size != non_cumulative_impact_size:
			raise ValueError(
				f"Sx child of node {node_data['id']} has inconsistent non_cumulative_impact size: "
				f"{sx_non_cumulative_impact_size} (expected {non_cumulative_impact_size})"
			)

	if "dx_child" in node_data and node_data["dx_child"]:
		dx_impact_size, dx_non_cumulative_impact_size = validate_node(
			node_data["dx_child"], impact_size, non_cumulative_impact_size
		)

		if impact_size < 0:
			impact_size = dx_impact_size
		elif dx_impact_size != impact_size:
			raise ValueError(
				f"Dx child of node {node_data['id']} has inconsistent impact size: {dx_impact_size} (expected {impact_size})"
			)

		if non_cumulative_impact_size < 0:
			non_cumulative_impact_size = dx_non_cumulative_impact_size
		elif dx_non_cumulative_impact_size != non_cumulative_impact_size:
			raise ValueError(
				f"Dx child of node {node_data['id']} has inconsistent non_cumulative_impact size: "
				f"{dx_non_cumulative_impact_size} (expected {non_cumulative_impact_size})"
			)

	return impact_size, non_cumulative_impact_size
