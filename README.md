# Web Plagiarism Checker

> This is a code to scrap abstracts of many research papers(100 most relavant) given query to search.
> Date:13-10-2020

The includes query searching and clustering documents on the basis of their similarity
  - Scrape abstracts from the first 100 search results for the query “neurodegenerative diseases” on pubmed
  - Remove 10 most frequently occurring words in this corpus from each abstract to create a “cleansed” corpus
  - Represent each abstract as a vector. The components of the vector should be the frequency of occurrence of a word within an abstract 
  - Use the cosine similarity between the 100 vectors as a metric to cluster them into exactly six clusters
  - Find most unique words in each cluster

### Approach 

I have written the code in Jupyter Notebook. Steps invloved are:
  - Scrapping abstracts
  - Data preparation: Remove mostly used words, remove characters/elemets which are not words
  - Representation of text data into vectors of frequency i.e word to frequency
  - KNN algorithm using cosine similarity

### Scraping

- used request library to request website data
- Used lxml to create xpaths of texts required
- loop 10 pages for query search(10 search results in a page: 10*10=100)
- find xpath of all 10 results (document id of 10 papers) in a page
- call query to pubmed using document id
- find xpath of abstrat
- scrap text of each absract

### Data cleaning and preparation

- Save text as columns in a csv file(this step is unnecesaary but it will reduce call to query each time we change modeling approach)
- Use pandas to extract data of csv file
- Remove unwanted characters
- Used FreqDist from nltk library to calculate frquency matrix of words
- Removed most frequent 10 words from all subsets
- Created list of words instead of string

### Vector Transformation

- Number of dimensions of each vector is equal to number of words in whole corpus i.e len(fdist)-10
- Used numpy for 2D vector where each row vector is vector corresponding to an abstract
- Check if i^th word is there in each abstract, if yes ith component of that vector is frequency, else 0

### KNN Algorithm

##### Similarity Matrix
- 100*100 matrix with each entry(i,j) as cosine similarity of ith and jth vector 
- Cosine similarity= dot(a,b)/(norm(a)*norm(b))

##### Clustering Algorithm
- Randomly select k data points for initial k centroids 
- Calculate cosine similarity between each data point and each centroid. 
- Assign each data point to the cluster with which it has the highest cosine similarity.
- Calculate the average of each cluster to get new centroids
- Repeat until no data point changes clusters, the cluster centroids fail to change, or a maximum number of iterations is reached.

### Code

Code is saved as PUBMED_QUERY_SEARCH_ABHAY.ipynb. It is properly commented, so go through the code to know more details about how each function workd.
