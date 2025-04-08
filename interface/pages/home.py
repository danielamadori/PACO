import json
import dash
from dash import html, callback, Output, Input, dcc, State, ALL
import dash_bootstrap_components as dbc
from dash import dcc
from core.config import ALGORITHMS, DELAYS, DURATIONS, H, IMPACTS, PATH_BPMN, EXPRESSION, IMPACTS_NAMES, PROBABILITIES, LOOP_ROUND, LOOP_PROBABILITY, SESE_PARSER
from core.grammar.syntax import extract_nodes

dash.register_page(__name__, path='/')

from dash import Input, Output, State, callback
from copy import deepcopy

DEFAULT_DURATION = 1


def update_bpmn_data(data):
    alert = ''

    if data[EXPRESSION] == '':
        return data, alert

    tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(data[EXPRESSION]))
    for task in tasks:
        if task not in data[IMPACTS]:
            data[IMPACTS][task] = {}

        for impact_name in data[IMPACTS_NAMES]:
            if impact_name in data[IMPACTS][task]:
                continue
            data[IMPACTS][task][impact_name] = 0.0

        if task not in data[DURATIONS]:
            data[DURATIONS][task] = [0, DEFAULT_DURATION]

    for choice in choices:
        if choice not in data[DELAYS]:
            data[DELAYS][choice] = 0
    for nature in natures:
        if nature not in data[PROBABILITIES]:
            data[PROBABILITIES][nature] = 0.5
    for loop  in loops:
        if loop not in data[LOOP_PROBABILITY]:
            data[LOOP_PROBABILITY][loop] = 0.5
        if loop not in data[LOOP_ROUND]:
            data[LOOP_ROUND][loop] = 1


    if len(data[IMPACTS_NAMES]) < 1:
        return data, dbc.Alert(f"Add an impacts", color="danger", dismissable=True)

    # Filter the data to keep only the relevant tasks, choices, natures, and loops
    bpmn = deepcopy(data)
    bpmn[IMPACTS_NAMES] = sorted(data[IMPACTS_NAMES])
    bpmn[IMPACTS] = {
        task: [data[IMPACTS][task][impact_name] for impact_name in bpmn[IMPACTS_NAMES]]
        for task in tasks if task in data[IMPACTS]
    }
    bpmn[DURATIONS] = {task: data[DURATIONS][task] for task in tasks if task in data[DURATIONS]}
    bpmn[DELAYS] = {choice: data[DELAYS][choice] for choice in choices if choice in data[DELAYS]}
    bpmn[PROBABILITIES] = {nature: data[PROBABILITIES][nature] for nature in natures if nature in data[PROBABILITIES]}
    bpmn[LOOP_PROBABILITY] = {loop: data[LOOP_PROBABILITY][loop] for loop in loops if loop in data[LOOP_PROBABILITY]}
    bpmn[LOOP_ROUND] = {loop: data[LOOP_ROUND][loop] for loop in loops if loop in data[LOOP_ROUND]}

    try:
        resp = requests.get(API_URL, json={'bpmn': bpmn}, headers=HEADERS)
        resp.raise_for_status()
        dot = resp.json().get('bpmn_dot', '')
    except requests.exceptions.RequestException as e:
        return data, dbc.Alert(f"Processing error: {str(e)}", color="danger", dismissable=True)

    svg = graphviz.Source(dot).pipe(format='svg').decode('utf-8')
    #write the svg file
    with open('test.svg', 'w') as f:
        f.write(svg)
    #return html.Div(svg, dangerously_allow_html=True)
    #return html.Div(svg, dangerously_allow_html=True), False, "", ""

    return data, alert


@callback(
    Output('bpmn-lark-store', 'data'),
    Output('bpmn-alert', 'children'),
    Input('input-bpmn', 'value'),
    State('bpmn-lark-store', 'data'),
    prevent_initial_call=True
)
def update_expression(current_expression, data):
    return validate_expression_and_update(current_expression, data)

