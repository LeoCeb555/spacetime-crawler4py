from scraper import longestLength, longestURL, word_frequencies, numOfUniquePages
# I don't think we need to have this done rn, as long as our
# crawler is actually running by deployment date

# as far as this goes I thought It'd be easier to just createa a function
# that prints out everything we need

#1. Unique pages - we just have to create a list of unique urls
# and loop through the lines in analytics_data and skip empty/duplicate
# urls - DONE

#2. Loop and Compare word count of current URL to a 'longest' variable
# and if its > then just update it to the new longest one - DONE

#3. I think common words is pretty easy, we already did something similar
# in assignment 1.  - DONE

#4. Gotta do some parsing here I assume, lowkey I gotta go to work tonight
# so I'm going to leave this for later unless you want to try it rn

def makeReport():
    #Num of unique pages found
    print("Number of unique pages found: " + str(numOfUniquePages) + "\n")
    #Longest page
    print("Longest page: " + longestURL + " - " + str(longestLength) + " words\n")
    #Top 50 most common words
    print("50 most common words: ")
    print(word_frequencies.most_common(50))