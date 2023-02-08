import os
import sys

import pandas as pd
import numpy as np
#import requests
import multiprocessing as mp
from multiprocessing import freeze_support

from pandas_parallel_apply import DataFrameParallel

from crawl import Crawl
from context import context
import argparse

if __name__ == '__main__':
    freeze_support()

    parser = argparse.ArgumentParser()
    parser.add_argument('--company_name', default='삼전')
    parser.add_argument('--sort', default='date')
    args = parser.parse_args()

    print(' ### Api Call Start ###')
    cw = Crawl(client_id = "GV0sLpuZoaE73nEjOyc1", client_secret = "uD20MiNcbQ", args=args)
    result = cw(query=args.company_name, number=1000)

    print(' ### Parsering start ###')
    dfp = DataFrameParallel(result, n_cores=16, pbar=True)
    result['context'] = dfp['link'].apply(context)

    result.to_pickle(f'./crawl_set/{args.company_name}_{args.sort}.pkl')

