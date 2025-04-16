import requests

from src.env import URL_SERVER, HEADERS


def get_agent_definition(
    url: str, api_key: str,
    model: str, temperature: float = 0.7,token = None
    ):
    data = {
        'url': url,
        'api_key': api_key,
        'model': model,
        'temperature':temperature,
        'token': 'token'
    }
    agent_definition = requests.get(
        f'{URL_SERVER}agent-definition',
        params=data,
        headers=HEADERS,
    )
    if agent_definition.status_code == 200:
        llm = agent_definition.json()['llm']
        config = agent_definition.json()['config']
        return llm, config
    return None, None


def invoke_llm(llm, prompt, token= None):
    ag = requests.post(
        f'{URL_SERVER}invoke-agent',
        json={'llm': llm, 'prompt': prompt},
        params={'token': token},
        headers=HEADERS,
    )
    if ag.status_code == 200:
        return ag.json()['response'], list(ag.json()['history'])
    return None, None
