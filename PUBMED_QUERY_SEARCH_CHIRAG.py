
# coding: utf-8

# In[411]:


__title__ = 'PUBMED-Query search'
__version__ = '1.0.0'
__author__ = 'Chirag Gupta'


import unicodecsv as csv
from lxml import html
import lxml.html.clean
import requests

#making csv file to record data
csv_out = open('NeuroDis.csv', 'ab')
csv_out.truncate(0)
writer = csv.writer(csv_out, dialect='excel', delimiter=',', encoding='utf-8')

writer.writerow(['Abstract'])
#indes: serial number of result
index=0

#there are 10 results in each page, so we need to go through 10 pages to get 100 search results
i=['1','2','3','4','5','6','7','8','9','10']
for x in i:
    Search_Term = 'neurodegenerative%20diseases&page='
    Search_URL = 'https://www.ncbi.nlm.nih.gov/pubmed?term=' + Search_Term + x #To fetch more results than the default 20, add the parameter dispmax=## to the URL, e.g. https://www.ncbi.nlm.nih.gov/pubmed?term=((histone)%20AND%20chromatin)%20AND%20ESC&dispmax=100
#     print(Search_URL)
    #query to scrap search result page
    Search_Page = requests.get(Search_URL)
    Tree = html.fromstring(Search_Page.content)
    #making xpath using lxml
    Id=Tree.xpath('//meta[@name="log_displayeduids"]/@content')[0]
    #now we now all 10 ids of papers present in that page related to our search
    Ids=Id.split(",")
    for Id in Ids:
        index=index+1
        url= 'https://pubmed.ncbi.nlm.nih.gov/'+Id+'/'
#         print(Id)
        Page=requests.get(url)
        tree=html.fromstring(Page.content)
        abstracts= tree.xpath('//div[@class="article-page"]/main[@class="article-details"]/div[@class="abstract"]/div[@class="abstract-content selected"]')
        for abstract in abstracts:
            #if there are more than one headings, it will join all such lists with whitespace
            s=' '.join(abstract.text_content().split())
        if(len(abstracts)>0):    
            writer.writerow([s])
        else:
            #'N' means there is no abstract corresponding to that search
            writer.writerow(['N'])
#         print(s)
csv_out.close()


# In[412]:


#use saved data as array for further computations
import pandas as pd
data=pd.read_csv('NeuroDis.csv')


# #Print- Task 1

# In[413]:


# data.head(5)
i=0
#some abstracts are not given in the site, they are part of 100 search results but we wont print them as first 10 abstracts
while (i<10):
    if(data['Abstract'][i]!='N'):
        print(data['Abstract'][i],end='\n\n')
    else:
        print("%%Alert%%: reaseach paper corresponding to this search result dont have any abstract\n")
    i=i+1


# In[414]:


#special characters are not a word, so this step will remove comma, fullstop, etc. from the word corpus
import re
s=''
for i in range (100):
    data['Abstract'][i]=re.sub('[^A-Za-z0-9 ]+', '',data['Abstract'][i])
    if(data['Abstract'][i]!='N'):
        s=s+' '+data['Abstract'][i]
    else:
        data['Abstract'][i]=''


# In[415]:


s = re.sub('[^A-Za-z0-9 ]+', '', s)
#calculate frequency of word using nltk library
from nltk.book import FreqDist
#newlist is list of all words
newlist=s.split()
#normalize capitals- The and the are same
for i in range(len(newlist)):
    newlist[i]=newlist[i].lower()
fdist=FreqDist(newlist)
#extracting most common i.e. most frequent words
remlist=fdist.most_common(10)
# print(remlist)
rem=remlist
for i in range(0,10):
    rem[i]=remlist[i][0]
# print(rem)


# TASK 2-

# In[416]:


#this will remove frequent 10 words from whole corpus
newlist=[w for w in newlist if w.lower() not in rem]

#removal from each asbtract 
for i in range(100):
    #split string to list
    x=data['Abstract'][i].split()
    #remove
    y=[w for w in x if w.lower() not in rem]
    #list to string
    data['Abstract'][i]=' '.join(y)
#print removed words
print(rem)


# All abstract are cleansed: Free from most frequently occuring word
# Last printed values are lowercased words which are removed from the corpus

# In[417]:


# Number of dimensions of each vector is equal to number of words in whole corpus i.e len(fdist)-10


# In[418]:


#new list of words, new fdist calculation
import numpy as np
np.set_printoptions(threshold=np.inf)
#using numpy for 2D vector where each row vector is vector corresponding to an abstract
fdist=FreqDist(newlist)
fcom=fdist.most_common(len(fdist))
gcom=fcom
#gcom is list of words in whole corpus- no of words are number of components of each vector
for om in range(len(fdist)):
    gcom[om]=fcom[om][0]
# print(len(gcom))
del fdist,fcom
#vector initialization
vectors=np.zeros((100,len(gcom)))
vectors=np.int_(vectors)

