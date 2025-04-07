import emoji
from wordcloud import WordCloud, STOPWORDS
import pandas as pd
from urlextract import URLExtract
from collections import Counter
extract = URLExtract()

def fetch_stats(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    num_messages = df.shape[0]

    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]    #fetch no. of media messages

    words = []
    links=[]
    for message in df['message']:
        words.extend(message.split())   #fetch no. of words shared
        links.extend(extract.find_urls(message))    #fetch no. of links shared
        emojis = df['message'].apply(lambda x: len([c for c in x if c in emoji.EMOJI_DATA])).sum()   #fetch no. of emojis shared
        stickers = df[df['message'].str.contains('sticker')].shape[0]    #fetch no. of stickers shared
    
    return num_messages, len(words), num_media_messages, len(links), emojis, stickers

def most_active_users(df):
    x = df['user'].value_counts().head(5)    #fetch top 5 active users
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(columns={'user': 'name', 'count': 'percent'})
    return x, df

def create_wordcloud(selected_user, df):    #wordcloud
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    stopwords = set(STOPWORDS)
    stopwords.update(['Media', 'omitted', 'https', 'added', 'left', 'group_notification'])  # Add words to exclude
    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white', stopwords=stopwords)
    wc = wc.generate(df['message'].str.cat(sep=' '))
    return wc

def emoji_helper(selected_user, df):    #emoji analysis
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])
    emoji_df = pd.DataFrame(Counter(emojis).most_common(10))
    emoji_df.columns = ['Emoji', 'Count']
    return emoji_df

def monthly_timeline(selected_user, df):    #monthly timeline
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    monthly_timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    time = []
    for i in range(monthly_timeline.shape[0]):
        time.append(monthly_timeline['month'][i] + '-' + str(monthly_timeline['year'][i]))
    monthly_timeline['time'] = time
    return monthly_timeline

def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    daily_timeline = df.groupby('only_date').size().reset_index(name='message')  # Count messages per day
    return daily_timeline

def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['day_name'].value_counts()  # Count messages per day of the week

def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['month'].value_counts()  # Count messages per month

def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
    return heatmap  # Create a pivot table for heatmap