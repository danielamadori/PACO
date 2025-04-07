# views/callbacks.py
import json, requests, graphviz
from dash import html, dcc, Input, Output, State, ctx
import dash_bootstrap_components as dbc

from main import app
from models.bpmn import compute_bound
from controllers.bpmn_controller import store_expression_data, store_duration_data, store_details_data

API_URL = "http://127.0.0.1:8000/create_bpmn"
HEADERS = {"Content-Type": "application/json"}

# Macro-like helper function for modal
def open_modal(header, body):
	return True, header, body

# Content callback
@app.callback(
	Output('tab-content', 'children'),
	Input('tabs', 'value'),
	State('bpmn-store', 'data')
)
def render_tab(tab, data):
	if tab == 'expression':
		return html.Div([
			dcc.Textarea(id='input-expression', style={'width':'100%', 'height':120}),
			dbc.Button('Save Expression', id='save-expression', color='primary')
		])
	elif tab == 'duration':
		return html.Div([
			dcc.Textarea(id='input-duration', style={'width':'100%', 'height':120}),
			dbc.Button('Save Duration', id='save-duration', color='primary')
		])
	elif tab == 'details':
		return html.Div([
			dcc.Textarea(id='input-impacts', placeholder='Impacts JSON', style={'width':'100%', 'height':100}),
			dcc.Input(id='input-delay', type='number', placeholder='Delay', style={'width':'100%'}),
			dcc.Input(id='input-probabilities', type='number', placeholder='Probabilities', style={'width':'100%'}),
			dbc.Button('Save Details', id='save-details', color='primary')
		])
	elif tab == 'output':
		return dbc.Button('Generate Diagram', id='generate-diagram', color='success'), html.Div(id='diagram-output')

# Save callbacks with modal feedback
@app.callback(
	Output('bpmn-store', 'data'),
	Output('modal', 'is_open'),
	Output('modal-header', 'children'),
	Output('modal-body', 'children'),
	Input('save-expression', 'n_clicks'),
	Input('save-duration', 'n_clicks'),
	Input('save-details', 'n_clicks'),
	State('input-expression', 'value'),
	State('input-duration', 'value'),
	State('input-impacts', 'value'),
	State('input-delay', 'value'),
	State('input-probabilities', 'value'),
	State('bpmn-store', 'data'),
	prevent_initial_call=True
)
def save_data(n_expr, n_dur, n_det, expr, dur, impacts, delay, prob, data):
	data = data or {}
	trigger_id = ctx.triggered_id

	print(f"Triggered: {trigger_id}, Expression: {expr}, Duration: {dur}, Impacts: {impacts}, Delay: {delay}, Probabilities: {prob}")
	if trigger_id == 'save-expression':
		if not expr:
			return data, *open_modal("Error", "Expression cannot be empty.")
		data = store_expression_data(data, expr, compute_bound)
		return data, *open_modal("Success", "Expression saved.")
	elif trigger_id == 'save-duration':
		try:
			dur_json = json.loads(dur)
			data = store_duration_data(data, dur_json)
			return data, *open_modal("Success", "Duration saved.")
		except:
			return data, *open_modal("Error", "Duration must be valid JSON.")
	elif trigger_id == 'save-details':
		try:
			impacts_json = json.loads(impacts)
			delay = float(delay)
			prob = float(prob)
			data = store_details_data(data, impacts_json, delay, prob)
			return data, *open_modal("Success", "Details saved.")
		except:
			return data, *open_modal("Error", "Details inputs are invalid.")

# Generate BPMN Diagram
@app.callback(
	Output('diagram-output', 'children'),
	Output('modal', 'is_open', allow_duplicate=True),
	Output('modal-header', 'children', allow_duplicate=True),
	Output('modal-body', 'children', allow_duplicate=True),
	Input('generate-diagram', 'n_clicks'),
	State('bpmn-store', 'data'),
	prevent_initial_call=True
)
def generate_bpmn(_, data):
	if not data or 'expression' not in data:
		return "", *open_modal("Error", "Missing expression.")

	bpmn_payload = {
		"EXPRESSION": data.get("expression", ""),
		"H": 0,
		"IMPACTS": data.get('details', {}).get('impacts', {}),
		"DURATIONS": data.get('duration', {}),
		"IMPACTS_NAMES": ["cost", "hours"],
		"PROBABILITIES": {"N1": data.get('details', {}).get('probabilities', 0)},
		"DELAYS": {"C1": data.get('details', {}).get('delay', 0)},
		"LOOP_PROBABILITY": {},
		"LOOP_ROUND": {}
	}
	try:
		resp = requests.get(API_URL, json={'bpmn': bpmn_payload}, headers=HEADERS)
		resp.raise_for_status()
		dot = resp.json().get('bpmn_dot', '')
		svg = graphviz.Source(dot).pipe(format='svg').decode('utf-8')
		return html.Div(svg, dangerously_allow_html=True), False, "", ""
	except Exception as e:
		return "", *open_modal("API Error", str(e))

# Close Modal
@app.callback(
	Output("modal", "is_open", allow_duplicate=True),
	Input("close-modal", "n_clicks"),
	State("modal", "is_open"),
	prevent_initial_call=True
)
def close_modal(_, is_open):
	return not is_open
