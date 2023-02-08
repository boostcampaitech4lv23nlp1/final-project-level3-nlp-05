import json

import pandas as pd
from tqdm import tqdm

from elasticsearch import Elasticsearch
from elasticsearch import helpers

import warnings

warnings.filterwarnings(action="ignore")


class ElasticDB:
    """Elasticsearch is used as a database for news search

    Attributes:
        self.es (Elasticsearch) : Elasticsearch instance
        self.index_name (str) : index name of news dataset repository
        self.setting_path (str) : Path of Elastic Search settings.json file

    Returns:
        None
    """

    def __init__(self):

        self.es = Elasticsearch(
            "http://localhost:9200",
            request_timeout=30,
            max_retries=10,
            retry_on_timeout=True,
        )
        self.setting_path = "./config/setting.json"

    def check_index(self, index_name):
        """Checking index whether index_name exists

        when self.index_name exists do nothing and return True
        when self.index_name does not exist create one and return True if successful
        when something go wrong return False

        Args:

        Returns:
            True if successful, False otherwise.

        """

        try:
            if not self.es.indices.exists(index=index_name):
                self._create_index(index_name)
            return True
        except Exception:
            return False

    def _create_index(self, index_name):
        """Creating an index in Elasticsearch

        create an index based on self.index_name args

        """

        if self.es.indices.exists(index=index_name):
            self.es.indices.delete(index=index_name)

        with open(self.setting_path, "r") as f:
            setting = json.load(f)

        self.es.indices.create(index=index_name, body=setting)

        print(f"{index_name} index has been successfully created")

    def insert(self, df):

        """Checking index whether index_name exists

        This is deprecated

        when self.index_name exists do nothing and return True
        when self.index_name does not exist create one and return True if successful
        when something go wrong return False

        Args:

        Returns:
            True if successful, False otherwise.

        """

        for each in tqdm(df.iterrows()):

            try:
                doc = {
                    "title": each[1]["제목"],
                    "description": each[1]["본문"],
                    "titleNdescription": " ".join([each[1]["제목"], each[1]["본문"]]),
                    "context": each[1]["context"],
                    "URL": each[1]["URL"],
                    "date": each[1]["일자"],
                }
                self.es.index(index=self.index_name, body=doc)

            except Exception:
                pass

    def search(
        self,
        query_sentence,
        date_gte=20230115,
        date_lte=20230116,
        topk=9999,
        index_name="bigkinds_newsdata",
    ):
        """
        This is deprecated
        """

        self.index_name = index_name

        query_doc = {
            "bool": {
                "must": [
                    {"match": {"titleNdescription": query_sentence}},
                    {
                        "range": {
                            "date": {
                                "gte": date_gte,
                                "lte": date_lte,
                            }
                        }
                    },
                ]
            },
        }

        res = self.es.search(index=self.index_name, query=query_doc, size=topk)

        return res

    def new_search(
        self,
        query_sentence,
        field,
        date_gte=20230115,
        date_lte=20230116,
        topk=9999,
        index_name="bigkinds_newsdata",
    ):

        self.index_name = index_name

        query_doc = {
            "bool": {
                "must": [
                    {"match": {field: query_sentence}},
                    {
                        "range": {
                            "date": {
                                "gte": date_gte,
                                "lte": date_lte,
                            }
                        }
                    },
                ]
            },
        }

        res = self.es.search(index=self.index_name, query=query_doc, size=topk)

        return res

    def return_maxdate(self, index_name):

        query_doc = {
            "size": 0,
            "aggs": {
                "doc_with_max_run_id": {
                    "top_hits": {"sort": [{"date": {"order": "desc"}}], "size": 1}
                }
            },
        }

        res = self.es.search(index=index_name, body=query_doc)

        # fmt : off
        return res["aggregations"]["doc_with_max_run_id"]["hits"]["hits"][0]["_source"][
            "date"
        ]

    def count(self, index_name):

        response = self.es.count(index=index_name)
        return response

    def get_alias(self):
        response = self.es.indices.get("*")
        return response

    def delete(self, index_name):

        try:
            self.es.indices.delete(index=index_name)
            return True
        except Exception:
            print("No index_name to delete")

    def bulk_insert(self, index_name, df):

        self.check_index(index_name)

        docs = [
            {
                "_index": index_name,
                "_type": "_doc",
                "_source": {
                    "title": x[0],
                    "titleNdescription": " ".join([x[0], x[1]]),
                    "context": x[2],
                    "URL": x[3],
                    "date": x[4],
                    "category1": x[5],
                    "category2": x[6],
                },
            }
            for x in zip(
                df["제목"],
                df["본문"],
                df["context"],
                df["URL"],
                df["일자"],
                df["category1"],
                df["category2"],
            )
        ]

        try:
            helpers.bulk(self.es, docs)
            return True
        except Exception:
            return False


if __name__ == "__main__":

    import os
    from pandas_parallel_apply import DataFrameParallel

    from preprocess import Preprocess
    from context import context

    prepro = Preprocess()
    es = ElasticDB()

    dir_list = os.listdir("./Dataset")

    # Collect News data file in Dataset folder
    full_df = pd.DataFrame()
    for each in tqdm(dir_list):
        if each.endswith(".xlsx"):
            tmp_df = pd.read_excel(
                f"./Dataset/{each}", usecols=["제목", "본문", "URL", "일자", "통합 분류1"]
            )
            full_df = pd.concat([full_df, tmp_df])

    full_df = full_df.loc[~full_df["URL"].isna()]
    full_df = full_df.reset_index(drop=True)

    # check url
    def url_check(x):
        """
        Check whether each item in URL column is a completed item

        Returns:
            wwww.google.com => http://www.google.com
        """
        http_str = ("http://", "https://")
        if not x.startswith(http_str):
            return "http://" + x
        else:
            return x

    full_df["URL"] = full_df["URL"].apply(url_check)

    # parallelize dataframe
    dfp = DataFrameParallel(full_df, n_cores=16, pbar=True)

    # crawl news data using newspaper3k library
    full_df["context"] = dfp["URL"].apply(context)
    # preprocesssing context, title, description
    full_df["context"] = dfp.apply(lambda x: prepro(x["제목"], x["context"]), axis=1)
    full_df["제목"] = dfp["제목"].apply(prepro.title_preprocess)
    full_df["본문"] = dfp["본문"].apply(prepro.title_preprocess)

    # Category split function
    def category1(x):
        """
        Splite 통합 분류1 column into Larget category and Subcategory

        ex) if input is 경제>증시, return 경제

        Returns:
            return string if input is not None else return None
        """
        try:
            x = x.split(">")
            return x[0]
        except Exception:
            return None

    def category2(x):
        """
        Splite 통합 분류1 column into Larget category and Subcategory

        ex) if input is 경제>증시, return 증시

        Returns:
            return string if input is not None else return None
        """
        try:
            x = x.split(">")
            return x[1]
        except Exception:
            return None

    # Apply category function
    full_df["category1"] = full_df["통합 분류1"].apply(category1)
    full_df["category2"] = full_df["통합 분류1"].apply(category2)

    # Insert data into a index in elasticsearch
    es.bulk_insert(index_name="bigkinds_new2", df=full_df)

    print(" @@@ Data Insert has been done successfully @@@")

    # Removed used xlsx files
    for each in dir_list:
        if each.endswith(".xlsx"):
            os.remove(f"./Dataset/{each}")

    print(" @@@ xlsx files successfully removed @@@ ")