def validate_expression_and_update(current_expression, data):
    print(f"Current expression: {current_expression}, data: {data}")
    alert = ''
    if current_expression is None:
        return data, alert

    current_expression = current_expression.replace("\n", "").replace("\t", "").strip().replace(" ", "")
    if current_expression == '':
        return data, dbc.Alert("The expression is empty.", color="warning", dismissable=True)

    if current_expression != data.get(EXPRESSION, ''):
        try:
            SESE_PARSER.parse(current_expression)
        except Exception as e:
            return data, dbc.Alert(f"Parsing error: {str(e)}", color="danger", dismissable=True)
        data[EXPRESSION] = current_expression

    return update_bpmn_data(data)



spinner = dbc.Spinner(color="primary", type="grow", fullscreen=True)


def layout():
    return html.Div([
        dcc.Store(id='bpmn-lark-store', data={
            EXPRESSION: '',
            H: 0,
            IMPACTS: {},
            DURATIONS: {},
            IMPACTS_NAMES : [],
            DELAYS: {},
            PROBABILITIES: {},
            LOOP_PROBABILITY: {},
            LOOP_ROUND: {}
        }, storage_type='session'),

        html.Div(id='logging'),
        html.Div(id='logging-strategy'),
        dcc.Tabs(id="tabs", value='tab-1', children=[
            ################################
            ### DEFINING THE BPMN + CPI  ###
            ################################
            dcc.Tab(label='BPMN+CPI', value='tab-1', children=[
                html.Div([
                    html.H1('Insert your BPMN here:'),
                    html.Div(id='bpmn-alert'),
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select a JSON File')
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        # Allow multiple files to be uploaded
                        multiple=True
                    ),
                    html.Div(id='output-data-upload'),
                    html.Br(),
                    html.P("""Here is an example of a BPMN complete diagram: Task0, (Task1 || Task4), (Task3 ^[N1] Task9, Task8 /[C1] Task2)"""),
                    html.Br(),
                    html.Div(id='loaded-bpmn-file'),
                    html.Br(),
                    dcc.Input(type="text", debounce=True, id='input-bpmn', style={'width': '90%'}),
                    html.Div([
                        html.Div(id='task-duration'),
                        html.Div(id='choice-table'),
                        html.Div(id='nature-table'),
                        html.Div(id='loop-table'),
                    ], style={
                        "display": "flex",
                        "gap": "20px",
                        "flexWrap": "wrap",
                        "justifyContent": "center"
                    }),
                    html.A('Download diagram as SVG', id='download-diagram', download='diagram.svg', href=PATH_BPMN+'.svg', target='_blank'),
                    dbc.Button('Next', id='go-to-define-durations'),
                ])
            ]),
            dcc.Tab(label='Durations', value='tab-2', children=[
                html.Div([
                    dbc.Button('Back', id='back-to-load-bpmn'),
                    dbc.Button('Next', id='go-to-impacts-bpmn'),
                ])
            ]),
            dcc.Tab(label='CPI: Choices and natures', value='tab-4', children=[
                html.Div([
                    html.P('Insert the probabilities for each natural choice, if any. The values have to be between 0 and 1.'),
                    html.Div(id= 'probabilities'),
                    html.Br(),
                    html.P('Insert the delays for each natural choice, if any. The values have to be between 0 and 100.'),
                    html.Div(id= 'delays'),
                    html.Br(),
                    html.P('Insert the number of maximum loops round, if any. The value have to be between 1 and 100.'),
                    html.Div(id= 'loops'),
                    html.Br(),
                    dbc.Button('Back', id='back-to-impacts'),
                    dbc.Button('Next', id='go-to-show-bpmn'),
                ])
            ]),
            ###############################
            ### BPMN DIAGRAM USING LARK ###
            ###############################
            dcc.Tab(label='Show BPMN', value='tab-5', children=[
                dbc.Button('Create diagram', id='create-diagram-button'),
                dbc.Spinner(html.Div(id='api-diagram-output'), color="primary"),
                html.Div([
                    html.H3("BPMN diagram in lark:"),
                    #html.Img(id='lark-diagram1', src= 'assets/graph.svg', style={'height': '500', 'width': '1000'}),
                    html.Iframe(id="lark-frame",
                                src='',#PATH_IMAGE_BPMN_LARK_SVG,
                                style={'height': '100%', 'width': '100%'}
                                # style={"height": "70vh", "width": "95vw", 'border':'none'}
                                ), #style={'height': '100%', 'width': '100%'}
                    # html.Embed(
                    #     id="lark-frame",
                    #     src=PATH_IMAGE_BPMN_LARK_SVG,
                    #     type="image/svg+xml",
                    #     style={"height": "100vh", "width": "100vw", "border": "none"}
                    # ),
                    html.Br(),
                    # download diagram as svg
                    html.Br(),
                    dbc.Button('Back', id='back-to-load-cpi'),
                    dbc.Button('Next', id='go-to-define-strategy'),
                ]),
                html.Br(),
            ]),
            ################
            ### STRATEGY ###
            ################
            dcc.Tab(label='Define Strategy',  value='tab-6', children=[
                html.Div([
                    html.Div(id="strategy", children=[
                        html.H3("Choose the algorithm to use:"),
                        dcc.Dropdown(
                            id='choose-strategy',
                            options=[
                                {'label': value, 'value': key}
                                for key, value in ALGORITHMS.items()
                            ],
                            value= list(ALGORITHMS.keys())[0] # default value
                        ),
                        html.H3('Insert the bound'),
                        html.Div(id= 'choose-bound-dict'),
                        html.Br(),
                        html.Br(),
                        dbc.Button('Find strategy', id='find-strategy-button'),
                    ]),
                    html.Br(),
                    html.Br(),
                    dbc.Button('Back', id='back-to-show-bpmn'),
                    dbc.Button('Next', id='go-to-show-strategy'),
                ])
            ]),
            dcc.Tab(label='Show Strategy',  value='tab-7', children=[
                html.Div([
                    html.Div(
                        children = [
                            dcc.Loading(
                                id="loading-strategy",
                                children=[html.Div([html.Div(id="strategy-founded")])],
                                type="circle", #'graph', 'cube', 'circle', 'dot', 'default'
                                # fullscreen=True,
                            )
                        ]
                    ),
                    dbc.Button('Back', id='back-to-strategy'),
                    dbc.Button('Next', id='go-to-download'),
                ])
            ]),
            dcc.Tab(label='Download data',  value='tab-8', children=[
                ########################
                ### DOWNLOAD EXAMPLE ###
                ########################
                html.Div(id="download-example", children=[
                    html.H1("Download the example:"),
                    dbc.Checklist(
                        options=[
                            {"label": "BPMN + CPI", "value": 1},
                            {"label": "Bound", "value": 2},
                            {"label": "Strategy", "value": 3},
                        ],
                        value=[1, 2],
                        id="switches-input",
                        switch=True,
                    ),
                    dbc.Button("Download", id="btn-download"),
                    dcc.Download(id="download"),
                    html.Br(),
                    dbc.Button('Back', id='back-to-show-strategy'),
                    # dbc.Button('Next', id='go-to-define-strategy'),
                ]),
            ]),
            # dcc.Tab(label='Strategy Explainer', value='tab-6', children=[
            #     html.Div([
            #         html.H1("Explaining strategy"),
            #           dbc.Button('Back', id='back-to-load-bpmn'),
            #     ])
            # ])
        ]),

    ]
)

