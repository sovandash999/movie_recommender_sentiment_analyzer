import random
import matplotlib.pyplot as plt
import streamlit as st
from nltk.sentiment import SentimentIntensityAnalyzer
from wordcloud import WordCloud


st.title('SENTIMENT ANALYZER')
st.subheader('REVIEWS')

st.image(st.session_state.poster)
st.write(st.session_state.movie_name)
polarity_scores,positive_review,negative_review,fdist,word_count,positive_words_count,negative_words_count,review_results=st.session_state.movie_sent

sid=SentimentIntensityAnalyzer()

#if polarity_scores

c1,c2,c3=st.columns(3)

with c1:
    st.subheader('1')
    st.subheader('positive sentiment' if sid.polarity_scores(review_results[0])['compound']>0 else('negative sentiment' if sid.polarity_scores(review_results[0])['compound']<0 else 'neutral sentiment'))
    st.write(review_results[0][:500]+'...')

with c2:
    st.subheader('2')
    st.subheader('positive sentiment' if sid.polarity_scores(review_results[2])['compound']>0 else('negative sentiment' if sid.polarity_scores(review_results[2])['compound']<0 else 'neutral sentiment'))
    st.write(review_results[2][:500]+'...')

with c3:
    st.subheader('3')
    st.subheader('positive sentiment' if sid.polarity_scores(review_results[4])['compound']>0 else('negative sentiment' if sid.polarity_scores(review_results[4])['compound']<0 else 'neutral sentiment'))
    st.write(review_results[4][:500] + '...')


st.subheader('For the top 100 reviews:')
st.write(f'out of the {word_count} unique words.There are {positive_words_count} positive words, {negative_words_count} negative words and the rest are neutral.')

col1,col2=st.columns(2)
labels1=['positive word count','negative word count','neutral word count']
sizes1=[positive_words_count,negative_words_count,negative_words_count]
with col1:
    fig1,ax1=plt.subplots()
    ax1.pie(sizes1,labels=labels1,autopct='%1.1f%%')
    ax1.axis('equal')
    ax1.set_title('word count')
    st.pyplot(fig1)

labels=['positive reviews','negative reviews']
sizes=[positive_review,negative_review]
with col2:
    fig,ax=plt.subplots()
    ax.pie(sizes,labels=labels,autopct='%1.1f%%')
    ax.axis('equal')
    ax.set_title('review count')
    st.pyplot(fig)

st.subheader(f"Overall sentiment of all the reviews: {'positive' if polarity_scores['compound']>0 else('negative' if polarity_scores['compound']<0 else 'neutral')}")



st.subheader('Most common words:')
fig, ax = plt.subplots()
wordcloud = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(fdist)
ax.imshow(wordcloud, interpolation='bilinear')
ax.axis("off")
st.pyplot(fig)
