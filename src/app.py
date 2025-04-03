import asyncio
import os
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import dash
from api.api import authorization_function, get_agent_definition, invoke_llm
import dash_auth
from dash.dependencies import Input, Output, State
from flask_session import Session
# https://help.dash.app/en/articles/3535011-dash-security-overview
# docker build -t paco_dash .  && docker run -p 8050:8050 paco_dash
# https://github.com/RenaudLN/dash_socketio/tree/main per websocket
chat_history = []
llm, config_llm = None, None

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
            suppress_callback_exceptions=True, 
        )
server = app.server
server.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', os.urandom(24).hex()),
    SESSION_TYPE='filesystem',
    SESSION_FILE_DIR='flask_session'
)
Session(server)

def login(username, password):
    if username== 'admin' and password == 'admin':
        # token = os.urandom(24).hex()
        # server.config.update(
        #     SECRET_KEY=os.environ.get('SECRET_KEY', token),
        #     SESSION_TYPE='filesystem',
        #     SESSION_FILE_DIR='flask_session',
        #     SESSION_PERMANENT=False,
        #     PERMANENT_SESSION_LIFETIME=3600  # Session lifetime in seconds
        # )

        # Initialize Flask-Session
        # Session(server)
        return True
    return False

auth = dash_auth.BasicAuth(
    app,
    auth_func = login, 
)

app.layout = html.Div([  
        dcc.Store(id='auth-token-store', data='vnfo'),#storage_type='session'),     
        dcc.Store(id = 'bpmn-lark-store', data={}),
        dcc.Store(id = 'chat-ai-store'),
        html.H1('BPMN+CPI APP!', style={'textAlign': 'center'}),
        dbc.Row(
            [
                dbc.Col(
                    children = [dbc.DropdownMenu([
                            dbc.DropdownMenuItem(
                                f"{page['name']}", href=page["relative_path"]
                            ) for page in dash.page_registry.values()
                            ],
                            label="Menu",
                        ),
                        dash.page_container,
                    ],
                    width=8
                ),
                dbc.Col(
                    children= [
                        html.Div(
                            [
                                dbc.Button(
                                    "Configure AI Model",
                                    id="collapse-config-button",
                                    className="mb-3",
                                    color="secondary",
                                    n_clicks=0,
                                ),
                                dbc.Collapse(
                                    html.Div([
                                        html.H3("AI Model Configuration"),
                                        html.P('''Configure the AI model to chat with the assistant.
                                               Here an example of the configuration:
                                                  - API Key: 123456
                                                    - Model URL: https://api.openai.com/...
                                                    - Model: llama-3.2-1b-instruct
                                                    - Temperature: 0.7
                                               '''),
                                        dbc.Input(id='model-api-key', placeholder='Enter API Key', type='text'),
                                        html.Br(),
                                        dbc.Input(id='model-url', placeholder='Enter Model URL', type='text'),
                                        html.Br(),
                                        dbc.Input(id='model', placeholder='Enter Model', type='text'),
                                        html.Br(),
                                        html.Label("Temperature"),
                                        dcc.Slider(
                                            id='temperature-slider',
                                            min=0,
                                            max=1,
                                            step=0.01,
                                            value=0.7,
                                            marks={i: f'{i:.1f}' for i in range(0, 1)},
                                            tooltip={
                                                "placement": "bottom",
                                                "always_visible": True,
                                            }
                                        ),
                                        html.Br(),
                                        dbc.Button("Save Configuration", id='save-config-button', color="primary"),
                                        html.Div(id='config-output')
                                    ]),
                                    id="collapse-config",
                                    is_open=False,
                                ),
                            ]
                        ),
                        html.Div(
                            [
                                dbc.Button(
                                    "Open Chat",
                                    id="collapse-button",
                                    className="mb-3",
                                    color="primary",
                                    n_clicks=0,
                                ),
                                dbc.Collapse(
                                    html.Div([
                                        html.H3("Chat with AI"),
                                        dbc.Textarea(id='input-box', placeholder='Type your message here...'),
                                        html.Br(),
                                        dbc.Button(class_name="bi bi-send", id='send-button'),
                                        dcc.Loading(
                                            id="loading-spinner",
                                            type="default",
                                            overlay_style={"visibility":"visible", "filter": "blur(2px)"},
                                            custom_spinner=html.H2(["I'm thinking...", dcc.Loading(id="loading-1", type="default",)]), #,  dbc.Spinner(color="primary")
                                            children=html.Div(id='chat-output-home')
                                        )
                                    ]),
                                    id="collapse",
                                    is_open=False,
                                ),
                            ]
                        ),
                    ],
                    width=4
                ),
            ]
        )
        
    ], style={'padding':'30px'})

#######################

## CHAT WITH AI

#######################

@app.callback(
    [Output('chat-output-home', 'children'),],
    [Input('send-button', 'n_clicks')],
    [State('input-box', 'value'),
     State('auth-token-store', 'data'),
     State('chat-ai-store', 'data')],
    prevent_initial_call=True
)
def update_output(n_clicks, prompt, token, chat_history,  verbose = False):
    if not token:
        return html.P("Please log in first")

    return html.P("TODO")
    #TODO
    if prompt:
        if verbose:
            print(prompt)
        try:      

            global llm
            if llm is None:
                return dbc.Alert("Please configure AI model first.", color="danger") 
            # Generate the response
            response, chat_history = invoke_llm(llm, prompt, token=token)
            if chat_history is None:
                return dbc.Alert("Please configure AI model first.", color="danger")
            if verbose:
                print(f' response {response}')
           
            # Generate the chat history for display
            chat_display = []
            for user_msg, assistant_msg in chat_history:
                chat_display.append(html.P(f"User: {user_msg}"))
                chat_display.append(dcc.Markdown(f"Assistant: {assistant_msg.replace('[', '[[').replace(']', ']]')}"))
            
            return html.Div(chat_display)
        except Exception as e:
            return html.P(f"Error: {e}")

#######################

## CONFIGURE AI MODEL

#######################

@app.callback(
    Output('config-output', 'children'),
    Input('save-config-button', 'n_clicks'),
    State('model-api-key', 'value'),
    State('model-url', 'value'),
    State('auth-token-store', 'data'),
    State('model', 'value'),
    State('temperature-slider', 'value'),
    prevent_initial_call=True
)
def save_config(n_clicks, api_key, model_url, token,model, temperature):
    #token = os.environ.get('SECRET_KEY', token)
    if api_key and model_url:
        try:
            global llm, config_llm
            #TODO
            '''
            llm, config_llm = get_agent_definition(
                api_key=api_key, 
                url=model_url, 
                model=model,
                temperature=temperature,
                token='token'
            )
            '''
            return dbc.Alert("Configuration saved successfully!", color="success")
        except Exception as e:
            return dbc.Alert(f"Error: {e}", color="danger")


@app.callback(
    Output("collapse-config", "is_open"),
    [Input("collapse-config-button", "n_clicks")],
    [State("collapse-config", "is_open")],
)
def toggle_config_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8050", dev_tools_hot_reload=False) # http://157.27.86.122:8050/