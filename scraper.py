import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup as bs
from stopWords import STOP_WORDS

# Using tokenizer logic from assignment 1
def tokenize(text):
    tokens = [] # A list to store the tokens
    current_token = ""   # Buffer to hold the characters of the current token

    for char in text:
        if char.isalnum():
            current_token += char.lower()   #Sets alphanumeric characters to lowercase
        else:      # Else triggers when the carriage hits a separator such as a space comma or newline
            if len(current_token) > 0:       # Checks if a valid word was actually constructed

                #Filter out stop words
                if current_token not in STOP_WORDS:  
                    tokens.append(current_token)  # Push back current token to the list of tokens
                current_token = ""           # Reset current token 
    
    # Check for the last token
    if len(current_token) > 0:
        if current_token not in STOP_WORDS:
            tokens.append(current_token)

    return tokens


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
    
    # Get page content for token reading
    page_text = soup.get_text() 

    tokens = tokenize(page_text) # Call tokenizer

    #####****** LEO - 
    # on your IDE run the crawler to get the analytics file since
    # I'm running my own rn and its going to keep getting modified every second
    # We'll work on writing that report function and we can use this since
    # it essentially gives us the length of the page

    #Refer to report.py 

    # Write to a new filefor analytics data
    # Displays the url, number of tokens, and the tokens themselves
    # This way we can find the url with the highest number of tokens which will give us the longest page for the report.
    # Basically it saves the stats of the page
    with open("analytics_data.txt", "a", encoding="utf-8") as f:
        f.write(f"{url}|{len(tokens)}|{' '.join(tokens)}\n")

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

        # Added the 4 URLs allowed for crawling by the assignment
        allowed_domains = [".ics.uci.edu", 
        ".cs.uci.edu", 
        ".informatics.uci.edu", 
        ".stat.uci.edu"]

        # Returns false for 'is_valid' if the netlocation (url) attempting
        # to be crawled is not in the list of allowed domains
        # This will keep the crawler from going outside of the uci specified domains
        if not any(parsed.netloc.endswith(d) for d in allowed_domains):
            return False

        # Trap protection for wiki (updated) and calendar
        # Block DokuWiki Trap
        #Ex: http://intranet.ics.uci.edu/doku.php/wiki:dokuwiki?tab_details=view&do=media&tab_files=upload&image=wiki%3Alogo.png.bak&ns=
        if "doku.php" in parsed.path:
            if "do=" in parsed.query or "tab_" in parsed.query:
                return False
        if "calendar" in parsed.hostname:
            return False
        

        # Additional trap protection

        # Block calendar/events infinite trap
        if "events" in parsed.path.lower() or "calendar" in parsed.path.lower():
            return False

        #Block dynamic calendar exports, ex: https://isg.ics.uci.edu/events/tag/talks/day/2024-10-12/?outlook-ical=1|0|
        if "ical" in parsed.query.lower():
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
