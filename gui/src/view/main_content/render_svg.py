from view.visualizer.render_svg import get_visualizer


def get_main_content(callback):
	return get_visualizer(callback,
						  input_id = "dot-store",
						  visualizer_id="main-content")