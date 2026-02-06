import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup as bs

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    harvested_links = []

    # if the status code is some other number than 200
    # or the program was unable to find the page, return an empty list 
    # This indicates there was some kind of error
    if resp.status != 200 or not resp.raw_response: 
        return []

    # Convert the content of the page to a beautiful soup object
    soup = bs(resp.raw_response.content, "lxml")
    
    # Find anchor tags and gets href for hyperlink
    for link in soup.find_all('a'):
        href = link.get('href')
        
        #Defragmentation
        if href:
            clean_href = href.split('#')[0]

            # Joins the relative links to the full url and appends to the list of links
            full_url = urljoin(url, clean_href)
            harvested_links.append(full_url)

    return harvested_links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        allowed_domains = [".ics.uci.edu", 
        ".cs.uci.edu", 
        ".informatics.uci.edu", 
        ".stat.uci.edu"]

        # Returns false for 'is_valid' if the netlocation (url) attempting
        # to be crawled is not in the list of allowed domains
        # This will keep the crawler from going outside of the uci specified domains
        if not any(parsed.netloc.endswith(d) for d in allowed_domains):
            return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
