import pydot
from solver_optimized.solution_tree import SolutionTree
from utils.env import RESOLUTION, PATH_AUTOMA_IMAGE, PATH_AUTOMA_IMAGE_SVG, PATH_AUTOMA_DOT, PATH_AUTOMA_TIME_DOT, \
	PATH_AUTOMA_TIME_IMAGE, PATH_AUTOMA_TIME_IMAGE_SVG, PATH_AUTOMA_TIME_EXTENDED, PATH_AUTOMA_TIME_EXTENDED_DOT, \
	PATH_AUTOMA_TIME_EXTENDED_IMAGE_SVG, PATH_AUTOMA_TIME_EXTENDED_IMAGE


def write_image(frontier: list[SolutionTree], dotPath: str, svgPath: str, pngPath: str):
	graphs = pydot.graph_from_dot_file(dotPath)
	graph = graphs[0]
	# print([node.get_name() for node in graph.get_nodes()])
	# color the winning nodes
	if frontier is not None:
		for el in frontier:
			node = graph.get_node('"' + el.state_str() + '"')[0]
			node.set_style('filled')
			node.set_fillcolor('green')

	graph.write_svg(svgPath)
	graph.set('dpi', RESOLUTION)
	graph.write_png(pngPath)


def write_solution_tree(solution_tree: SolutionTree, frontier: list[SolutionTree] = []):
	solution_tree.save_dot(PATH_AUTOMA_DOT)
	write_image(frontier, PATH_AUTOMA_DOT, PATH_AUTOMA_IMAGE_SVG, PATH_AUTOMA_IMAGE)

	solution_tree.save_dot(PATH_AUTOMA_TIME_DOT, executed_time=True)
	write_image(frontier, PATH_AUTOMA_TIME_DOT, PATH_AUTOMA_TIME_IMAGE_SVG, PATH_AUTOMA_TIME_IMAGE)

	solution_tree.save_dot(PATH_AUTOMA_TIME_EXTENDED_DOT, executed_time=True, all_states=True)
	write_image(frontier, PATH_AUTOMA_TIME_EXTENDED_DOT, PATH_AUTOMA_TIME_EXTENDED_IMAGE_SVG, PATH_AUTOMA_TIME_EXTENDED_IMAGE)
