# -*- coding: utf-8 -*-
"""
A Data Self-Service search engine based on Streamlit and Elasticsearch with full-text search capabilities.
Author: Mateus Picanco
github: https://github.com/mateuspicanco
"""

# Data processing imports
import os
import streamlit as st
import pandas as pd
import eland as ed
from elasticsearch import Elasticsearch

# custom classes and components
from components import ResultList, Download, Visualizer
from searchutils import MultiMatchSearcher

@st.cache(suppress_st_warning=True)
def load_dataset(target_index):
    """Loads data from Elasticsearch data store

    Args:
        target_index (str): index pattern to load data from

    Returns:
        pandas.DataFrame: dataframe containing the dataset
    """
    ed_df = ed.read_es(os.environ['ELASTIC_CLUSTER'], target_index)
    return ed.eland_to_pandas(ed_df)

def main():
    """Executes the web app logic within Streamlit

    Called when the program starts

    Args:
        None

    Returns:
        None

    """
    st.title('Data Index :mag_right:')

    st.markdown(
        '''
        [Data Pages](https://github.com/mateuspicanco/datapages) is a **proof of concept** for a **Data Self-Service** search engine.
        You can use it to explore the [Olist Dataset](https://www.kaggle.com/olistbr/brazilian-ecommerce?select=olist_order_items_dataset.csv) interactively.
        Use the search bar below and start exploring Olist orders, sellers and other kinds of data available. Here are a few suggestions for you to try out:
        - Top sellers
        - Most sold product categories
        - Volume of orders over time
        '''
    )

    # instantiate objects clients and search objects
    es_client = Elasticsearch(os.environ['ELASTIC_CLUSTER'])

    # decided to user the multi match search while boosting description
    searcher = MultiMatchSearcher(es_client, os.environ['ELASTIC_CLUSTER'], os.environ['DIRECTORY'])

    # loading the dataset from Elasticsearch data store
    df = load_dataset(os.environ['DATA_INDEX'])


    search_bar = st.text_input('What kind of information are you looking for?', key='SearchBar')

    # Check if search bar received a text input
    if(search_bar):
        # by default, the specs used took the "description" and "title" fields for search
        searcher.build_query_object(search_bar, ('description', 'title'))
        hits = searcher.search_data_directory()

        # get the ResultsList object to output the search results
        result_list = ResultList(hits)

        # establishing a limit for search results for the proof of concept (decided on 5 records)
        search_limit = 5

        if(len(hits) != 0):
            st.write(f'Your search for **{search_bar}** returned **{len(hits)}** result(s)')
            if(len(hits) > search_limit):
                st.info(f'Showing only the first {limit} results for **{search_bar}**')

            result_list.display_search_results(limit=search_limit)

            # retrieving references for the results so that the vega specs can be called back
            references = result_list.get_index_references(search_limit)
            results_bar = st.selectbox(label='Please choose what data source would like to explore',
                                    options=list(references.keys()),
                                    key='ResultsBar')

            if(results_bar):
                # getting the spec reference
                plot_ref = references[results_bar]
                st.spinner('Processing your request...')
                st.write(f'Please select one of the analysis available')

                # # generating visualizations
                plot_type = plot_ref['instructions']['type']

                # Visualizer takes the data and the spec
                visualizer = Visualizer(df, plot_ref)
                visualizer.display_visualization(limit=10)

                # # generating the download links from the resulting visualization
                download_link = Download(visualizer.output)
                download_link.get_download_link()

        else:
            st.warning(f'Your search for **{search_bar}** did not return any results')


if __name__ == "__main__":
    main()
