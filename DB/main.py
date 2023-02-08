from typing import Optional
from enum import Enum
from fastapi import FastAPI

from Database.elastic_db import ElasticDB

import pickle

app = FastAPI()
DI = ElasticDB()

class IndexName(str, Enum):
    bigkinds_new2 = "bigkinds_new2"
    all_journal_newsdataset = "all_journal_newsdataset"


class IndexField(str, Enum):
    title = "title"
    titleNdescription = "titleNdescription"
    context = "context"


@app.get("/")
async def root():
    return {"message": "Financial News dataset server"}


@app.get("/search/{query_sentence}")
def search_news(
    query_sentence: str,
    date_gte: Optional[int] = None,
    date_lte: Optional[int] = None,
    topk: Optional[int] = 9999,
):

    query_result = DI.search(
        query_sentence=query_sentence, date_gte=date_gte, date_lte=date_lte, topk=topk
    )

    return query_result["hits"]["hits"]


@app.get("/new_search/{query_sentence}")
def new_search_news(
    query_sentence: str,
    index_name: IndexName,
    field: IndexField,
    date_gte: Optional[int] = None,
    date_lte: Optional[int] = None,
    topk: Optional[int] = 9999,
):

    query_result = DI.new_search(
        query_sentence=query_sentence,
        field=field,
        date_gte=date_gte,
        date_lte=date_lte,
        topk=topk,
        index_name=index_name,
    )

    return query_result["hits"]["hits"]
