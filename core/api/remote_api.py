import base64
import aiohttp
import requests

from core.config import URL_SERVER

headers = {
    "Content-Type": "application/json",
}

########################
# LLM - AI
########################
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
        headers=headers,
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
        headers=headers,
    )
    if ag.status_code == 200:
        return ag.json()['response'], list(ag.json()['history'])
    return None, None

########################
# AUTHORIZATION FUNCTION
########################
async def authorization_function(username = '', password = '', server = None):
    """
    Authenticate user and store token
    Returns: Tuple[bool, Optional[str]] - (is_authorized, token)
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{URL_SERVER}login",
                json={"username": username, "password": password},
                headers=headers,
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    token = data.get('token')
                    if token:
                        return True, token, server.config.update(
                                                SECRET_KEY=token,
                                                SESSION_TYPE='filesystem',
                                                SESSION_FILE_DIR='flask_session'
                                            )
        return False, None
    except Exception as e:
        print(f"Auth error: {e}")
        return False, None
    


