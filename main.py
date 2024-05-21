import streamlit as st
import pickle
import pandas as pd
import textwrap

def convert_url(old_url):
    new_url = old_url.replace("i.gr-assets.com", "images-na.ssl-images-amazon.com")
    new_url = new_url.replace("._SX50_SY75_", "")
    new_url = new_url.replace("._SY75_", "")
    new_url = new_url.replace("._SX50_", "")
    return new_url

def recommend(book):
    book_row = bookes.loc[bookes['title'] == book]
    if book_row.empty:
        print(f"No books found with title {book}")
        return None
    print("Bookrow",book_row)
    cluster_label = book_row['cluster'].iloc[0]
    print("Cluster: ",cluster_label)
    similarity_matrix = similarity[cluster_label]
    cluster_data = bookes.loc[bookes['cluster'] == cluster_label].reset_index(drop=True)
    book_index = cluster_data[cluster_data['title'] == book].index[0]
    distances = sorted(list(enumerate(similarity_matrix[book_index])),reverse=True,key = lambda x: x[1])
    booksRecommend = []
    
    for i in distances[1:16]:
        booksRecommend.append(cluster_data.iloc[i[0]])
    return booksRecommend
    # return recommend_books
    
bookes_list = pickle.load(open('books.pkl', 'rb'))
bookes = pd.DataFrame(bookes_list)

similarity = pickle.load(open('similarity.pkl', 'rb'))
st.set_page_config(layout='wide')
st.title("Book Recommend System")
option = st.selectbox(
    "How would you like to be contacted?",
    bookes['title'].values)

if st.button('Recommend'):
    recommendations = recommend(option)
    # col1, col2, col3, col4, col5 = st.columns(5)
    # columns = [col1, col2, col3, col4, col5]

    # for i, book in enumerate(recommendations):  
    #     with columns[i]:
    #         wrapped_text = textwrap.fill(book['title'], width=30)  # Adjust the width as needed
    #         st.text(wrapped_text)
    #         new_img_url = convert_url(book['img'])
    #         print(new_img_url)
    #         st.image(new_img_url)
    num_columns = 5
    num_rows = 3

    for row in range(num_rows):
        columns = st.columns(num_columns)
        for col in range(num_columns):
            i = row * num_columns + col
            if i < len(recommendations):
                book = recommendations[i]
                with columns[col]:
                    wrapped_text = textwrap.fill(book['title'], width=30)  # Adjust the width as needed
                    st.text(wrapped_text)
                    new_img_url = convert_url(book['img'])
                    st.image(new_img_url)
    # st.write(option)    
