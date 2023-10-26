#!/usr/bin/env python3

import chromadb
from chromadb.config import Settings

import sys
from .. import const


def resolver(path):
    path = path.as_posix()
    if 'index' in path: return const.DOMAIN + path[path.find('docs'):path.find('index')]
    else: return const.DOMAIN + path[path.find('docs'):-3]


def index(client):
    collection = client.get_or_create_collection(const.HEAD)
    docs = list(const.DOCS_PATH.glob('**/*.md'))

    try: collection.add(documents=[open(doc, 'r').read() for doc in docs], ids=[resolver(doc) for doc in docs])
    except chromadb.errors.IDAlreadyExistsError: pass


if __name__ == '__main__':
    client = chromadb.Client(Settings(chroma_db_impl='duckdb+parquet',
                                      persist_directory=const.DB_PATH.as_posix()))
    index(client)
    sys.exit(0)
