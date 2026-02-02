from dash import html
import dash_bootstrap_components as dbc

def get_message(msg):
    content = [html.Div(msg['text'])]
    
    if msg.get('is_proposal'):
        content.append(html.Div([
            dbc.Button("Accept", id="btn-accept-proposal", color="success", size="sm", className="me-2"),
            dbc.Button("Reject", id="btn-reject-proposal", color="danger", size="sm")
        ], style={'marginTop': '10px'}))

    return html.Div(
        content,
        style={
            'alignSelf': 'flex-end' if msg['type'] == 'user' else 'flex-start',
            'backgroundColor': '#d1e7dd' if msg['type'] == 'user' else '#e2e3e5',
            'padding': '8px 12px',
            'borderRadius': '12px',
            'maxWidth': '75%',
            'marginBottom': '10px'
        }
    )