#calculate frequency of each word in the given abstract
for i in range(0,100):
    x=data['Abstract'][i].split()
    for q in range(len(x)):
        x[q]=x[q].lower()
    mdist=FreqDist(x)
    com=mdist.most_common(len(mdist))
#     print(com)
    wcom=[]
    for wx in range(len(com)):
        wcom.insert(0,com[wx][0])
    q=0
    for ind in gcom:
#         print(ind,end="  ")
        w=0
        if ind in wcom:
            for w in range(0,len(com)):
                if com[w][0]==ind:
                    vectors[i][q]=com[w][1]
                    break
        else:
            #the word is not in this abstract
            vectors[i][q]=0
        q=q+1


# TASK 3- Printing first two vectors

# In[419]:


#vectors for first two rows
print(vectors[0],end="\n\n")
print(vectors[1])


# In[420]:


#norm function to help cosine similarity function
def norm(vector):
    c=0
    for i in range (len(vectors[0])):
        c=c+ (vectors[0][i])*(vectors[0][i])
    c=pow(c,0.5)
    return c


# In[421]:


#cosine similarity function
def cosine(a, b):
    #if both vectors are unequal
    for i in range(len(a)):
        if(a[i]!=b[i]):
            return (np.dot(a,b))/(norm(a)*norm(b))
    #if equal
    return 1.0


# In[422]:


#calculation of similarity matrix
sim_mat=np.zeros((100,100))
for i in range(100):
    for j in range(100):
        sim_mat[i][j]=cosine(vectors[i],vectors[j])


# In[423]:


#cluster function, calculate max similarity centroid and add itself into that cluster
def cluster():
    for i in list1:
        c=-1
        q=-1
        for j in range(len(lists)):
            d=sim_mat[i][lists[j][0]]
            if(d>c):
                c=d
                q=j
        lists[q].append(i)


# In[424]:


#new centroid calculation
def centroid():
    for i in lists:
        c=0
        for j in range(1,len(i)):
            c=c+i[j]
        c=c/(len(i)-1)
        d=200
        k=0
        for j in range(1,len(i)):
            if(abs(i[j]-c)<d):
                d=abs(i[j]-c)
                k=j
        i[0]=i[k]


# In[425]:


#check if new clusters are repeating
def check(lists,lists2):
    l1=[]
    l2=[]
    if(len(lists)!=len(lists2)):
        return 0
    for y in range(len(lists)):
        l3=[]
        l4=[]
        #first element of each list is centroid
        for z in range(1,len(lists[y])):
            l3.append(lists[y][z])
        l1.append(l3)
        for z in range(1,len(lists2[y])):
            l4.append(lists2[y][z])
        l2.append(l4)
        
    l1.sort()
    l2.sort()
    return (l1==l2)


# In[427]:


import random
#Generate 6 random numbers between 0 and 99
randomlist = random.sample(range(0, 100), 6)

lists=[]
for i in range(6):
    lists.append([randomlist[i]])

list1=range(100)
lists2=[[]]
u=0
while(u<10000):
    cluster()
#     print(lists,end="\n")
    centroid()
    c=0
    #check if clusters are same as before
    if(check(lists,lists2)):
        break
    lists2=lists
#     print(lists,end="\n\n")
    lists=[]
    for i in lists2:
        lists.append([i[0]])
    u=u+1
print("6 Clusters successfully created.\nClusters are-\n")
print(lists2)


# #every list of lists is index of abstract which lie in same cluster
# <br>Next task is to find 3 unique number corresponding to each cluster

# In[428]:


#this is done by adding all the corresponding vectors which lies in same cluster(identified from lists)
#6 vectors will come corresponding to each cluster, where ith element of the vector will tell frequency of ith word in that cluster
clus_word=[]
for i in lists2:
    c=vectors[3]
    for j in range(1,len(i)):
        c=c+vectors[i[j]]
#         print(c)
    clus_word.append(c)
tot=clus_word[0]+clus_word[2]+clus_word[3]+clus_word[4]+clus_word[5]+clus_word[1]


# In[429]:


#adding index of word to frequency which will help us during sorting
y=[]
for i in clus_word:
    x=[]
    for j in range(len(i)):
        x.append([i[j],[tot[j],j]])
    x.sort(key=lambda z:z[1][0])
    x.sort()
    y.append(x)
#sorted such that if less frquency in cluster- comes first, same frequency in cluster- one with less frequency in corpus comes first


# TASK 5:

# In[430]:


for i in range(len(y)):
    j=0
    while(j<len(y[i])):
        if(y[i][j][0]>0):
            break
        j=j+1
    if(j==len(y[i])):
        print("Cluster ",i+1,": No unique number, all vectors in this cluster are 0 i.e Abstracts corresponding to this cluster are absent",end="\n")
    else:
        print("Cluster ",i+1,": Most unique numbers are-",gcom[j],", ",gcom[j+1]," and ",gcom[j+2],end="\n")

