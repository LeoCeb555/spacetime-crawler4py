from scraper import longestLength, longestURL, word_frequencies, unique_urls, numOfUniquePagesPerSubDomain

def makeReport():
    #Num of unique pages found
    print("Number of unique pages found: " + str(len(unique_urls)) + "\n")
    #Longest page
    print("Longest page: " + longestURL + " - " + str(longestLength) + " words\n")
    #Top 50 most common words
    print("50 most common words: ")
    for word, freq in word_frequencies.most_common(50):
        print(f"{word}: {freq}")
    #Number of subdomains and unique pages per subdomain
    print("Number of subdomains:", len(numOfUniquePagesPerSubDomain))
    print("Number of unique pages per subdomain:\n")
    for subdomain in sorted(numOfUniquePagesPerSubDomain):
        print(f"{subdomain}, {numOfUniquePagesPerSubDomain[subdomain]}")