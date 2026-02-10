import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup as bs
from stopWords import STOP_WORDS
from collections import Counter

longestURL = "" #tracks the name of the page with the most words
longestLength = 0 #tracks the word amount of the longest page
word_frequencies = Counter() #tracks word frequences
unique_urls = set() #tracks the urls already found, works with subdomain counter
numOfUniquePagesPerSubDomain = Counter() #tracks number of unique pages per unique subdomain
analytics_buffer = [] #analytics_data buffer

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

#Saves analytics all at once at the end of crawl
def save_analytics(filename="analytics_data.txt"):
    with open(filename, "a", encoding="utf-8") as f: #append to analytics data
        f.write("\n".join(analytics_buffer) + "\n")
    analytics_buffer.clear() #clear the buffer

def extract_next_links(url, resp):
    #Lets function know these are global variables
    global longestURL, longestLength, word_frequencies, unique_urls, numOfUniquePagesPerSubDomain, analytics_buffer
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!

    # Set tracks unique hyperlinks (as strings) scrapped from resp.raw_response.content
    harvested_links = set()

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
    word_frequencies.update(tokens) #Add page's tokens to word counts

    # Write to a new filefor analytics data
    # Displays the url, number of tokens, and the tokens themselves
    # This way we can find the url with the highest number of tokens which will give us the longest page for the report.
    # Basically it saves the stats of the page
    
    # If buffer reaches 150 pages
    if len(analytics_buffer) >= 150:
        save_analytics() #write the data to the file

    # Add to url to analytics buffer
    analytics_buffer.append(f"{url}|{len(tokens)}|{' '.join(tokens)}")
    
    #if url has not been found yet, adds it to found urls and updates unique page counter for this url
    temp = url.split("#")[0].rstrip("/").lower() #ensure defragmentation, remove trailing slash, set to lowercase

    if temp not in unique_urls:
        unique_urls.add(temp)
        parsed = urlparse(temp) #seperates url into sections
        hostname = parsed.hostname  # drops the port if present
        if hostname and hostname.startswith("www."): #checks for www. and bad urls
            hostname = hostname[4:]  # drop the first 4 characters
        numOfUniquePagesPerSubDomain[hostname] += 1 #increment count for subdomain

    #Checks if url has more words than current longest
    if len(tokens) > longestLength:
        longestURL = url
        longestLength = len(tokens)

    # Find anchor tags and gets href for hyperlink
    for link in soup.find_all('a'):
        href = link.get('href')
        
        #Defragmentation
        if href:
            clean_href = href.split('#')[0]

            # Joins the relative links to the full url and add to the set of links
            full_url = urljoin(url, clean_href)
            harvested_links.add(full_url)

    return list(harvested_links)

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
            # Block actions (do=), revisions (tab_), and sitemaps (idx=)
            if any(x in parsed.query for x in ["do=", "tab_", "idx="]):
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

        #Block large galleries
        if "eppstein" in parsed.path.lower() or "/pix/" in parsed.path.lower():
            return False

        # More trap protection, this time for dynamic gitlab urls
        #Ex: https://gitlab.ics.uci.edu/joshug4/heros/-/commit/663aa65db524c27f85c3cdbc4e5f7c8dad0a37d8?view=parallel|64|
        if "gitlab.ics.uci.edu" in parsed.netloc and parsed.query:
            return False
        
        # Blocks pages that are just re-sorting the same content
        if any(x in parsed.query for x in ["sort=", "filter=", "limit=", "order="]):
            return False

        #Block grape/wiki trap
        if "grape.ics.uci.edu" in parsed.netloc:
            # Block timeline (infinite calendar)
            if "timeline" in parsed.path:
                return False
            # Block attachments
            if "attachment" in parsed.path:
                return False
            # Block history/diffs/specific versions
            if any(x in parsed.query for x in ["action=", "version=", "format="]):
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
