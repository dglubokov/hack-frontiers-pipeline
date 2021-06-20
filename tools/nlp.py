
import pandas as pd

# PREPROCESSING ?
# make Dictionary from a list of sentences
# create a bag of words 
# save a gensim dictionary and corpus to disk and load them back
# Bigrams
# Trigrams

# id2word
# id2word = corpora.Dictionary(data_ready)

# Create Corpus: Term Document Frequency
# corpus = [id2word.doc2bow(text) for text in data_ready]

# --------------
# Word frequency
# --------------

# --------------
# Texts classification
# --------------

# TFIDF matrix (corpus)



# --------------
# Word2Vec
# --------------
# train Word2Vec model 

# update an existing Word2Vec model with new data

# extract word vectors using pre-trained Word2Vec and FastText models

# --------------
# named entity recognition
# --------------


# --------------
# Topics Modeling
# --------------
# Build LDA model
def lda_build(corpus, id2word):
    lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                           id2word=id2word,
                                           num_topics=4, 
                                           random_state=100,
                                           update_every=1,
                                           chunksize=10,
                                           passes=10,
                                           alpha='symmetric',
                                           iterations=100,
                                           per_word_topics=True)

def lda_get_dominant_topics(ldamodel=None, corpus=corpus, texts=data):
    """
    df_topic_sents_keywords = format_topics_sentences(ldamodel=lda_model, corpus=corpus, texts=data_ready)
    df_dominant_topic = df_topic_sents_keywords.reset_index()
    df_dominant_topic.columns = ['Document_No', 'Dominant_Topic', 'Topic_Perc_Contrib', 'Keywords', 'Text']
    df_dominant_topic.head(10)
    """
    # Init output
    sent_topics_df = pd.DataFrame()

    # Get main topic in each document
    for i, row_list in enumerate(ldamodel[corpus]):
        row = row_list[0] if ldamodel.per_word_topics else row_list            
        # print(row)
        row = sorted(row, key=lambda x: (x[1]), reverse=True)
        # Get the Dominant topic, Perc Contribution and Keywords for each document
        for j, (topic_num, prop_topic) in enumerate(row):
            if j == 0:  # => dominant topic
                wp = ldamodel.show_topic(topic_num)
                topic_keywords = ", ".join([word for word, prop in wp])
                sent_topics_df = sent_topics_df.append(pd.Series([int(topic_num), round(prop_topic,4), topic_keywords]), ignore_index=True)
            else:
                break
    sent_topics_df.columns = ['Dominant_Topic', 'Perc_Contribution', 'Topic_Keywords']

    # Add original text to the end of the output
    contents = pd.Series(texts)
    sent_topics_df = pd.concat([sent_topics_df, contents], axis=1)
    return(sent_topics_df)



# LSI topic model


# --------------
# Summarization
# --------------



# --------------
# Metrics
# --------------
# Compute Perplexity

# Compute Coherence Score