import os
import pandas as pd
import eland as ed

if __name__ == "__main__":
    file_path = sys.argv[1]
    target_index_name = sys.argv[2]
    df = pd.read_csv(file_path)
    es = Elasticsearch(os.environ['ELASTIC_CLUSTER'])

    ed_input = ed.pandas_to_eland(
        pd_df=df,
        es_client=es,

        # Where the data will live in Elasticsearch
        es_dest_index=target_index_name,

        # If the index already exists what should we do?
        es_if_exists="replace",

        # Wait for data to be indexed before returning
        es_refresh=True
    )