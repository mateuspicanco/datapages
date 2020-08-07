# A Search engine for Data Self-service

![](streamlit_search_engine_demo_full.gif)

This project is a **proof of concept** of a search engine with full-text search capabilities for the exploration of company data for non-technical users. It aims to illustrate a way to foster data-driven decision making without the interface of technical teams, a concept known as [data self-service](https://devops.com/how-to-implement-a-data-self-service-program/). It was inspired by an existing product from [Looqbox](https://www.looqbox.com/), a Brazilian startup.

In its design, **Data Pages** consists of a guided access to data and analysis previously made available by technical teams as specifications in a data directory (hence the Index reference). The search engine capabilities provide for a cleaner interface to find relevant data about the company, without requiring browsing through a long list of available information.

## Business motivation

Businesses are more likely to thrive when informed decisions are made and having the necessary data in hand at any time a decision needs to be made makes them more efficient. However, it is not always easy at a big company to allow its employees to find information for specific use cases. 

Let's imagine you are a part of the marketing team and are working on a project that needs the information of who are your best customers so you can make them a special offer. Where would you find that? How many people do you think you would have to talk to under normal circumstances to get the data you want? How long do you think that endeavor would take? In many big, bureaucratic companies, this is not a trivial task.

In such settings, when an organization has mature data management systems, the concept of Data self-service becomes a lot more relevant. With a self-service platform available, employees would be able easily check relevant information, improving time-to-market in a variety of scenarios. Access to the comprehensive, curated information about your company can also improve the effectiveness of business decisions, mitigating inappropriate offers from the marketing department, for example.

To implement such a Self-service system, though, is not easy. There needs to be the right kinds of abstractions so that non-technical users can effectively find the information they are looking for. That's where the idea of a search engine can help us.

Search engines have very simple interfaces. They inquiry the user to express themselves in what they are looking for and are one of the most familiar tools in the words, since most people had contact with products like Google or Bing at least once. Data Pages tries to bridge this gap of available information and being able to get to this information faster by mirroring the experience of search engines in a data analytics setting. 

## About the data
All the data currently being used for this project was found in [Brazillian E-commerce Public Dataset](https://www.kaggle.com/olistbr/brazilian-ecommerce?select=olist_order_items_dataset.csv), made public by [Olist](https://olist.com/), a marketplace aggregator company from Brazil. The dataset provides several kinds of information available in the dataset. Some of these are related to orders, locations of sellers and customers, product categories, amongst others. Please note that Olist itself anonymized all the data they collected for this dataset. I made changes to this data by changing hashed seller ids with randomly generated company names using [Faker](https://github.com/joke2k/faker), so that results would look more meaningful on the app.

## Technical considerations

This project relies heavily on two technologies:

1. **Elasticsearch** as a search engine backend for performing full-text queries on the data directory;
2. **Streamlit** to build the web app and UI components and processing data in-memory;

Elasticsearch here can be understood as a serving-layer component, effectively providing a data store that can be accessed through the full-text search features. Due to the NoSQL and document-based structure of Elasticsearch, I decided to store records representing what would be a "flat table" in relational databases, where every row represents an unnormalized transaction.

That leads to a big number of unique documents that might differ very little from each other. Even though this design is not ideal, it still avoids trying to use Elasticsearch as a relational database, which would lead to unnecessary complexity and very inefficient querying.

For the version of this app deployed on [Heroku](https://datapages.herokuapp.com/), however, to keep costs low, I did not use Elasticsearch as the data store itself. Because Bonsai's free tier Elasticsearch cluster only allows 10k records, I would not be able to store the entire Olist dataset. With this in mind, the dataset is stored as in **feather** format locally for demo purposes. This repo contains the original implementation of this project, using Elasticsearch as the data store as well as the search directory.

## Setting up the application locally:
If you want to try this app out by yourself on your own environment and play around with your own visualizations and data, here are a few things you need to set it up:

### Set up a virtual environment
```bash
# create a virtual environment using the requirements.txt file provided
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Set up Elasticsearch
Depending on where you are running your elasticsearch cluster, you need setup the correct environment variables

```bash
# setting up environment variables for the project:
export ELASTIC_CLUSTER="url-to-your-elasticsearch-cluster" 
export DIRECTORY = "name-of-your-directory-index-pattern"
```

I also provided the exact dataset I used (with the modifications) for download [here](https://drive.google.com/file/d/1D3bp4oKOME98TrWa74_GDu_eyfGVSCPT/view?usp=sharing). To bootstrap your Elasticsearch cluster, you can use the utility script `bootstrap_elasticsearch` I provided in the `scripts` folders. 

```bash
# running bootstrapper:
python bootstrap_elasticsearch.py path/to/dataset.csv target-index-name
```

### Using specification template
I provided several specifications I used as examples for the app, but these require that you use the same dataset I used for the project. To make your own specifications, please follow through the `spec_template.json` file provided in the `specs` folder. 

To submit your specification to Elasticsearch, you can simply use the Dev Tools console and make a POST request. You can also use the utility script `submit_spec.py` if you find it more convenient.

```bash
# in the Dev Tools console in Kibana:
POST your-directory-index-pattern/_doc/your-specification-id
{
    ... your spec goes here
}

# alternatively, using the python script:
python submit_spec.py path/to/your/spec.json
```

## Lessons learned with this project

- Good visualization abstractions are **REALLY HARD** to make. Think about this whenever you curse `matplotlib` and be grateful about the work that has been put into it;
- Vega plots (Vega-lite, altair) provide a really expressive syntax, even though content about it is a bit scarce outside the official documentation;
- Vega-based plots are quite powerful and fit perfectly with Elasticsearch. In fact, this project relies heavily on the ability to store a previously described visualization in the database itself. To the best of my knowledge, I haven't seen any kind of database for visualizations and this idea itself has a lot of potential;

## To-dos and project roadmap:
- [ ] Scale the proof of concept to more than one full dataset;
- [ ] Implement visualizations with more than two dimensions;
- [ ] Implement time-based interactivity for datasets that are time-oriented;
- [ ] Figure out a way to make more specific data transformations entirely on vega specs instead of pandas;
- [ ] Improve abstractions for the data visualization object;
- [ ] Implement clickable search results in lieu to Streamlit's selectbox; <sup>[1](#clickable)</sup>
- [ ] Improve search with semantic features;


## Footnotes:
- <a name="clickable"><b>1</b></a>: This is currently not supported by Streamlit, since non-widget elements still do not interact with the backend;