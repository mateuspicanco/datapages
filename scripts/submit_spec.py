import sys
import os
import json
from elasticsearch import Elasticsearch

if __name__ == "__main__":
    with open(sys.argv[1], 'r') as spec_file:
        specs = json.load(spec_file)

    es = Elasticsearch(os.environ['ELASTIC_CLUSTER'])
    response = es.index(index=os.environ['DIRECTORY'], id=specs['spec_id'], body=specs)
    if (response['_shards']['successful'] > 0):
        print(f"Specification with id {specs['spec_id']} was successfully submitted")

    else:
        raise ValueError(f"Specification with id {specs['spec_id']} could not be submitted, with response: {response}")

