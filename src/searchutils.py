# -*- coding: utf-8 -*-
"""
Utility classes for handling search and results from Elasticsearch queries
"""

import unicodedata
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
import eland as ed
import streamlit as st

class Searcher:
    """Base class for all search-oriented objects. 
    Handles queries and search results from Elasticsearch full-text operations

    Args: 
        es_client (elasticsearch.client.Elasticsearch): client handler for Elasticsearch from low-level client
        cluster_location (str): string reference to cluster connection. Ex: http://somecluster@password:9200/
        index_reference (str): index pattern reference for the search, defaulting to "directory"

    Attributes:
        es_client (elasticsearch.client.Elasticsearch): active client connection for interfacing queries
        cluster_location (str): used in Eland-based queries
        index_reference (str): index in which searches will be performed
    """
    def __init__(self, es_client, cluster_location, index_reference="directory"):
        self.es_client = es_client
        self.cluster_location = cluster_location
        self.index_reference = index_reference

    def process_input_text(self, input_text):
        """Normalizes text inputs from the search elements and stores in processed_text attribute.
        Normalization includes the following steps:

        1. Removes accents and substitutes for ascii version
        2. Removes non-ascii characters

        Args: 
            input_text (str): input text to search widgets 
        
        Returns:
            None -> adds processed_text as an attribute to the Searcher object

        """
        processed_text = str(unicodedata.normalize('NFKD', input_text).encode('ASCII', 'ignore'), 'utf-8')
        self.processed_text = processed_text


    def search_data_directory(self):
        """Performs configured search in the specified index (directory)
        Args:
            None
        
        Returns:
            search_results (list): list of "hits" (dictionary result from search) containing all search results

        Note:
            For very large indices, this is not a good solution, since it performs pagination on the index. Might result in long queries.

        """
        search_statement = Search(using=self.es_client, index=self.index_reference)

        # scan search results through pagination - by default it scans the ENTIRE index, this should now be used for very large queries
        st.spinner('Processing your request...')
        search_results = [hit.to_dict() for hit in search_statement.query(self.query_structure).scan()]
        return search_results


class SourceFinder(Searcher):
    """Extendes Searcher object with Eland query functionality

    Args: 
        es_client (elasticsearch.client.Elasticsearch): client handler for Elasticsearch from low-level client
        cluster_location (str): string reference to cluster connection. Ex: http://somecluster@password:9200/
        index_reference (str): index pattern reference for the search, defaulting to "directory"
    
    Attributes:
        es_client (elasticsearch.client.Elasticsearch): active client connection for interfacing queries
        cluster_location (str): used in Eland-based queries
        index_reference (str): index in which searches will be performed
    
    """
    def __init__(self, es_client, cluster_location, index_reference):
        Searcher.__init__(self, es_client, cluster_location, index_reference)


    def get_index_data(self):
        """Retrieves all data in an index as a Eland dataframe

        Args:
            None -> expects index reference to be made during initialization. This is to avoid retrieving data from incorrect that does not match defined search.

        Returns:
            None -> resulting Eland dataframe reference is stored in "source" parameter.
        """
        df = ed.DataFrame(self.cluster_location, self.index_reference)
        self.source = df

class MultiMatchSearcher(Searcher):
    """Extends Searcher object with Multi Match search functionality

    Args: 
        es_client (elasticsearch.client.Elasticsearch): client handler for Elasticsearch from low-level client
        cluster_location (str): string reference to cluster connection. Ex: http://somecluster@password:9200/
        index_reference (str): index pattern reference for the search, defaulting to "directory"
    
    Attributes:
        es_client (elasticsearch.client.Elasticsearch): active client connection for interfacing queries
        cluster_location (str): used in Eland-based queries
        index_reference (str): index in which searches will be performed

    """
    def __init__(self, es_client, cluster_location, index_reference):
        Searcher.__init__(self, es_client, cluster_location, index_reference)


    def build_query_object(self, search_input, target_field=('description', 'title'), boosting_param=2):
        """Associates search element object to the direct Elasticsearch query correspondence.

        Used for building Multi Match query structures in two disting fields.

        Args:
            search_input (str): input text from search bar or widget
            target_field (tuple): fields that will be used for search, only supporting two distinct fields. Boosting is by default applied to the first element of the tuple input.
            boosting_param (int): boosting parameter for Multi Match search. Refers to how many times a field is more relevant to the search than the other field in the tuple input.
        
        Returns:
            None -> query structure is stored within Searcher object
        """
        self.process_input_text(search_input)

        # Building multi_match query structure
        query_structure = Q({
            "multi_match" : {
                "query": self.processed_text,
                "fields": [f'{target_field[0]}^{str(boosting_param)}', f'{target_field[1]}'] # by default the first field is boosted
            }
        })

        self.query_structure = query_structure


class MatchSearcher(Searcher):
    """

    Args:
        search_input (str): input text from search bar or widget
        target_field (tuple): fields that will be used for search, using just the first field. No boosting is applied to such field.
        boosting_param (int): boosting parameter for Multi Match search. Refers to how many times a field is more relevant to the search than the other field in the tuple input.
        
    Returns:
        None -> query structure is stored within Searcher object

    """
    def __init__(self, es_client, cluster_location, index_reference):
        Searcher.__init__(self, es_client, cluster_location, index_reference)


    def build_query_object(self, search_input, target_field=('description'), fuzziness_param=1):
        """Associates search element object to the direct Elasticsearch query correspondence.

        Used for building simple Match query structures targeting only one field. 
        
        Args:
            search_input (str): input text from search bar or widget
            target_field (tuple): fields that will be used for search, only supporting two distinct fields. Boosting is by default applied to the first element of the tuple input.
            fuzziness_param (int): represents the degree to which the edit distance for a specific search input will be considered, used for handling typos. Defaults to 1, for up to 5 characters.

        Returns:
            None -> query structure is stored within Searcher object
        """
        self.process_input_text(search_input)

        query_structure = Q({
            "match" : {
                target_field[0] : {
                    "query": self.processed_text,
                    "fuziness": fuzziness_param, 
                    "max expansions": 100
                }
            }
        })

        self.query_structure = query_structure