######################
## NAVIGATE TABS  ###
######################

@callback(
    Output('tabs', 'value', allow_duplicate=True),
    [
     Input('back-to-load-bpmn', 'n_clicks'),
     Input('go-to-show-bpmn', 'n_clicks'),
     Input('back-to-load-cpi', 'n_clicks'),
     Input('go-to-define-strategy', 'n_clicks'),
     Input('back-to-show-bpmn', 'n_clicks'),
     Input('go-to-show-strategy', 'n_clicks'),
     Input('back-to-strategy', 'n_clicks'),
     Input('go-to-define-durations', 'n_clicks'),
     Input('go-to-impacts-bpmn', 'n_clicks'),
     Input('back-to-durations', 'n_clicks'),
     Input('go-to-cp', 'n_clicks'),
     Input('back-to-impacts', 'n_clicks'),
     Input('back-to-show-strategy', 'n_clicks'),
     Input('go-to-download', 'n_clicks'),
    ],
    prevent_initial_call=True
)
def navigate_tabs(*args):
    ctx = dash.callback_context

    if not ctx.triggered:
        # No button was clicked yet
        return 'tab-1'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Mapping from button ID to tab value
    tab_mapping = {
        'go-to-define-durations': 'tab-2',
        'go-to-impacts-bpmn': 'tab-3',
        'back-to-durations': 'tab-2',
        'go-to-cp': 'tab-4',
        'back-to-impacts': 'tab-3',
        'go-to-define-cpi': 'tab-2',
        'back-to-load-bpmn': 'tab-1',
        'go-to-show-bpmn': 'tab-5',
        'back-to-load-cpi': 'tab-4',
        'go-to-define-strategy': 'tab-6',
        'back-to-show-bpmn': 'tab-5',
        'go-to-show-strategy': 'tab-7',
        'back-to-strategy': 'tab-6',
        'back-to-show-strategy': 'tab-7',
        'go-to-download': 'tab-8',
    }

    return tab_mapping.get(button_id, 'tab-1')  # Default to 'tab-1' if button_id is not found



@callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open



@callback(
    Output("download", "data"),
    Input("btn-download", "n_clicks"),
    State('switches-input', 'value'),
    State('bpmn-lark-store', 'data'),
    prevent_initial_call=True,
)
def func(n_clicks, switches, bpmn_lark):
    print(f' in dwonlaoad {switches}')
    content = {}
    for el in switches:
        if el == 1:
            content['bpmn'] = bpmn_lark
        '''
        elif el == 2:
            content['bound'] = strategy_d[BOUND]
        elif el == 3:
            content['strategy'] = strategy_d[STRATEGY]
        '''
    content = json.dumps(content)
    return dict(content=content, filename="bpmn_cpi_strategy.json")


import requests, graphviz
from dash import Output, Input, State

API_URL = "http://127.0.0.1:8000/create_bpmn"
HEADERS = {"Content-Type": "application/json"}

@callback(
    Output('api-diagram-output', 'children'),
    Input('create-diagram-button', 'n_clicks'),
    State('bpmn-lark-store', 'data'),
    prevent_initial_call=True
)
def generate_bpmn_diagram(n_clicks, bpmn_data):
    try:
        response = requests.get(API_URL, json={'bpmn': bpmn_data}, headers=HEADERS)
        response.raise_for_status()
        dot_diagram = response.json().get('bpmn_dot', '')
        svg = graphviz.Source(dot_diagram).pipe(format='svg').decode('utf-8')
        return html.Div(svg, dangerously_allow_html=True)
    except Exception as e:
        return dbc.Alert(f"API Error: {str(e)}", color="danger")


