# import all dependencies
import requests
import pymongo
import pandas as pd
from bs4 import BeautifulSoup as bs
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo

def init_browser():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    return Browser('chrome', **executable_path, headless=False)
def scrape():
    browser=init_browser()
    mars_dict={}
    
    ### Mars News

    # URL of page to be scraped
    url = 'http://redplanetscience.com/'
    browser.visit(url)
    html = browser.html
    soup = bs(html, 'html.parser')

    # scrape for news title and paragraph text
    news_title = soup.find_all('div', class_ = 'content_title')[0].text
    news_p = soup.find_all('div', class_ = 'article_teaser_body')[0].text

    ### JPL Mars Space Images - Featured Image

    url = 'https://spaceimages-mars.com'
    browser.visit(url)
    html = browser.html
    soup = bs(html, 'html.parser')
    
    # scrape for featured image url
    featured_image_tag = soup.find('img', class_ = 'headerimage fade-in')
    featured_image_tag = featured_image_tag.attrs['src']
    featured_image_url = f'{url}/{featured_image_tag}'


    ### Mars Facts

    url = 'https://galaxyfacts-mars.com'
    facts = pd.read_html(url)
    
    fact_table_df = facts[1]
    fact_table_df = fact_table_df.rename(columns={0:"Profile",1:"Value"},errors="raise")
    fact_table_df.set_index("Profile",inplace=True)
    
    # convert pandas df to html string
    html_fact_table = fact_table_df.to_html()
    html_fact_table.replace('\n','')
    
    ### Mars Hemispheres

    # Scrape Mars hemisphere title and image
    usgs_url='https://astrogeology.usgs.gov'
    url='https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    html=browser.html
    soup=bs(html,'html.parser')

    # Extract hemispheres item elements
    mars_hems=soup.find('div',class_='collapsible results')
    mars_item=mars_hems.find_all('div',class_='item')
    hemisphere_image_urls=[]

    # Loop through each hemisphere item
    for item in mars_item:
        # Error handling
        try:
            # Extract title
            hem=item.find('div',class_='description')
            title=hem.h3.text
            
            # Extract image url
            hem_url=hem.a['href']
            browser.visit(usgs_url+hem_url)
            html=browser.html
            soup=bs(html,'html.parser')
            image_src=soup.find('li').a['href']
            if (title and image_src):
                # Print results
                print('-'*50)
                print(title)
                print(image_src)
            # Create dictionary for title and url
            hem_dict={
                'title':title,
                'image_url':image_src
            }
            hemisphere_image_urls.append(hem_dict)
        except Exception as e:
            print(e)

    # Create dictionary for all info scraped from sources above
    mars_dict={
        "news_title":news_title,
        "news_p":news_p,
        "featured_image_url":featured_image_url,
        "fact_table":fact_table,
        "hemisphere_images":hemisphere_image_urls
    }
    # Close the browser after scraping
    browser.quit()
    return mars_dict