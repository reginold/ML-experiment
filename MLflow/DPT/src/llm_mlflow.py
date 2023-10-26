from src.chat.converse import Client
from src import const

import mlflow
import openai

bot=Client()
db=bot.db
db

db.count() ## This gets the number of records in the VectorDB

def _prompt(documents,prompt):

    if 'before_documents' in prompt:
        before_doc=prompt['before_documents']

    else:
        before_doc=""
    if "after_documents" in prompt:
        after_doc=prompt['after_documents']
    else:
        after_doc=""

    final_prompt=before_doc + \
                '\n'.join([''.join(section) for section in [document for document in documents]]) \
                + after_doc
    #print("PROMPT ",final_prompt)
    return final_prompt


from typing import List,Dict

def generate_prompt(input):
    documents=input['documents']
    prompt=input['prompt']
    if "n_results" in input:
        top_k=input['n_results']
    else:
        top_k=10
    context_length=input['context_length']
    prompts=_prompt(documents['documents'][0][:top_k],prompt)[:context_length]
    messages=[{'role': 'system', 'content': prompts},{'role': 'user', 'content': input['query']}]
    return messages,prompts

PROMPT = {
    'before_documents': (
        'You are a chatbot assistant answering technical questions about DagsHub, an MLOps platform. '
        'You can only respond to a question if the content necessary to answer the question is contained in the following provided documentation. '
        'If the answer is in the documentation, summarize it in a helpful way to the user. '
        'If it isn\'t, simply reply that you cannot answer the question. '
        'Do not refer to the documentation directly, but use the instructions provided within it to answer questions. '
        'Here is the documentation: '
        '<DOCUMENTS> '
    ),
    'after_documents': (
        '<\\DOCUMENTS>\n'
        'REMEMBER:\n'
        'Here are the rules you must follow:\n'
        '1) You must only respond with information contained in the documentation above. Say you do not know if the information is not provided.\n'
        '2) Make sure to format your answers in Markdown format, including code block and snippets.\n'
        '3) Do not include any links, urls or hyperlinks in your answers.\n'
        '4) If you do not know the answer to a question, or if it is completely irrelevant to the library usage, simply reply with:\n'
        '5) Do not refer to the documentation directly, but use the instructions provided within it to answer questions. '
        '"I\'m sorry, but I am an AI language model trained to assist with questions related to the DagsHub library. I cannot answer that question as it is not relevant to the library or its usage. Is there anything else I can assist you with?"'
    ),
}

def generate_input(query,prompt_format,n_results=10,context_length=16385):

    inputs={}
    inputs['query']=query
    inputs['documents']=db.query(query_texts=query,n_results=n_results)
    inputs['prompt']=prompt_format
    inputs['n_results']=n_results
    inputs['context_length']=context_length

    return str(inputs)

from ast import literal_eval

def chat_completion_dagshub(inputs):

    inputs=literal_eval(inputs)
    message,prompt=generate_prompt(inputs)
    completion = openai.ChatCompletion.create(
                model=const.MODEL,
                messages=message
            )


    if "n_results" in inputs:
        top_k=inputs['n_results']
    else:
        top_k=10




    outputs=(inputs,completion.choices[0].message.content,message)

    return outputs


import pandas as pd
def chat_completion(inputs):

    outputs=[]

    print(type(inputs))
    if type(inputs)==str:

        output=chat_completion_dagshub(inputs)

        #print(output)
        return output



    if isinstance(inputs, pd.DataFrame):
        ###  This is to handle mlflow.evaluate function
        print(inputs.columns)


        input_list=inputs['input'].tolist()
        for input in input_list:
            output=chat_completion_dagshub(input)
            final_output={}
            final_output['output']=output[1]
            final_output['n_results']=output[0]['n_results']
            final_output['prompt_message']=output[2]
            outputs.append(str(final_output))
        return outputs

    else:
        for input in inputs:
            output=chat_completion_dagshub(input)
            outputs.append(output)
        print(len(outputs))

        return outputs
    
tracking_uri = "http://localhost:5000/"
mlflow.set_tracking_uri(tracking_uri)

with mlflow.start_run(nested=True,run_name="llm_dagshub_model") as run:
    mlflow.pyfunc.log_model(
    artifact_path="model",
    python_model=chat_completion,
    pip_requirements=["openai"],registered_model_name="mlflow-llm-openai-dagshub")



    mlflow.log_params({'n_results':5,'context_length':8192,'llm_model':const.MODEL})
    print("Running Queries")
    queries=["What is the benefit of using DDA?","i am having problem regarding activation  i am not able to activate my account from past 1 week"]
    input_list=[]
    for query in queries:
        inputs=generate_input(query,PROMPT,5)
        input_list.append(inputs)

    output=chat_completion(input_list)

    prompts=[out[2] for out in output]
    target=[out[1] for out in output]



    mlflow.llm.log_predictions(queries,target,prompts)