@callback(
    Output('task-duration', 'children'),
    Input('bpmn-lark-store', 'data'),
    prevent_initial_call=True
)
def generate_duration_table(data):
    if DURATIONS not in data:
        return dash.no_update

    rows = []

    lark_tree = SESE_PARSER.parse(data[EXPRESSION])
    tasks, choices, natures, loops = extract_nodes(lark_tree)
    for task in sorted(data[DURATIONS].keys()):
        if task not in tasks:
            continue

        (min_d, max_d) = data[DURATIONS][task]

        impact_inputs = [
            html.Td(dcc.Input(
                value=data[IMPACTS].get(task, {}).get(impact_name, 0.0),
                type='number', min=0, debounce=True, style={'width': '80px', "border": "none", "padding": "0.4rem"},
            id={'type': f'impact-{impact_name}', 'index': task}
            )) for impact_name in data[IMPACTS_NAMES]
        ]

        row = html.Tr([
                html.Td(html.Span(task, style={"whiteSpace": "nowrap", "overflow": "hidden", "textOverflow": "ellipsis", "minWidth": "100px", "display": "inline-block"})),
                html.Td(dcc.Input(value=min_d, type='number', min=0, debounce=True, style={'width': '80px', "border": "none", "padding": "0.4rem"}, id={'type': 'min-duration', 'index': task})),
                html.Td(dcc.Input(value=max_d, type='number', min=0, debounce=True, style={'width': '80px', "border": "none", "padding": "0.4rem"}, id={'type': 'max-duration', 'index': task})),
              ] + impact_inputs)
        rows.append(row)

    new_impacts_element = html.Div([
        dbc.Input(
            id='new-impact-name',
            placeholder='New impact',
            debounce=True,
            style={'flexGrow': 1, 'marginRight': '4px'}
        ),
        dbc.Button(
            "+",
            id='add-impact-button',
            n_clicks=0,
            color="success",
            size="sm",
            style={"padding": "0.25rem 0.4rem", "lineHeight": "1"}
        ),
    ], style={'width': '180px', 'display': 'flex', 'alignItems': 'center'})


    impacts_sub_columns = [
        html.Th([
            html.Div([
                html.Span(name, style={"whiteSpace": "nowrap", "overflow": "hidden", "textOverflow": "ellipsis", "maxWidth": "80px", "display": "inline-block"}),
                dbc.Button("×", id={'type': 'remove-impact', 'index': name},
                           n_clicks=0, color="danger", size="sm", className="ms-1", style={"padding": "2px 6px"})
            ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'space-between'})
        ]) for name in data[IMPACTS_NAMES]
    ]


    if len(data[IMPACTS_NAMES]) < 3:
        impacts_sub_columns.append(html.Th([ new_impacts_element ]))

    header = html.Thead([
        html.Tr([
            html.Th(html.H3("Tasks"), rowSpan=2, style={'vertical-align': 'middle'}),
            html.Th("Duration", colSpan=2, style={'vertical-align': 'middle', 'textAlign': 'center'}),
            html.Th("Impacts", colSpan=len(data[IMPACTS_NAMES]) + 2, style={'vertical-align': 'middle', 'textAlign': 'center'})
        ]),
        html.Tr([
            html.Th("Min", style={'width': '80px', 'vertical-align': 'middle'}),
            html.Th("Max", style={'width': '80px', 'vertical-align': 'middle'})
        ] + impacts_sub_columns)
    ])

    table = [html.Div([
        dbc.Table(
            [header] + rows,
            bordered=True,
            hover=True,
            responsive=True,
            striped=True,
            style={"width": "auto", "margin": "auto", "borderCollapse": "collapse"},
            className="table-sm"
        )
    ], style={
        "display": "inline-block",
        "padding": "10px",
        "border": "1px solid #ccc",
        "borderRadius": "10px",
        "marginTop": "20px"
    }),
        html.Div(id='add-impact-alert', className='mt-2')
    ]

    if len(data[IMPACTS_NAMES]) > 2:
        table.insert(1, new_impacts_element)

    return html.Div(table)


