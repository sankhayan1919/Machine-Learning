import emoji
from wordcloud import WordCloud, STOPWORDS
import pandas as pd
import numpy as np
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

def call_analysis(df):
    # Filter messages containing "voice call" or "video call"
    voice_calls = df[df['message'].str.contains('voice call', case=False, na=False)]
    video_calls = df[df['message'].str.contains('video call', case=False, na=False)]

    # Count the number of voice and video calls
    voice_call_count = len(voice_calls)
    video_call_count = len(video_calls)

    # If no calls are found, return a message
    if voice_call_count == 0 and video_call_count == 0:
        return pd.DataFrame(columns=['Call Type', 'Count']), "No calls happened."

    # Create a DataFrame with the counts
    call_data = pd.DataFrame({
        'Call Type': ['Voice Call', 'Video Call'],
        'Count': [voice_call_count, video_call_count]
    })

    return call_data, None

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
    if len(emojis) == 0:  # Check if no emojis are found
        return pd.DataFrame(columns=['Emoji', 'Count'])  # Return an empty DataFrame
    
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

def response_time_analysis(df):
    df = df[df['user'] != 'group_notification']

    # Calculate time difference between consecutive messages
    df['time_diff'] = df['date'].diff().dt.total_seconds()

    # Shift the 'user' column to align with the time difference (who replied to whom)
    df['prev_user'] = df['user'].shift()

    # Filter rows where the user is replying to someone else
    df = df[df['user'] != df['prev_user']]

    # Group by user and calculate average response time
    response_times = df.groupby('user')['time_diff'].mean().reset_index()
    response_times.rename(columns={'time_diff': 'avg_response_time'}, inplace=True)

    # Identify the fastest responder
    fastest_responder = response_times.loc[response_times['avg_response_time'].idxmin()]

    return response_times, fastest_responder

def first_message_of_day(df):
    # Remove group notifications
    df = df[df['user'] != 'group_notification']
    # Extract the date part of the timestamp
    df['only_date'] = df['date'].dt.date

    # Find the first message of each day
    first_messages = df.groupby('only_date').first().reset_index()

    # Count the occurrences of each user in the first messages
    first_message_counts = first_messages['user'].value_counts().reset_index()
    first_message_counts.columns = ['user', 'first_message_count']

    return first_message_counts

def late_night_activity(df):
    # Remove group notifications
    df = df[df['user'] != 'group_notification']
    # Filter messages sent between 12 AM and 3 AM
    late_night_messages = df[(df['hour'] >= 0) & (df['hour'] < 3)]

    # Count the number of messages sent by each user during this time
    late_night_counts = late_night_messages['user'].value_counts().reset_index()
    late_night_counts.columns = ['user', 'late_night_message_count']

    return late_night_counts

def longest_streaks(df):
    # Group messages by date and count the number of messages for each day
    daily_activity = df.groupby('only_date').size().reset_index(name='message_count')

    # Sort by message count in descending order
    top_days = daily_activity.sort_values(by='message_count', ascending=False).head(10)

    return top_days

