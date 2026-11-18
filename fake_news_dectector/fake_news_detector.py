import streamlit as st
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import random

# =============================================================================
# 1. DATA GENERATION & MODEL TRAINING (Cached to run only once)
# =============================================================================
@st.cache_resource
def train_model():
    """Generates a synthetic dataset and trains the ML model."""
    
    # --- 1. Create Synthetic Data ---
    # We create specific word patterns so the model can easily learn 
    # the difference between "Real" (objective, factual) and "Fake" (sensational, clickbait).
    
    fake_news_templates = [
        "SHOCKING! You won't believe what the government just did to your money!",
        "Aliens have officially landed in New York, secret sources confirm.",
        "Doctors HATE this one weird trick to cure all diseases instantly!",
        "The truth about the moon landing they are hiding from you.",
        "BREAKING: Massive conspiracy uncovered by anonymous insider!",
        "Click here to claim your free million dollars right now!",
        "Scientists are secretly replacing humans with lizard people.",
        "This celebrity is actually a robot, leaked photos prove it!",
        "Mainstream media is lying to you about the weather!",
        "URGENT ALERT: The end of the world is happening tomorrow, prepare now!"
    ]
    
    real_news_templates = [
        "The Federal Reserve announced a 0.25% interest rate hike on Wednesday.",
        "Researchers at MIT published a new study on renewable energy efficiency.",
        "The city council approved the new budget for infrastructure repairs.",
        "According to the latest census data, the population grew by 2%.",
        "The stock market closed higher today, driven by tech sector gains.",
        "A new species of frog was discovered in the Amazon rainforest.",
        "The president met with foreign leaders to discuss trade agreements.",
        "Apple released its quarterly earnings report, meeting analyst expectations.",
        "Local schools received a grant to improve their STEM programs.",
        "The weather forecast predicts moderate rainfall over the weekend."
    ]

    # Generate a larger dataset by shuffling words slightly
    texts = []
    labels = []
    
    for _ in range(300):
        texts.append(random.choice(fake_news_templates))
        labels.append(1) # 1 = FAKE
        
    for _ in range(300):
        texts.append(random.choice(real_news_templates))
        labels.append(0) # 0 = REAL
        
    df = pd.DataFrame({'text': texts, 'label': labels})
    
    # --- 2. Train the Model ---
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(df['text'], df['label'], test_size=0.2, random_state=42)
    
    # Vectorization (TF-IDF: Term Frequency-Inverse Document Frequency)
    # This converts text into numbers, giving higher weight to unique, important words.
    vectorizer = TfidfVectorizer(stop_words='english', max_df=0.7)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # Classification (Logistic Regression)
    model = LogisticRegression()
    model.fit(X_train_vec, y_train)
    
    # Evaluate
    predictions = model.predict(X_test_vec)
    accuracy = accuracy_score(y_test, predictions)
    
    return vectorizer, model, accuracy, df

# Load the model (this will only take a second)
with st.spinner("Training NLP Model on synthetic data... (This only happens once)"):
    vectorizer, model, model_accuracy, training_df = train_model()

# =============================================================================
# 2. STREAMLIT UI
# =============================================================================
st.set_page_config(page_title="Fake News Detector", page_icon="📰", layout="wide")

st.title("📰 Fake News Detector")
st.markdown("""
**What it does:**
Uses Machine Learning and NLP to classify news text based on learned language patterns. 
Paste an article or headline below to check its validity.
""")

# Sidebar Info
with st.sidebar:
    st.header("📊 Model Stats")
    st.metric(label="Model Accuracy", value=f"{model_accuracy * 100:.1f}%")
    st.info("""
    **How it works:**
    1. **TF-IDF**: Converts text to numbers.
    2. **Logistic Regression**: Finds patterns in the words.
    3. **Classification**: Predicts Real (0) or Fake (1).
    """)
    with st.expander("View Training Data Samples"):
        st.dataframe(training_df.sample(5), use_container_width=True)

# Main Content
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Input Text")
    user_input = st.text_area(
        "Paste the news headline or article here:", 
        height=300,
        placeholder="Example: SHOCKING! Aliens have officially landed in New York..."
    )
    
    analyze_btn = st.button("🔍 Analyze Text", type="primary", use_container_width=True)

with col2:
    st.subheader("📋 Verification Results")
    
    if analyze_btn:
        if not user_input.strip():
            st.warning("Please enter some text to analyze.")
        else:
            # Vectorize the input
            input_vec = vectorizer.transform([user_input])
            
            # Predict
            prediction = model.predict(input_vec)[0]
            probabilities = model.predict_proba(input_vec)[0]
            
            # Display Results
            if prediction == 1:
                st.error("### 🚨 FAKE NEWS DETECTED")
                st.write("The model detects patterns commonly associated with sensationalized, clickbait, or false reporting.")
                confidence = probabilities[1] * 100
                st.progress(int(confidence), text=f"Confidence: {confidence:.1f}%")
            else:
                st.success("### ✅ LIKELY REAL NEWS")
                st.write("The model detects objective, factual language patterns.")
                confidence = probabilities[0] * 100
                st.progress(int(confidence), text=f"Confidence: {confidence:.1f}%")
                
            # Show breakdown
            st.markdown("---")
            st.write("**Probability Breakdown:**")
            st.write(f"- Real News: `{probabilities[0]*100:.1f}%`")
            st.write(f"- Fake News: `{probabilities[1]*100:.1f}%`")
            
    else:
        st.info("Awaiting input. Paste text on the left and click Analyze.")