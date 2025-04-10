from dash import Output, Input
from view.components.render_svg import render


def register_render_svg(render_svg_callback):
    @render_svg_callback(
        Output("svg-bpmn", "children"),
        Output("svg-execution-tree", "children"),
        Output("svg-strategy", "children"),
        Output("svg-bdds", "children"),
        Input("dot-store", "data"),
        prevent_initial_call=True
    )

    def render_all_svgs(dot_store):
        return (
            render(dot_store.get("bpmn", "")),
            render(dot_store.get("execution_tree", "")),
            render(dot_store.get("strategy", "")),
            render(dot_store.get("bdds", ""))
        )