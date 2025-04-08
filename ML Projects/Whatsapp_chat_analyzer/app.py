import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import emoji

st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")     #conversion of the bytes_data into readable text
    df = preprocessor.preprocess(data)

    st.dataframe(df)    # display the dataframe
    
    user_list = df['user'].unique().tolist()     # fetch unique users
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")
    selected_user = st.sidebar.selectbox("Show analysis w.r.t", user_list)
    
    if st.sidebar.button("Show analysis"):
        num_messages, words, num_media_messages, links, num_emojis, num_stickers = helper.fetch_stats(selected_user,df)

        st.title("Top Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Total Media Shared")
            st.title(num_media_messages)

        col4, col5, col6 = st.columns(3)
        with col4:
            st.header("Total Links Shared")
            st.title(links)
        with col5:
            st.header("Total Emojis Shared")
            st.title(num_emojis)
        with col6:
            st.header("Total Stickers Shared")
            st.title(num_stickers)
        
    
        if selected_user == 'Overall':
            st.title("Most Active Users")
            x, new_df = helper.most_active_users(df)
            fig, ax = plt.subplots()
            col1, col2 = st.columns(2)
            with col1:
                ax.bar(x.index, x.values)
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)
        
        st.title("Call Analysis")  # Call Analysis
        call_data, call_message = helper.call_analysis(df)
        if call_message:
            st.write(call_message)
        else:
            st.dataframe(call_data)
            fig, ax = plt.subplots()
            ax.bar(call_data['Call Type'], call_data['Count'], color=['blue', 'green'])
            ax.set_xlabel("Call Type", fontsize=12)
            ax.set_ylabel("Count", fontsize=12)
            ax.set_title("Number of Voice and Video Calls", fontsize=14)
            st.pyplot(fig)
        
        st.title("Wordcloud")   # wordcloud
        wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(wc)
        st.pyplot(fig)

        emoji_df = helper.emoji_helper(selected_user, df)    # emoji analysis
        st.title("Emoji Analysis") 
        col1, col2 = st.columns(2)
        if emoji_df.empty:
            st.write("No emojis found in the messages.")
        else:
            with col1:
                st.dataframe(emoji_df)
            with col2:
                fig, ax = plt.subplots()
                ax.pie(emoji_df['Count'], labels=emoji_df['Emoji'], autopct='%1.1f%%')
                st.pyplot(fig)

        st.title("Monthly Timeline")    # monthly timeline
        monthly_timeline = helper.monthly_timeline(selected_user, df)    
        fig, ax = plt.subplots()
        ax.plot(monthly_timeline['month'], monthly_timeline['message'], color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        st.title("Daily Timeline")    # daily timeline
        daily_timeline = helper.daily_timeline(selected_user, df)
        if daily_timeline is not None and not daily_timeline.empty:
            fig, ax = plt.subplots()
            ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        else:
            st.write("No data available for the daily timeline.")
        
        st.title("Activity Map")
        col1,col2 = st.columns(2)
        with col1:
            st.header("Most busy day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='black')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        with col2:
            st.header("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='red')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        
        st.title("Activity Heatmap")
        heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax = sns.heatmap(heatmap)
        st.pyplot(fig)

        st.title("Response Time Analysis")      # Response Time Analysis
        response_times, fastest_responder = helper.response_time_analysis(df)

        col1, col2 = st.columns(2)
        with col1:
            st.header("Average Response Time")
            st.dataframe(response_times)
        with col2:
            st.header("Fastest Responder")
            st.write(f"User: {fastest_responder['user']}")
            st.write(f"Average Response Time: {fastest_responder['avg_response_time']:.2f} seconds")

        st.title("First Message of the Day")   # first message of the day
        first_message_counts = helper.first_message_of_day(df)

        if selected_user == 'Overall' and not first_message_counts.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(first_message_counts['user'], first_message_counts['first_message_count'], color='pink')
            ax.set_xlabel("User", fontsize=12)
            ax.set_ylabel("First Message Count", fontsize=12)
            st.pyplot(fig)
        elif not first_message_counts.empty:
            st.dataframe(first_message_counts)
        else:
            st.write("No data available for first message analysis.")
        
        st.title("Late Night Activity (12 AM - 3 AM)")    # late night activity
        late_night_counts = helper.late_night_activity(df)

        if selected_user == 'Overall' and not late_night_counts.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(late_night_counts['user'], late_night_counts['late_night_message_count'], color='yellow')
            ax.set_xlabel("User", fontsize=12)
            ax.set_ylabel("Late Night Message Count", fontsize=12)
            st.pyplot(fig)
        elif not late_night_counts.empty:
            st.dataframe(late_night_counts)
        else:
            st.write("No late-night activity detected.")

        st.title("Top 10 Days with Continuous Chat Activity")      # Longest Streaks Analysis
        top_days = helper.longest_streaks(df)

        if not top_days.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Create the bar chart
            ax.bar(top_days['only_date'].astype(str), top_days['message_count'], color='purple')
                            
            ax.set_xlabel("Date", fontsize=12)
            ax.set_ylabel("Number of Messages", fontsize=12)
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        else:
            st.write("No data available for longest streaks analysis.")

      