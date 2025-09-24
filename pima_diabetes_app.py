import streamlit as st
import pickle
import numpy as np

# Load the trained Naive Bayes model
model = pickle.load(open('naive_bayes_model.pkl', 'rb'))

# App title and description
st.title("🩺 Pima Indians Diabetes Predictor")
st.write("""
This app predicts whether a person is likely to have diabetes based on health parameters.
Please enter the following information and click **Predict**.
""")

# Input fields for user to enter features
pregnancies = st.number_input("Number of Pregnancies", min_value=0, max_value=20, step=1)
glucose = st.number_input("Glucose Level", min_value=0, max_value=200, step=1)
blood_pressure = st.number_input("Blood Pressure (mm Hg)", min_value=0, max_value=140, step=1)
skin_thickness = st.number_input("Skin Thickness (mm)", min_value=0, max_value=100, step=1)
insulin = st.number_input("Insulin Level (mu U/ml)", min_value=0, max_value=900, step=1)
bmi = st.number_input("BMI (Body Mass Index)", min_value=0.0, max_value=70.0, step=0.1, format="%.1f")
dpf = st.number_input("Diabetes Pedigree Function", min_value=0.0, max_value=3.0, step=0.01, format="%.2f")
age = st.number_input("Age", min_value=1, max_value=120, step=1)

# Prediction button
if st.button("Predict"):
    # Prepare input data as numpy array
    input_data = np.array([[pregnancies, glucose, blood_pressure, skin_thickness,
                            insulin, bmi, dpf, age]])
    
    # Make prediction
    prediction = model.predict(input_data)
    proba = model.predict_proba(input_data)[0][1]  # probability of diabetes
    
    # Display result
    if prediction[0] == 1:
        st.error(f"🚨 High risk of diabetes detected! Probability: {proba:.2f}")
    else:
        st.success(f"😊 Low risk of diabetes. Probability: {proba:.2f}")

# Sidebar info
st.sidebar.info("""
Developed by **Rini Chhabra**  
Contact: rinisamuel27@gmail.com  
[GitHub](https://github.com/Rinichhabra) | [LinkedIn](https://linkedin.com/in/rini-chhabra-06606a221)
""")
