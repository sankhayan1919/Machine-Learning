import emoji
from wordcloud import WordCloud, STOPWORDS
from urlextract import URLExtract
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
    stopwords.update(['Media', 'omitted', 'https'])  # Add words to exclude
    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white', stopwords=stopwords)
    wc = wc.generate(df['message'].str.cat(sep=' '))
    return wc