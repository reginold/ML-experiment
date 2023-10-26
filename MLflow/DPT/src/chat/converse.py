#!/usr/bin/env python3

import os
import openai
import chromadb
from dotenv import load_dotenv
from chromadb.config import Settings

from .. import const
from .index import index


class Client:
    def __init__(self):
        client = chromadb.Client(Settings(chroma_db_impl='duckdb+parquet',
                                          persist_directory=const.DB_PATH.as_posix()))
        if const.HEAD not in [c.name for c in client.list_collections()]: index(client)
        self.db = client.get_collection(const.HEAD)

        load_dotenv()
        openai.api_type = os.environ['OPENAI_API_TYPE']
        openai.api_key = os.environ['OPENAI_API_KEY']
        openai.api_base = os.environ['OPENAI_API_BASE']
        openai.api_version = os.environ['OPENAI_API_VERSION']

    def _prompt(self, documents):
        return const.PROMPT['before_documents'] + \
                '\n'.join(['\n'.join(section) for section in [document for document in documents]]) \
                + const.PROMPT['after_documents']

    def _sources(self, sources):
        formatted = '\n\n\N{MEMO} Here are the sources I used to answer your question:\n'
        for idx, source in enumerate(sources):
            formatted += f'{idx+1}. <{source}>\n'
        return formatted

    def result(self, query):
        documents = self.db.query(query_texts=query)

        return openai.ChatCompletion.create(deployment_id=const.MODEL,
                                            messages=[{'role': 'system', 'content': self._prompt(documents['documents'][0][:const.TOP_K])[:8192]},
                                                      {'role': 'user', 'content': query}]).choices[0].message.content + self._sources(documents['ids'][0][:const.TOP_K])


# For testing
if __name__ == '__main__':
    client = Client()

    while True:
        print(client.result(input('Input: ')))