@callback(
    Output('bpmn-lark-store', 'data', allow_duplicate=True),
    Output('add-impact-alert', 'children'),
    Input('add-impact-button', 'n_clicks'),
    State('new-impact-name', 'value'),
    State('bpmn-lark-store', 'data'),
    prevent_initial_call='initial_duplicate'
)
def add_impact_column(n_clicks, new_impact_name, data):
    if not new_impact_name or new_impact_name.strip() == '':
        return data, ''

    new_impact_name = new_impact_name.strip()
    if new_impact_name in data[IMPACTS_NAMES]:
        alert = dbc.Alert(f"Impact '{new_impact_name}' already exists.", color="warning", dismissable=True)
        return data, alert

    data[IMPACTS_NAMES].append(new_impact_name)
    return update_bpmn_data(data)


@callback(
    Output('bpmn-lark-store', 'data', allow_duplicate=True),
    Output('bpmn-alert', 'children', allow_duplicate=True),
    Input({'type': 'remove-impact', 'index': ALL}, 'n_clicks'),
    State('bpmn-lark-store', 'data'),
    State({'type': 'remove-impact', 'index': ALL}, 'id'),
    prevent_initial_call='initial_duplicate'
)
def remove_impact_column(n_clicks_list, data, id_list):
    changed = False
    for n_clicks, id_obj in zip(n_clicks_list, id_list):
        if n_clicks > 0:
            impact_to_remove = id_obj['index']
            if impact_to_remove in data[IMPACTS_NAMES]:
                data[IMPACTS_NAMES].remove(impact_to_remove)
                changed = True
    if changed:
        return update_bpmn_data(data)
    return data, ''


@callback(
    Output('bpmn-lark-store', 'data', allow_duplicate=True),
    Output('bpmn-alert', 'children', allow_duplicate=True),
    Input({'type': ALL, 'index': ALL}, 'value'),
    State({'type': ALL, 'index': ALL}, 'id'),
    State('bpmn-lark-store', 'data'),
    prevent_initial_call='initial_duplicate'
)
def update_impacts_from_inputs(values, ids, data):
    updated = False
    for value, id_obj in zip(values, ids):
        id_type = id_obj['type']
        if id_type.startswith('impact-'):
            impact_name = id_type.replace('impact-', '')
            task = id_obj['index']
            if task in data[IMPACTS]:
                data[IMPACTS][task][impact_name] = value
                updated = True
    if updated:
        return update_bpmn_data(data)
    return data, ''


@callback(
    Output('bpmn-lark-store', 'data', allow_duplicate=True),
    Output('bpmn-alert', 'children', allow_duplicate=True),
    Input({'type': 'min-duration', 'index': ALL}, 'value'),
    Input({'type': 'max-duration', 'index': ALL}, 'value'),
    State({'type': 'min-duration', 'index': ALL}, 'id'),
    State('bpmn-lark-store', 'data'),
    prevent_initial_call='initial_duplicate'
)
def update_duration_from_inputs(min_values, max_values, ids, data):
    changed = False
    for min_v, max_v, id_obj in zip(min_values, max_values, ids):
        task = id_obj['index']
        if task in data.get(DURATIONS, {}):
            data[DURATIONS][task] = [min_v, max_v]
            changed = True
    if changed:
        return update_bpmn_data(data)
    return data, ''

def create_table(title, columns, rows, table_id):
    return html.Div([
        html.H5(title, style={'textAlign': 'center'}),
        dbc.Table(
            [html.Thead(html.Tr([html.Th(col) for col in columns]))] + rows,
            bordered=True,
            hover=True,
            responsive=True,
            striped=True,
            className="table-sm",
            style={
                "width": "auto",
                "margin": "auto",
                "borderCollapse": "collapse"
            }
        )
    ], style={
        "display": "inline-block",
        "padding": "10px",
        "border": "1px solid #ccc",
        "borderRadius": "10px",
        "marginTop": "20px",
        "verticalAlign": "top"
    })


