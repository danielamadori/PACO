from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from ai.prompt import examples_bpmn, define_role

def define_agent(
        url:str = '157.27.193.108', verbose = False,
        api_key = "lm-studio",
        model = 'gpt-3.5-turbo',
        temperature = 0.7
    ):  
    """
    Define the agent to be used in the chatbot.
    
    Args:
        url (str): The url of the agent.
        verbose (bool): Whether to print the output of the agent.
        api_key (str): The api key of the agent.
        model (str): The model of the agent.
        temperature (float): The temperature of the agent.
        
    Returns:
        tuple: The agent defined and the configuration.
    """
    model: ChatOpenAI = ChatOpenAI(
        base_url=url,
        temperature=temperature,
        api_key=api_key,
        model=model
    )

    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{input}"),
            ("ai", "{answer}"),
        ]
    )

    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=examples_bpmn,
    )

    final_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", define_role),
            few_shot_prompt,
            ("human", "{input}"),
        ]
    )
    if verbose:
        print(few_shot_prompt.invoke({}).to_messages())
    chain = final_prompt | model
    config = {"configurable": {"thread_id": "abc123"}}
    if verbose:
        try:
            chain.invoke(    {"input": "I have to complete the writing task before having a nature between talking with the publisher or to print the page written. Then, i choose between going to the park or continue writing"})
        except Exception as e:
            print(e)
    return chain, config