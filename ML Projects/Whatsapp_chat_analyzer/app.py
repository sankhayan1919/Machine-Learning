import streamlit as st
import preprocessor, helper
import emoji

st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")     #conversion of the bytes_data into readable text
    df = preprocessor.preprocess(data)

    st.dataframe(df)
    user_list = df['user'].unique().tolist()     # fetch unique users
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")
    selected_user = st.sidebar.selectbox("Show analysis w.r.t", user_list)
    
    if st.sidebar.button("Show analysis"):
        num_messages = helper.fetch_stats(selected_user,df)

        st.title("Top Statistics")
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(df['message'].str.split().apply(len).sum())
        with col3:
            st.header("Total Media Shared")
            st.title(df[df['message'] == '<Media omitted>\n'].shape[0])
        with col4:
            st.header("Total Links Shared")
            st.title(df[df['message'].str.contains('http')].shape[0])
        with col5:
            st.header("Total Emojis Shared")
            total_emojis = df['message'].apply(lambda x: len([c for c in x if c in emoji.EMOJI_DATA])).sum()
            st.title(total_emojis)
        with col6:
            st.header("Total Stickers Shared")
            st.title(df[df['message'].str.contains('sticker')].shape[0])
        with col7:
            st.header("Most active user")
            st.title(df['user'].value_counts().index[0])

