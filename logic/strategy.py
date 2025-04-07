import json
import dash
from dash import html, dcc, Input, Output,State, callback
import dash_bootstrap_components as dbc
from dash import dcc

from core.api.remote_api import calc_strat
from core.config import DELAYS
from interface.pages.home import navigate_tabs


@callback(
    [Output('strategy-founded', 'children'), Output('logging-strategy', 'children'), Output('tabs','value', allow_duplicate=True)],
    Input('find-strategy-button', 'n_clicks'),
    State('choose-strategy', 'value'),
    State('choose-bound-dict', 'children'),
    State('bpmn-lark-store', 'data'),
    prevent_initial_call=True
)
def find_strategy(n_clicks, algo:str, bound:dict, bpmn_lark:dict):
    """This function is when the user search a str."""
    if bound == {} or bound == None:
        return [html.P(f'Insert a bound dictionary to find the strategy.'),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("ERROR"),  class_name="bg-danger"),
                        dbc.ModalBody("Insert a bound dictionary to find the strategy."),
                    ],
                    id="modal",
                    is_open=True,
                ),'tab-6'
            ]
    expected_impacts = None
    choices = None
    text_result = ''
    try:
        text_result, bound = check_input(bpmn_lark, bound)
        print(bound)
        code, resp_json = calc_strat(bpmn_lark, bound, algo, token='neonrejieji')
        print(resp_json)
        print(code)
        if code != 200:
            return [html.P(f'Insert a bound dictionary to find the strategy.'),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("ERROR"),  class_name="bg-danger"),
                        dbc.ModalBody(str(resp_json)),
                    ],
                    id="modal",
                    is_open=True,
                ),'tab-6'
            ]
        #strategy_d[BOUND] = resp_json[BOUND]
        expected_impacts = resp_json['expected_impacts']
        choices = resp_json['choices']
        text_result = resp_json['text_result']
    except Exception as e:
        error = True
        text_result = str(e)

    if expected_impacts is None:
        return [None,
            dbc.Modal([
                        dbc.ModalHeader(dbc.ModalTitle("Strategy not found"),  class_name="bg-info"),
                        dbc.ModalBody("No strategy found for the given bound. Try with another bound.\n"+ text_result),
                    ],
                id="modal", is_open=True,
            ),'tab-6']

    # # TODO save the strategy for the download
    # #strategy_d[STRATEGY] = ....

    s = [
        html.P(text_result),
        html.Iframe(src='', style={'height': '100%', 'width': '100%'}),
        #html.A('Download strategy diagram as SVG', id='download-diagram', download='strategy.svg', href=PATH_STRATEGY_TREE_STATE_TIME+'.png', target='_blank'),
    ]

    if choices:
        navigate_tabs('go-to-show-strategy')
        list_choices_excluded = list(set(list(bpmn_lark[DELAYS].keys())) - set(choices))
        s.append(dcc.Tabs(
            children=[dcc.Tab(label=c, children=[html.Iframe(src=f'assets/explainer/decision_tree_{c}.svg', style={'height': '100%', 'width': '100%'})]) for c in choices]
        ))
        if list_choices_excluded:
            s.append(dbc.Alert(f" The choices: {list_choices_excluded} are not visited by the explainer. ", color='warning'))

        return [html.Div(s), None, 'tab-7']

    #TODO: create the strategy tree
    s.append(dbc.Alert(" All the choices presents are not visited by the explainer. ", color='warning'))
    return [html.Div(s), None, 'tab-7']

