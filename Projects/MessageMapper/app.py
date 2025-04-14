import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import emoji

# Set page configuration (must be the first Streamlit command)
st.set_page_config(
    page_title="MessageMapper",
    page_icon="💬",
    layout="wide"
)

# Add custom CSS styling
st.markdown("""
    <style>
    /* Main app styling */
    .main {
        padding: 2rem;
    }
    
    /* Header styling */
    .st-emotion-cache-18ni7ap {
        background-color: #2c3e50;
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    /* Sidebar styling */
    .st-emotion-cache-1r6slb0 {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
    }
    
    /* Table styling */
    table {
        border: 2px solid #2c3e50 !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }
    
    th {
        background-color: #2c3e50 !important;
        color: white !important;
        padding: 12px !important;
        font-weight: 600 !important;
    }
    
    td {
        padding: 10px !important;
        border: 1px solid #e0e0e0 !important;
    }
    
    tr:nth-child(even) {
        background-color: #f8f9fa !important;
    }
    
    /* Button styling */
    .stButton button {
        background-color: #2c3e50 !important;
        color: white !important;
        border-radius: 5px !important;
        padding: 0.5rem 1rem !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton button:hover {
        background-color: #34495e !important;
        transform: translateY(-2px) !important;
    }
    
    /* Metric containers */
    div[data-testid="stMetricValue"] {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #2c3e50 !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
    }
    
    /* File uploader */
    .st-emotion-cache-1erivf3 {
        border: 2px dashed #2c3e50 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# Update the title (removed duplicate title)
st.sidebar.markdown("# 💬 MessageMapper")

# Remove this line as it's duplicate
# st.sidebar.title("MessageMapper")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")     #conversion of the bytes_data into readable text
    df = preprocessor.preprocess(data)

    # Display the dataframe only once
    st.dataframe(df, hide_index=True)
    
    # fetch unique users
    user_list = df['user'].unique().tolist()     
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
        
        # Most Active Users
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
        
         # Call Analysis
        st.title("Call Analysis") 
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
        
        # wordcloud
        st.title("Wordcloud")   
        wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(wc)
        st.pyplot(fig)
        
        # emoji analysis
        emoji_df = helper.emoji_helper(selected_user, df)   
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

        # monthly timeline
        st.title("Monthly Timeline")   
        monthly_timeline = helper.monthly_timeline(selected_user, df)    
        fig, ax = plt.subplots()
        ax.plot(monthly_timeline['month'], monthly_timeline['message'], color='#9955bb')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # daily timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        if daily_timeline is not None and not daily_timeline.empty:
            fig, ax = plt.subplots()
            ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='#00416A')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        else:
            st.write("No data available for the daily timeline.")
        
        # activity map
        st.title("Activity Map")
        col1,col2 = st.columns(2)
        with col1:
            st.header("Most busy day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='#00416A')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        with col2:
            st.header("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='#65000B')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        
        # heatmap
        st.title("Activity Heatmap")
        heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax = sns.heatmap(heatmap)
        st.pyplot(fig)

        # response time analysis
        st.title("Response Time Analysis")      
        response_times, fastest_responder = helper.response_time_analysis(df)

        col1, col2 = st.columns(2)
        with col1:
            st.header("Average Response Time")
            st.dataframe(response_times)
        with col2:
            st.header("Fastest Responder")
            st.write(f"User: {fastest_responder['user']}")
            st.write(f"Average Response Time: {fastest_responder['avg_response_time']:.2f} seconds")
        
        # first message of the day
        st.title("First Message of the Day")  
        first_message_counts = helper.first_message_of_day(df)

        if selected_user == 'Overall' and not first_message_counts.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(first_message_counts['user'], first_message_counts['first_message_count'], width=0.4, color='#FFCC00') #sunglow yellow
            ax.set_xlabel("User", fontsize=12)
            ax.set_ylabel("First Message Count", fontsize=8)
            st.pyplot(fig)
        elif not first_message_counts.empty:
            st.dataframe(first_message_counts)
        else:
            st.write("No data available for first message analysis.")
        
        # late night activity
        st.title("Late Night Activity (12 AM - 3 AM)")   
        late_night_counts = helper.late_night_activity(df)

        if selected_user == 'Overall' and not late_night_counts.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(late_night_counts['user'], late_night_counts['late_night_message_count'], width=0.4, color='#FF7F50') #gunmetal
            ax.set_xlabel("User", fontsize=12)
            ax.set_ylabel("No. of Messagest", fontsize=12)
            st.pyplot(fig)
        elif not late_night_counts.empty:
            st.dataframe(late_night_counts)
        else:
            st.write("No late-night activity detected.")
        
        # Longest Streaks Analysis
        st.title("Top 10 Days with Continuous Chat Activity")      
        top_days = helper.longest_streaks(df)

        if not top_days.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Create the bar chart
            ax.bar(top_days['only_date'].astype(str), top_days['message_count'], color='#39FF14') #neon green
                            
            ax.set_xlabel("Date", fontsize=12)
            ax.set_ylabel("Number of Messages", fontsize=12)
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        else:
            st.write("No data available for longest streaks analysis.")
        
        # Text Length Analysis
        st.title("Text Length Analysis")
        text_length_df = helper.text_length_analysis(selected_user, df)
        
        if selected_user == 'Overall':
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(text_length_df['User'], text_length_df['Average Message Length'], width=0.4, color='#008080') #teal
            ax.set_xlabel("User")
            ax.set_ylabel("Average Message Length (characters)")
            st.pyplot(fig)
        
    
        
            

      