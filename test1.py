import pickle
from pathlib import Path
import streamlit_authenticator as stauth
import tweepy
import config
import streamlit as st
from googletrans import Translator, LANGUAGES
from textblob import TextBlob
import pandas as pd
import altair as alt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime

# User Uthentication
names = ["Raihan Azka", "Thomas Muller"]
usernames = ["likethis777", "tMuller"]

#load hashed passwords
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    "sales_dashboard", "abcdef", cookie_expiry_days=30)

name, authenticator_status, username = authenticator.login("Login", "main")

if authenticator_status == False :
    st.error("Username or Password is wrong")
    
if authenticator_status == None:
    st.warning("Please enter your username and password")
    
if authenticator_status:  


    def main():
        #variable
        client = tweepy.Client(bearer_token=config.BEARER_TOKEN)
        translator = Translator()
        
        st.title("Tweet Sentiment Analysis NLP App")
        st.write("A website that will analyze the word from twitter")

        menu = ["Home","About"]
        choice = st.sidebar.selectbox("Menu", menu)
        authenticator.logout("Logout", "sidebar")
        st.sidebar.title(f"Welcome {name}")

        if choice == "Home":
            st.subheader("Home")
            with st.form("nlpForm"):
                keyword = st.text_input("Insert Keyword")
                tweet_count = st.number_input('Insert tweet count: ', 10,100)
                submit_button = st.form_submit_button(label='Analyze')

                if submit_button:
                    data = client.search_recent_tweets(query=keyword, max_results=tweet_count, tweet_fields=['created_at', 'lang'], expansions= ['author_id'])
                    users = {u['id']: u for u in data.includes['users']}
                    text = []
                    created_at = []
                    username = []
                    translated = []
                    sentiment_data = []
                    
                    for tweet in data.data:
                            user = users[tweet.author_id]
                            kalimat = str(tweet.text)
                            final_text=translator.translate(kalimat, dest='en')
                            final = str(final_text.text)
                            sentiment = TextBlob(final).sentiment
                            
                            if sentiment.polarity > 0:
                                result = "Positive 😊 "
                            elif sentiment.polarity < 0:
                                result = "Negative 😡 "
                            else:
                                result = "Neutral 😐 "
                            
                            
                            token_sentimen = anlyze_token_sentiment(final)
                            clock = datetime.strftime(tweet.created_at, '%d/%m/%y %H:%M:%S')
                            #memasukan hasil ke array
                            text.append(tweet.text)
                            translated.append(final)
                            created_at.append(clock)
                            username.append(user.username)
                            sentiment_data.append(result)

                    
                    #dataframe        
                    tweet_dict = {"Tweet":text, "Created at":created_at, "Username":username, "Translated": translated, "Sentiment": sentiment_data}
                    df = pd.DataFrame(tweet_dict,columns=["Username","Sentiment","Tweet","Translated","Created at"])
                    st.title('Result')
                    df                    

    def convert_to_df(data):
        tweet_dict = {"text" : data.text, "created_at": data.created_at, "username": data.username}
        df = pd.DataFrame(tweet_dict, columns=["username", "text", "created at"])
        return df

    def anlyze_token_sentiment(docx):
        analyzer = SentimentIntensityAnalyzer()
        pos_list = []
        neg_list = []
        neu_list = []
        for i in docx.split():
            res = analyzer.polarity_scores(i)['compound']
            if res > 0.1:
                pos_list.append(i)
                pos_list.append(res)

            if res <= -0.1:
                neg_list.append(i)
                neg_list.append(res)

            else:
                neu_list.append(i)

        result = {'positives':pos_list,'negtives':neg_list,'neutral':neu_list}
        return result
                                
    if __name__ == '__main__':
        main()