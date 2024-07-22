import pydot
from solver_optimized.solution_tree import SolutionTree
from utils.env import RESOLUTION, PATH_AUTOMA_IMAGE, PATH_AUTOMA_IMAGE_SVG, PATH_AUTOMA_DOT, PATH_AUTOMA_TIME_DOT, \
	PATH_AUTOMA_TIME_IMAGE, PATH_AUTOMA_TIME_IMAGE_SVG, PATH_AUTOMA_TIME_EXTENDED, PATH_AUTOMA_TIME_EXTENDED_DOT, \
	PATH_AUTOMA_TIME_EXTENDED_IMAGE_SVG, PATH_AUTOMA_TIME_EXTENDED_IMAGE

def write_solution_tree(solution_tree: SolutionTree):
	solution_tree.save_dot(PATH_AUTOMA_DOT)

	graphs = pydot.graph_from_dot_file(PATH_AUTOMA_DOT)
	graph = graphs[0]
	graph.write_svg(PATH_AUTOMA_IMAGE_SVG)
	graph.set('dpi', RESOLUTION)
	graph.write_png(PATH_AUTOMA_IMAGE)

	solution_tree.save_dot(PATH_AUTOMA_TIME_DOT, executed_time=True)

	graphs = pydot.graph_from_dot_file(PATH_AUTOMA_TIME_DOT)
	graph = graphs[0]
	graph.write_svg(PATH_AUTOMA_TIME_IMAGE_SVG)
	graph.set('dpi', RESOLUTION)
	graph.write_png(PATH_AUTOMA_TIME_IMAGE)

	solution_tree.save_dot(PATH_AUTOMA_TIME_EXTENDED_DOT, executed_time=True, all_states=True)

	graphs = pydot.graph_from_dot_file(PATH_AUTOMA_TIME_EXTENDED_DOT)
	graph = graphs[0]
	graph.write_svg(PATH_AUTOMA_TIME_EXTENDED_IMAGE_SVG)
	graph.set('dpi', RESOLUTION)
	graph.write_png(PATH_AUTOMA_TIME_EXTENDED_IMAGE)