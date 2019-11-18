#!/usr/bin/env python
# coding: utf-8

# ## Routine declarations 

# In[25]:


from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from datetime import timedelta, date
import sys
import pandas as pd
import time


def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)
    
add_link = "bulli/2033"
race_date = "11-11-1111"


col = ['date','race_name','race_number','race_place', 'rug', 'dog_name', 'dog_trainer', 'time', 'mgn', 'split', 'inRun', 'wgt', 'sire', 'dam', 'sp']
all_data = pd.DataFrame([],columns=col)


# ## Function to scrape from the internet race_name-wise

# In[26]:


def race_scrape():
    base_link = "https://thegreyhoundrecorder.com.au/results/"

    race_name = add_link
    link = base_link+add_link
    print(link)

    raw_html = simple_get(link) #Connection complete
    print(len(raw_html))

    html = BeautifulSoup(raw_html, 'html.parser')

    html_file_name='race.html'
    orig_stdout = sys.stdout
    f = open(html_file_name, 'w')
    sys.stdout = f

    print(html.prettify())

    sys.stdout = orig_stdout
    f.close()





    raceContent = html.findAll('div',{"class": "resultsDesktopContent tabs"})[0]

    raceTable = raceContent.findAll('table')
    no_of_races = int(len(raceTable)/2)
    #print(no_of_races)


    i=0 # race iterator
    while(i<no_of_races):

        # ##printing the unique race header

        raceHeader = raceTable[2*i]
        raceHeader = raceHeader.findAll('td')
        #print(len(raceHeader))

        raceNumber = raceHeader[0].decode_contents()
        raceSubName = raceHeader[1].decode_contents()
        raceLength = raceHeader[2].decode_contents()
        raceHeaderCategory = raceHeader[3].decode_contents()

        raceBets = raceHeader[4].decode_contents()
        raceBets = raceBets.replace(' ','')
        raceBets = raceBets[:(raceBets.rfind('-')+1)]+raceBets[raceBets.rfind('$'):] #output formating

        raceSplits = raceHeader[5].decode_contents()
        #print(raceNumber+raceSubName+raceLength+raceHeaderCategory+raceBets+raceSplits)

        #raceHeader is not included in the CSV at the moment
        
        raceBody = raceTable[2*i+1]
        raceBody = raceBody.find('tbody')
        rows = raceBody.findAll('tr')
        no_of_rows = len(rows)

        #printing the rest of the table

        j = 0 #row iterator
        while(j<no_of_rows):
            current_row = rows[j].findAll('td')

            #print(current_row)

            race_place = current_row[0].decode_contents()
            rug = current_row[1].decode_contents()
            dog_name = current_row[2].find('a')['href'][12:]
            dog_trainer = current_row[3].find('a')['href'][10:]
            
            if(race_place!='SCR'): 
                time = current_row[4].decode_contents()
                mgn = current_row[5].decode_contents()
                split = current_row[6].decode_contents()
                inRun = current_row[7].decode_contents()
                wgt = current_row[8].decode_contents()
                sire = current_row[9].find('a')['href'][12:]
                dam = current_row[10].find('a')['href'][12:]
                sp = current_row[11].find('p').decode_contents()[2:]
                
            else: #if its SCR all these contents do not exist
                time = 'blank'
                mgn = 'blank'
                split = 'blank'
                inRun = 'blank'
                wgt = 'blank'
                sire = 'blank'
                dam = 'blank'
                sp = 'blank'

            #print(race_place+' '+rug+' '+dog_name+' '+dog_trainer+' '+time+' '+mgn+' '+split+' '+inRun+' '+wgt+' '+sire+' '+dam+' '+sp)

            df2 = pd.DataFrame([[race_date, race_name, (i+1), race_place, rug, dog_name, dog_trainer, time, mgn, split, inRun, wgt, sire, dam, sp]],columns=col)
            global all_data # to prevent local creation
            all_data = all_data.append(df2) #appending the table row
            j=j+1
        i=i+1
    


# In[27]:


print(all_data) # to check if the df is created properly and has no prior content on it


# ### fetching the date-list 

# In[28]:


dateFile = pd.read_csv('date.csv') 
print(dateFile)


# ## All-date iterator 

# In[30]:


t = time.process_time() # keeping a track of time

len_of_date = len(dateFile)
k=0
while(k<len_of_date): #iterate among all the dates in the dateFile
    print(dateFile.iloc[k,0])
    if(dateFile.iloc[k,0].find('/')==-1): #if the line is a date or a link
        race_date = dateFile.iloc[k,0] 
    else:
        add_link = dateFile.iloc[k,0]
        race_scrape()
    k=k+1
    
    
elapsed_time = time.process_time() - t


# ### storing to CSV

# In[ ]:


all_data.to_csv('january_2016.csv',index=False)


# In[33]:


print(all_data)


# ## Total number of minutes it took 

# In[36]:


print(elapsed_time/60) # amount of time it took for all of this calculation


# In[ ]:




