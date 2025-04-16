from dash import Output, Input, html


def register_render_svg(render_svg_callback):
    @render_svg_callback(
        Output("svg-bpmn", "children"),
        #Output("svg-bdds", "children"),
        Input("dot-store", "data"),
        prevent_initial_call=True
    )

    def render_all_svgs(dot_store):
        return (
            render(dot_store.get("bpmn", ""))#,
            #render(dot_store.get("bdds", ""))
        )


def render(svg_str:str):
	return html.Iframe(
		src=svg_str,
		style={"width": "100%", "height": "100%", "border": "none"}
	)
