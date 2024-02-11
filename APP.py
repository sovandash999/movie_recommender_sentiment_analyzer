import streamlit as st
import pickle as pkl
import pandas as pd
import requests
from bs4 import BeautifulSoup
import requests
import nltk
from nltk.tokenize import word_tokenize,sent_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.probability import FreqDist
from nltk.corpus import stopwords
import string
import re

nltk.download('punkt')
nltk.download('vader_lexicon')
nltk.download('stopwords')
stop_words=set(stopwords.words('english'))


movies1=pkl.load(open('movies.pkl','rb'))
movies=pd.DataFrame(movies1)
similarity=pkl.load(open('similarity.pkl','rb'))


def get_poster(movie_id):
    api_key = '499d6df71f5b7e2273d9de859e153278'

    url=f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&append_to_response=images'
    response=requests.get(url)
    if response.status_code==200:
        movie_data=response.json()
        image1=movie_data.get('poster_path')
        return 'http://image.tmdb.org/t/p/w185'+image1


def recommend(a):
    index=movies[movies['title']==a].index[0]
    #movie_id=movies[movies['title']==a]['movie_id'][0]
    x = (-similarity[index]).argsort()[1:10]
    movie_name = []
    movie_image=[]
    for i in x:
        movie_id = movies.iloc[i]['movie_id']
        movie_name.append(movies.iloc[i]['title'])
        movie_image.append(get_poster(movie_id))
    return movie_name,movie_image


def get_imdb_reviews(movie_id,number_of_reviews=25):
    reviews1 = []
    url = f'https://www.imdb.com/title/{movie_id}/reviews?sort=totalVotes&dir=desc&ratingFilter=0'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    review_divs = soup.find_all('div', class_='text show-more__control')

    for i in review_divs:
        if i.text.strip() not in reviews1:
            reviews1.append(i.text.strip())
            if len(reviews1) == number_of_reviews:
                break

    # ajax_url=f'https://www.imdb.com/title/{movie_id}/reviews/_ajax?sort=totalVotes&dir=desc&ratingFilter=0'
    # response=requests.get(ajax_url)
    # soup=BeautifulSoup(response.text,'html.parser')

    while len(reviews1) < 100:
        load_more_divs = soup.find('div', class_='load-more-data')
        data_key = load_more_divs['data-key']
        if data_key:
            load_more_url = f"https://www.imdb.com/title/{movie_id}/reviews/_ajax?sort=totalVotes&dir=desc&ratingFilter=0&ref_=undefined&paginationKey={data_key}"
            ajax_response = requests.get(load_more_url)
            soup = BeautifulSoup(ajax_response.text, 'html.parser')
            review_divs = soup.find_all('div', class_='text show-more__control')
            for i in review_divs:
                reviews1.append(i.text.strip())
    return list(reviews1)



def movie_sentiments(movie_name):
    movie_id = get_imdb_id(movie_name)
    review_result = get_imdb_reviews(movie_id)
    all_reviews = ' '.join(review_result)
    sid = SentimentIntensityAnalyzer()
    polarity_scores=sid.polarity_scores(all_reviews)
    review_without_punctuation = all_reviews.translate(str.maketrans("", "", string.punctuation))
    words = word_tokenize(review_without_punctuation)
    no_stop_words = [word for word in words if word.lower() not in stop_words]
    only_words = ' '.join(no_stop_words)
    tokenized_words = word_tokenize(only_words)
    fdist = FreqDist(tokenized_words)
    most_common_words=fdist.most_common(20)
    positive_words_count = 0
    negative_words_count = 0
    for word in tokenized_words:
        if sid.polarity_scores(word)['compound'] < 0:
            negative_words_count += 1
        elif sid.polarity_scores(word)['compound'] > 0:
            positive_words_count += 1
    positive_review=0
    negative_review=0
    for i in review_result:
        compound_score=sid.polarity_scores(i)['compound']
        if compound_score>0:
            positive_review+=1
        else:
            negative_review+=1
    total_words = len(tokenized_words)


    return polarity_scores,positive_review,negative_review,fdist,total_words,positive_words_count,negative_words_count,review_result

def sentiment_analysis_page():
    st.write('this is the page')


def get_imdb_id(movie_name):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    search_query=movie_name.replace(' ','+')
    search_url = f'https://www.imdb.com/find?q={search_query}&s=tt&ttype=ft&ref_=fn_ft'
    response=requests.get(search_url,headers=headers)
    if response:
        soup=BeautifulSoup(response.text,'html.parser')
        result=soup.find('a',class_='ipc-metadata-list-summary-item__t')
        text=result['href']
        imdb_movie_id=re.search(r'/title/(tt\d+)/',text)[1]
    return imdb_movie_id

#if 'movie_name' not in st.session_state:
 #   st.session_state.movie_name = ''
#if 'sentiment_result' not in st.session_state:
 #   st.session_state.sentiment_result = ''

st.title('MOVIE RECOMMENDER')
selected_movie_name=st.selectbox('movie selector',movies['title'].values)
#if st.button('recommend'):
movies,poster=recommend(selected_movie_name)
col1,col2,col3=st.columns(3)
for idx,(movie,movie_poster) in enumerate(zip(movies,poster)):
    column=col1 if movies.index(movie)%3==0 else (col2 if movies.index(movie)%3==1 else col3)


    with column:
        st.image(movie_poster,use_column_width='auto',caption=movie)
        if st.button('analyze',key=f'analyze_movie_{idx}'):
            st.session_state.movie_name=movie
            st.session_state.poster = movie_poster
            st.session_state.movie_sent=movie_sentiments(movie)
            st.switch_page('pages/analysis_page.py')
