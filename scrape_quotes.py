from bs4 import BeautifulSoup
import requests
#pip install html5lib
#pip install requests
#pip install bs4

def generate_quotes():
    url = 'https://upperhand.com/50-motivational-workout-quotes/'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html5lib')
    div_container = soup.find('div', attrs={'class':'elementor-widget-container'})
    list_of_bq = soup.findAll('blockquote')

    # key: quote, val: author
    quotes = []
    for i in range(len(list_of_bq)):
        all_p = list_of_bq[i].findAll('p')
        # if there's no author
        if len(all_p) != 2:
            # if there is no span tag for the quote
            if all_p[0].text == None:
                quotes.append(all_p[0].span.text)
                
            # if there IS span tag for text
            else:
                quotes.append(all_p[0].text)
        else:
            # if you come across <p><span>text <author>
            if all_p[0].text == None:
                quote = all_p[0].span.text
                author = all_p[1].text
                author = author.replace('-', '')
                quotes.append(quote + ' - ' + author)
            # if <p>text <author>
            else:
                quote = all_p[0].text 
                author = all_p[1].text
                author = author.replace('-', '')
                quotes.append(quote + ' - ' + author)
        
    return quotes

if __name__ == "__main__":
    generate_quotes()