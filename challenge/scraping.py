# import dependencies
from bs4.builder import TreeBuilderRegistry
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    #Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    # Set variables to capture results from mars_news
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": hemispheres(browser)
    }
    
    #Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object
    html = browser.html
    news_soup = soup(html, 'html.parser')

    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').text
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').text

    except AttributeError:
        return None, None

    # Use the return function to store the news title and paragraph
    return news_title, news_p

#### Featured Images

def featured_image(browser):

    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)
    
    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()


    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url


# ### Table Data Scrape
def mars_facts():
    try:
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None

    df.columns=['Description','Mars','Earth']
    df.set_index('Description', inplace=True)

    return df.to_html(classes="table table-striped")

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())

### Hemisphere image and title scrape
def hemispheres(browser):
    # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    html = browser.html
    hemisphere_soup = soup(html, 'html.parser')

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    ## 3a. Create a list that contains the title/image content for each of the 4 products on the page
    container = hemisphere_soup.find('div', class_='collapsible results')
    urls = container.find_all('div', class_='item')

    ## 3b. Loop through the list to scrape the specific data points into a dictionary which is added to the list created earlier
    try:
        for url in range(len(urls)):
            browser.find_by_css('a.product-item img')[url].click()
            sample_elem = browser.links.find_by_text('Sample').first
            img_url = sample_elem['href']
            title = browser.find_by_css("h2.title").text
            hemisphere_image_urls.append ({"img_url": img_url,
                                                "title": title})
            browser.back()
    except AttributeError:
        return None
    
    return hemisphere_image_urls
    