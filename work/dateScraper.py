#!/usr/bin/env python
# coding: utf-8

# In[22]:


from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from datetime import timedelta, date
import sys


# ## All library invoke(s) 

# In[23]:


base_link = "https://thegreyhoundrecorder.com.au/results/search/"

#html_file_name = link_date + ".html"


# In[24]:


links=list()


# ## URL connection functions 

# In[25]:


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


# ## Function for each Date. The link-date is a global variable 

# In[26]:


def date_execute():
    
    link  = base_link+link_date+'/' #Creation of link
    raw_html = simple_get(link) #Connection complete
    
    
    html = BeautifulSoup(raw_html, 'html.parser')
    
    
    race_date = html.find('h2').decode_contents()
    
    print(race_date) #Progress tracking output statements
    print(len(raw_html))
    print(len(html))
    
    
    
    result_div = html.findAll("div", {"class": "resultsTblWrap"})
    #print(result_div)
    anchors = result_div[0].findAll('a') #selecting all the race hyperlinks

    i=0
    links.append(link_date)
    while (i < len(anchors)):
        #print((anchors[i]['href']))
        s=anchors[i]['href']
        links.append(s) #adding them to a global list
        i=i+1
        
    
    
    


# ## library function to traverse through all possible dates 

# In[27]:




def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

start_date = date(2016, 1, 1)
end_date = date(2016, 2, 1) # Feb 1 2016 is the sop-date
for single_date in daterange(start_date, end_date):
    link_date=single_date.strftime("%Y-%m-%d")
    #print(link_date)
    date_execute() #Calling day-wise function to execute


# ## Check out the outcome 

# In[28]:


print("\n".join(links))


# ## storing the entire list into a file

# In[29]:


with open('datefile.txt', 'w') as filehandle:
    filehandle.writelines("%s\n" % place for place in links)


# ### ignore | code snippet to redirect system-output to text file 
import sys

orig_stdout = sys.stdout
f = open(html_file_name, 'w')
sys.stdout = f

print(html)

sys.stdout = orig_stdout
f.close()