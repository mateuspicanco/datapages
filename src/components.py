# -*- coding: utf-8 -*-
"""
Custom components for displaying information in a specific way in Streamlit
"""

# data processing imports
import base64
import numpy as np
import pandas as pd

# streamlit
import streamlit as st

class Download:
    """Download URL handler for providing download functionality to Streamlit page

    Args: 
        dataframe (pandas.DataFrame): data that will be used for generating the results for download

    Attributes:
        dataframe (pandas.DataFrame): data attribute that will be converted into base64 file for download

    """
    def __init__(self, dataframe):
        self.dataframe = dataframe

    def get_csv_data(self):
        """Simple wrappper on top of pandas.DataFrame.to_csv() with previously specified parameters

        Args:
            None
        
        Returns:
            None -> csv data is stored inside "data" attribute
        """
        self.data = self.dataframe.to_csv(index=False)

    def get_download_link(self):
        """Generates a download clickable link containing the data processed by the Download object

        Args:
            None
        
        Returns:
            streamlit html ref: resulting html element on page with clickable href

        """
        self.get_csv_data()

        # encodes data for download in the browser
        self.download_object = base64.b64encode(self.data.encode()).decode()

        # builds the html object 
        href = f'Click <i><a href="data:file/csv;base64,{self.download_object}" download="analysis.csv">here</a></i> to download the data for your search.'
        return st.write(href, unsafe_allow_html=True)

class ResultList:
    """List aggregator for search results display in Streamlit pages

    Args: 
        search_results (list): list of "hits" expected from search results from Elasticsearch query

    Attributes:
        results (list): list of dictionaries containing the json-like objects from search results

    """
    def __init__(self, search_results):
        self.results = search_results

    def get_result_url(self):
        """Builds list of results as html components in the Streamlit page

        Args:
            None

        Returns:
            None -> search result html components are stored in responses attribute
        """
        responses = []
        for result in self.results:
            title = result['title']
            description = result['description']
            response = f"""
            <h4>&#128193{title}</h4>
            <p>{description}</p>
            """
            responses.append(response)
        self.responses = responses

    def get_index_references(self, limit=5):
        """Retrieves index references from search results 
        This is expected from the spec itself. Changing spec structure would require a change in this method.

        Args:
            limit (int): number of records kept from search as limit. Defaults to 5.
            Note: since Streamlit does allow for multiple page apps now, limit has to be kept low for usability of the interface. 

        Returns:
            references (dict): dictionary of title referenced to vega spec from the directory index. Check the specs folder for examples.
        """
        references = {}
        for record in self.results[:limit]:
            references[record['title']] = record
        return references

    def display_search_results(self, limit=5):
        """Method for displaying search results as streamlit html components

        Args:
            limit (int): number of records kept from search as limit. Defaults to 5.

        Returns:
            None -> builds Streamlit components on the page
        """
        self.get_result_url()
        for response in self.responses[:limit]:
            st.write(response, unsafe_allow_html=True)
    
class Visualizer:
    """Visualization handler for interface with the Directory index and Vega-lite specs

    Args:
        data (pandas.DataFrame): original dataset that will be used to generate "views" given vega-lite specs.
        definition (dict): json-like object from directory search results 
    
    Attributes:
        data (pandas.DataFrame): dataset that will be used to create views for visualizations
        definition (dict): raw json-like object from search
        instructions (dict): json-like object from raw definition isolating just the instruction set for building the visualization
        specs (dict): json-link object with explicit vega-lite specs

    """
    def __init__(self, data, definition):
        self.data = data
        self.definition = definition
        self.instructions = self.definition['instructions']
        self.specs = self.definition['specs']

    def build_handle(self):
        """Defines an aggreagtion handle based on the type of plot requested in the instruction set

        Args:
            None -> logic is entirely contained within the instruction set

        Returns:
            None -> output is stored in self.handle object

        """

        # make a copy of the data to avoid self-referencing
        data = self.data[self.instructions['dimensions']].copy()

        # get the type of plot being requested
        report_type = self.instructions['type']

        # check if plot type is time-based (timeseries, data that is associated with time objects)
        if(report_type == 'timeseries'):
            time_field = self.instructions['time_field']
            time_unit = self.instructions['time_unit']

            # converts time field to pandas DateTime object
            data[time_field] = pd.to_datetime(data[time_field])
            data = data.set_index(time_field)

            # Check each unit for resampling 
            if(time_unit == 'month'):
                data_handle = data.resample('1M')
                self.handle = data_handle

            elif(time_unit == 'day'):
                data_handle = data.resample('1d')
                self.handle = data_handle
            else:
                raise TypeError(f"{time_unit} is not a valid time unit")

        # If report is not timeseries (category)
        elif(report_type == 'category'):
            cat_field = self.instructions['cat_field']

            # group by target category
            data_handle = data.groupby(cat_field)
            self.handle = data_handle
        else:
            raise TypeError(f"Instruction set{self.instruction} given is not valid, check for plot types or dimensions")

    def make_aggregation(self, limit=10):
        """Builds the aggregation from the previously defined handles
        Args: 
            limit (int): limits the number of output data points to not overcrowd the visualization -> useful for categorical data with high cardinality

        Returns:
            None -> generates output attribute containing the aggregated data in the expected format for vega-lite plotting 
        """
        op = self.instructions['agg_operation']
        sort = False
        if(self.instructions['type'] == 'category'):
            sort = True
        if(op == 'count'):
            if(sort):
                self.output = self.handle.aggregate(len).reset_index().sort_values(by=self.instructions['agg_field'], ascending=False).reset_index(drop=True).head(limit)
            else:
                self.output = self.handle.aggregate(len).reset_index()
        elif(op == 'sum'):
            if(sort):
                self.output = self.handle.aggregate(np.sum).reset_index().sort_values(by=self.instructions['agg_field'], ascending=False).reset_index(drop=True).head(limit)
            else:
                self.output = self.handle.aggregate(np.sum).reset_index()
        elif(op == 'mean'):
            if(sort):
                self.output = self.handle.aggregate(np.mean).reset_index().sort_values(by=self.instructions['agg_field'], ascending=False).reset_index(drop=True).head(limit)
            else:
                self.output = self.handle.aggregate(np.mean).reset_index()
        elif(op == 'median'):
            if(sort):
                self.output = self.handle.aggregate(np.median).reset_index().sort_values(by=self.instructions['agg_field'], ascending=False).reset_index(drop=True).head(limit)
            else:
                self.output = self.handle.aggregate(np.median).reset_index()
        else:
            raise NotImplementedError('{op} operation is not supported')

    def display_visualization(self, limit=10):
        """Builds and displays Vega-lite visualizations in streamlit pages

        Args:
            limit (int): limits the number of output data points to not overcrowd the visualization -> useful for categorical data with high cardinality

        Returns:
            streamlit vega_lite chart: vega-lite chart object with the given specifications

        """
        self.build_handle()
        self.make_aggregation(limit)
        return st.vega_lite_chart(self.output, self.specs)