@callback(
    Output('choice-table', 'children'),
    Input('bpmn-lark-store', 'data'),
    prevent_initial_call=True
)
def generate_choice_table(data):
    _, choices, _, _ = extract_nodes(SESE_PARSER.parse(data[EXPRESSION]))

    rows = [
        html.Tr([
            html.Td(name),
            html.Td(dcc.Input(value=data[PROBABILITIES][name], type="number", min=0, max=1, step=0.01, debounce=True,
                              id={'type': 'choice-prob', 'index': name}))
        ]) for name in choices
    ]
    return create_table("Choices", ["Name", "Probability"], rows, 'choice-table')


@callback(
    Output('nature-table', 'children'),
    Input('bpmn-lark-store', 'data'),
    prevent_initial_call=True
)
def generate_nature_table(data):
    _, _, natures, _ = extract_nodes(SESE_PARSER.parse(data[EXPRESSION]))

    rows = [
        html.Tr([
            html.Td(name),
            html.Td(dcc.Input(value=data[DELAYS][name], type="number", min=0, max=100, step=1, debounce=True,
                              id={'type': 'nature-delay', 'index': name}))
        ]) for name in natures
    ]
    return create_table("Natures", ["Name", "Delay"], rows, 'nature-table')


@callback(
    Output('loop-table', 'children'),
    Input('bpmn-lark-store', 'data'),
    prevent_initial_call=True
)
def generate_loop_table(data):
    _, _, _, loops = extract_nodes(SESE_PARSER.parse(data[EXPRESSION]))

    rows = [
        html.Tr([
            html.Td(name),
            html.Td(dcc.Input(value=data[LOOP_PROBABILITY][name], type="number", min=0, max=1, step=0.01, debounce=True,
                              id={'type': 'loop-prob', 'index': name})),
            html.Td(dcc.Input(value=data[LOOP_ROUND][name], type="number", min=1, max=100, step=1, debounce=True,
                              id={'type': 'loop-round', 'index': name}))
        ]) for name in loops
    ]
    return create_table("Loops", ["Name", "Prob.", "Max Rounds"], rows, 'loop-table')


@callback(
    Output('bpmn-lark-store', 'data', allow_duplicate=True),
    Output('bpmn-alert', 'children', allow_duplicate=True),
    Input({'type': 'choice-prob', 'index': ALL}, 'value'),
    State({'type': 'choice-prob', 'index': ALL}, 'id'),
    State('bpmn-lark-store', 'data'),
    prevent_initial_call='initial_duplicate'
)
def update_choices(values, ids, data):
    for value, id_obj in zip(values, ids):
        data[PROBABILITIES][id_obj['index']] = value
    return update_bpmn_data(data)


@callback(
    Output('bpmn-lark-store', 'data', allow_duplicate=True),
    Output('bpmn-alert', 'children', allow_duplicate=True),
    Input({'type': 'nature-delay', 'index': ALL}, 'value'),
    State({'type': 'nature-delay', 'index': ALL}, 'id'),
    State('bpmn-lark-store', 'data'),
    prevent_initial_call='initial_duplicate'
)
def update_natures(values, ids, data):
    for value, id_obj in zip(values, ids):
        data[DELAYS][id_obj['index']] = value
    return update_bpmn_data(data)


@callback(
    Output('bpmn-lark-store', 'data', allow_duplicate=True),
    Output('bpmn-alert', 'children', allow_duplicate=True),
    Input({'type': 'loop-prob', 'index': ALL}, 'value'),
    Input({'type': 'loop-round', 'index': ALL}, 'value'),
    State({'type': 'loop-prob', 'index': ALL}, 'id'),
    State('bpmn-lark-store', 'data'),
    prevent_initial_call='initial_duplicate'
)
def update_loops(probs, rounds, ids, data):
    for p, r, id_obj in zip(probs, rounds, ids):
        loop = id_obj['index']
        data[LOOP_PROBABILITY][loop] = p
        data[LOOP_ROUND][loop] = r
    return update_bpmn_data(data)
