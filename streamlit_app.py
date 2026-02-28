import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from pathlib import Path

# Configure page
st.set_page_config(page_title="Diet Planner AI", layout="wide", initial_sidebar_state="expanded")

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Load models and data
@st.cache_resource
def load_models():
    # Get the models directory - go up from streamlit_app.py to root, then models
    base_path = Path(__file__).parent
    model_path = base_path / 'models'
    
    models = {
        'reg_v3': joblib.load(model_path / 'v3_reg.joblib'),
        'clf_burnout': joblib.load(model_path / 'clf_burnout.joblib'),
        'clf_fitness': joblib.load(model_path / 'clf_fitness.joblib'),
        'clf_diet': joblib.load(model_path / 'clf_diet.joblib'),
        'clf_intensity': joblib.load(model_path / 'clf_intensity.joblib'),
        'kmeans': joblib.load(model_path / 'kmeans.joblib'),
        'encoders': joblib.load(model_path / 'encoders.joblib'),
        'archetypes': joblib.load(model_path / 'archetypes.joblib'),
        'feature_importance': joblib.load(model_path / 'feature_importance.joblib'),
        'clustered_data': pd.read_csv(model_path / 'clustered_data.csv')
    }
    return models

# Database constants
WORKOUT_DATABASE = {
    'low': ["Walking (30 mins)", "Yoga / Stretching", "Light Bodyweight Squats", "Plank (20s x 3)"],
    'medium': ["Brisk Walking / Jogging", "Push-ups (10 x 3)", "Lunges (12 x 3)", "Bird-dog Exercises"],
    'high': ["Running (20 mins)", "HIIT Cardio", "Burpees (15 x 3)", "Diamond Push-ups (10 x 3)"]
}

DIET_DATABASE = {
    'cutting': {
        'Breakfast': 'Oats with Almonds & Berries',
        'Lunch': 'Lentil Soup (Dal), 1 Brown Roti, Large Salad',
        'Snack': 'Roasted Makhana / Tea without Sugar',
        'Dinner': 'Soya Chunks Stir-fry / Grilled Fish, Sauteed Veggies',
        'Shopping': ['Oats', 'Lentils', 'Seasonal Vegetables', 'Makhana', 'Soya Chunks']
    },
    'balanced': {
        'Breakfast': 'Paneer Bhurji / Vegetable Poha',
        'Lunch': 'Dal Tadka, 2 Rotis, Curd, Cucumbers',
        'Snack': 'Sprouted Moong Salad',
        'Dinner': 'Mixed Vegetable Curry with 1 Roti and Salad',
        'Shopping': ['Paneer', 'Poha', 'Lentils', 'Sprouts', 'Vegetables']
    },
    'bulking': {
        'Breakfast': 'Egg Omelette (3 eggs) / Peanut Butter Toast + Milk',
        'Lunch': 'Chicken Curry / Rajma, 2 Rotis, Large bowl of Rice',
        'Snack': 'Mixed Nuts / Peanut Butter Banana Shake',
        'Dinner': 'Paneer Tikka / Grilled Chicken, Brown Rice, Dal',
        'Shopping': ['Eggs/Paneer', 'Peanut Butter', 'Chicken/Rajma', 'Rice', 'Nuts']
    }
}

def get_bmi_category(bmi):
    if bmi < 18.5: return "Underweight"
    if bmi < 24.9: return "Normal"
    if bmi < 29.9: return "Overweight"
    return "Obese"

def predict_plan(data, models, feedback=None):
    """Generate personalized fitness and diet plan"""
    encoders = models['encoders']
    reg_v3 = models['reg_v3']
    clf_burnout = models['clf_burnout']
    clf_fitness = models['clf_fitness']
    clf_diet = models['clf_diet']
    clf_intensity = models['clf_intensity']
    kmeans = models['kmeans']
    
    try:
        # Encode categorical features
        gender_enc = encoders['gender'].transform([data['gender']])[0]
        activity_enc = encoders['activity_level'].transform([data['activity_level']])[0]
        goal_enc = encoders['fitness_goal'].transform([data['fitness_goal']])[0]
        stress_enc = encoders['stress_level'].transform([data['stress_level']])[0]
        diet_pref_enc = encoders['diet_preference'].transform([data['diet_preference']])[0]
        living_enc = encoders['living_condition'].transform([data['living_condition']])[0]
        budget_enc = encoders['budget'].transform([data['budget']])[0]
        med_enc = encoders['medical_conditions'].transform([data.get('medical_conditions', 'none')])[0]
        equip_enc = encoders['cooking_equipment'].transform([data.get('cooking_equipment', 'none')])[0]
        
        context = data.get('context', 'normal')
        is_exam_season = 1 if context == 'exam' or data.get('is_exam_season') else 0
        
    except Exception as e:
        st.error(f"Encoding error: {str(e)}")
        return None
    
    # Calculate BMI
    bmi = data['weight'] / ((data['height'] / 100) ** 2)
    
    # Prepare feature vector
    X = np.array([[
        data['age'], data['height'], data['weight'], bmi,
        gender_enc, activity_enc, goal_enc, data['workout_time'],
        data.get('sleep_duration', 7), stress_enc, diet_pref_enc, 
        living_enc, budget_enc, med_enc, equip_enc, is_exam_season
    ]])
    
    # Base predictions
    preds = reg_v3.predict(X)[0]
    calories, protein, carbs, fats, hydration, base_fitness_score = preds
    
    burnout_idx = clf_burnout.predict(X)[0]
    fit_level_idx = clf_fitness.predict(X)[0]
    diet_type_idx = clf_diet.predict(X)[0]
    intensity_idx = clf_intensity.predict(X)[0]
    
    burnout_risk = encoders['burnout_risk'].inverse_transform([burnout_idx])[0]
    fitness_level = encoders['fitness_level'].inverse_transform([fit_level_idx])[0]
    diet_type = encoders['diet_type'].inverse_transform([diet_type_idx])[0]
    intensity = encoders['intensity'].inverse_transform([intensity_idx])[0]
    
    # Initialize default strategy
    strategy = f"Neural Blueprint Synchronized. Maintaining {intensity} intensity for optimal metabolic response."
    
    # 1. CONTINUOUS LEARNING & ADAPTATION
    learning_summary = []
    if feedback:
        act_weight = feedback.get('current_weight', data['weight'])
        work_pct = feedback.get('workout_completion', 100)
        diet_pct = feedback.get('diet_adherence', 100)
        
        if data['fitness_goal'] == 'weight loss' and act_weight > data['weight']:
            calories -= 150
            learning_summary.append("Weight trend higher than predicted; reducing calorie target for optimization.")
        elif data['fitness_goal'] == 'muscle gain' and act_weight <= data['weight']:
            calories += 200
            learning_summary.append("Weight plateau detected; increasing surplus to trigger muscle hypertrophy.")
            
        if work_pct < 50:
            intensity = 'low'
            learning_summary.append("Low completion detected; scaling back intensity to build consistent habits.")
        elif work_pct > 90 and intensity != 'high':
            learning_summary.append("Exceptional adherence; increasing neural workout intensity for faster progress.")

    # 2. FITNESS PERSONA REFINEMENT
    cluster = int(kmeans.predict(X)[0])
    student_personas = {
        0: "Busy Hostel Muscle Builder",
        1: "Stressed Exam-Phase Beginner",
        2: "Consistent Lean Fitness Improver",
        3: "Social Athlete - Group Focus"
    }
    persona = student_personas.get(cluster, "The Adaptive Striper")
    persona_explanation = f"You were clustered here based on your {data['living_condition']} lifestyle and {data['fitness_goal']} objective."

    # 3. INTELLIGENCE SCORE EVOLUTION
    evolved_score = base_fitness_score
    if feedback:
        evolved_score = (base_fitness_score * 0.7) + (feedback.get('workout_completion', 100) * 0.3)
    
    score_change = evolved_score - base_fitness_score
    score_reason = "High adherence is driving your score up!" if score_change > 0 else "Consistency is key to improving this score."

    # 4. SMART RECOVERY & RISK MONITORING
    risks = []
    if burnout_risk == 'high' or data.get('sleep_duration', 7) < 5:
        risks.append("CRITICAL: Sleep Deprivation Detected. Recovery protocols initialized.")
        strategy = "Recovery Shield Active: Reducing intensity to prevent burnout."
        intensity = 'low'
    
    if feedback and feedback.get('energy_level') == 'low' and feedback.get('sleep_consistency') == 'low':
        risks.append("Overtraining Risk: Body system reporting low energy. Auto-inserting rest days.")
        intensity = 'low'

    # 5. CONTEXT-AWARE ADAPTATION
    if context == 'exam':
        strategy = "Exam Neural Mode: High-protein, brain-fuel focus. Mid-day cardio replaced with 15m yoga."
        intensity = 'low'
    elif context == 'travel':
        strategy = "Travel Optimization: Equipment-free workouts. High-density meal selection."
        intensity = 'medium'

    # Generate final plans
    workout_plan = []
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for i, day in enumerate(days):
        if i == 6 or (risks and i % 3 == 0):
            workout_plan.append({'day': day, 'activities': ["Total Rest / Mindful Breathing"], 'intensity': 'Recovery'})
        else:
            workout_plan.append({'day': day, 'activities': WORKOUT_DATABASE[intensity].copy(), 'intensity': intensity})
            
    diet_plan = DIET_DATABASE[diet_type].copy()
    
    return {
        'persona': persona,
        'persona_explanation': persona_explanation,
        'fitness_score': int(evolved_score),
        'score_history': { 
            'current': int(evolved_score), 
            'previous': int(base_fitness_score), 
            'change': round(score_change, 1), 
            'reason': score_reason 
        },
        'learning_summary': learning_summary or ["AI core analyzed inputs and confirmed the current blueprint holds maximal efficiency."],
        'risks': risks,
        'hydration': round(hydration, 1),
        'bmi_summary': { 'bmi': round(bmi, 2), 'category': get_bmi_category(bmi) },
        'predictions': {
            'fitness_level': fitness_level,
            'diet_type': diet_type,
            'intensity': intensity,
            'macros': { 'calories': int(calories), 'protein': int(protein), 'carbs': int(carbs), 'fats': int(fats) }
        },
        'plans': {
            'workout': workout_plan,
            'diet': diet_plan,
            'shopping_list': diet_plan.get('Shopping', []),
            'smart_substitutions': {
                'meal': "Swap lentils for chicken if protein targets aren't being met." if data['diet_preference'] == 'non-vegetarian' else "Increase soy chunks for protein boost.",
                'workout': "If you skip this, perform 50 bodyweight squats to maintain neural metabolic load."
            }
        },
        'strategy': strategy,
        'explainable_ai': {
            'trigger': "ML Feedback Loop" if feedback else "Initial Feature Mapping",
            'reasoning': f"Because your stress is {data['stress_level']} and goals are {data['fitness_goal']}, we prioritized {intensity} intensity."
        }
    }

# Main app
st.title("🏋️ AI Diet & Fitness Planner")
st.markdown("Your personalized neural fitness blueprint powered by machine learning")

try:
    models = load_models()
    
    # Tabs for input and feedback
    tab1, tab2, tab3 = st.tabs(["📋 Personal Profile", "📊 Your Plan", "💬 Feedback & Adaptation"])
    
    with tab1:
        st.header("Tell us about yourself")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            age = st.number_input("Age", min_value=13, max_value=80, value=25)
            height = st.number_input("Height (cm)", min_value=130, max_value=220, value=170)
            weight = st.number_input("Weight (kg)", min_value=30, max_value=200, value=70)
        
        with col2:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            activity_level = st.selectbox("Activity Level", ["sedentary", "light", "moderate", "very active"])
            fitness_goal = st.selectbox("Fitness Goal", ["weight loss", "muscle gain", "maintenance"])
        
        with col3:
            stress_level = st.selectbox("Stress Level", ["low", "moderate", "high"])
            sleep_duration = st.slider("Sleep Duration (hours)", 3, 12, 7)
            workout_time = st.slider("Workout Time per week (mins)", 0, 300, 150)
        
        col4, col5, col6 = st.columns(3)
        
        with col4:
            diet_preference = st.selectbox("Diet Preference", ["vegetarian", "non-vegetarian", "vegan"])
            living_condition = st.selectbox("Living Condition", ["hostel", "home", "paying_guest"])
        
        with col5:
            budget = st.selectbox("Budget Level", ["low", "moderate", "high"])
            medical_conditions = st.selectbox("Medical Conditions", ["none", "diabetes", "hypertension", "thyroid"])
        
        with col6:
            cooking_equipment = st.selectbox("Cooking Equipment", ["none", "basic", "full"])
            context = st.selectbox("Current Context", ["normal", "exam", "travel"])
        
        # Create data dictionary
        user_data = {
            'age': age,
            'height': height,
            'weight': weight,
            'gender': gender,
            'activity_level': activity_level,
            'fitness_goal': fitness_goal,
            'stress_level': stress_level,
            'sleep_duration': sleep_duration,
            'workout_time': workout_time,
            'diet_preference': diet_preference,
            'living_condition': living_condition,
            'budget': budget,
            'medical_conditions': medical_conditions,
            'cooking_equipment': cooking_equipment,
            'context': context
        }
        
        if st.button("🚀 Generate Your Plan", key="generate_plan"):
            st.session_state.user_data = user_data
            st.session_state.show_results = True
    
    # Display results if generated
    if st.session_state.get('show_results'):
        result = predict_plan(st.session_state.user_data, models)
        
        if result:
            with tab2:
                st.success("✨ Your Personalized Plan is Ready!")
                
                # Persona and Strategy
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"### 👤 Your Persona")
                    st.markdown(f"**{result['persona']}**")
                    st.write(result['persona_explanation'])
                
                with col2:
                    st.markdown(f"### 🎯 Strategy")
                    st.info(result['strategy'])
                
                # Key Metrics
                st.markdown("### 📈 Key Metrics")
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                
                with metric_col1:
                    st.metric("Fitness Score", result['fitness_score'], f"{result['score_history']['change']:.1f}")
                
                with metric_col2:
                    bmi_data = result['bmi_summary']
                    st.metric("BMI", f"{bmi_data['bmi']}", delta=bmi_data['category'])
                
                with metric_col3:
                    st.metric("Hydration", f"{result['hydration']} L/day")
                
                with metric_col4:
                    st.metric("Fitness Level", result['predictions']['fitness_level'])
                
                # Macros
                st.markdown("### 🥗 Daily Macronutrients")
                macros = result['predictions']['macros']
                macro_col1, macro_col2, macro_col3, macro_col4 = st.columns(4)
                
                with macro_col1:
                    st.metric("Calories", f"{macros['calories']} kcal")
                with macro_col2:
                    st.metric("Protein", f"{macros['protein']}g")
                with macro_col3:
                    st.metric("Carbs", f"{macros['carbs']}g")
                with macro_col4:
                    st.metric("Fats", f"{macros['fats']}g")
                
                # Risks
                if result['risks']:
                    st.markdown("### ⚠️ Health Alerts")
                    for risk in result['risks']:
                        st.warning(risk)
                
                # Learning Summary
                if result['learning_summary']:
                    st.markdown("### 🧠 AI Insights")
                    for insight in result['learning_summary']:
                        st.info(insight)
                
                # Workout Plan
                st.markdown("### 💪 Weekly Workout Plan")
                workout_df = pd.DataFrame(result['plans']['workout'])
                for _, row in workout_df.iterrows():
                    with st.expander(f"{row['day']} - {row['intensity']}"):
                        for activity in row['activities']:
                            st.write(f"• {activity}")
                
                # Diet Plan
                st.markdown("### 🍽️ Daily Diet Plan")
                diet_plan = result['plans']['diet']
                for meal, description in diet_plan.items():
                    if meal != 'Shopping':
                        st.write(f"**{meal}:** {description}")
                
                # Shopping List
                st.markdown("### 🛒 Shopping List")
                shopping_list = result['plans']['shopping_list']
                cols = st.columns(2)
                for idx, item in enumerate(shopping_list):
                    with cols[idx % 2]:
                        st.checkbox(item)
                
                # Smart Substitutions
                st.markdown("### 💡 Smart Tips")
                st.write(f"**Meal:** {result['plans']['smart_substitutions']['meal']}")
                st.write(f"**Workout:** {result['plans']['smart_substitutions']['workout']}")
            
            with tab3:
                st.header("Weekly Feedback & Adaptation")
                st.write("Track your progress and let the AI adapt your plan!")
                
                feedback_col1, feedback_col2 = st.columns(2)
                
                with feedback_col1:
                    current_weight = st.number_input(
                        "Current Weight (kg)", 
                        value=st.session_state.user_data['weight'],
                        key="feedback_weight"
                    )
                    workout_completion = st.slider(
                        "Workout Completion (%)", 
                        0, 100, 100,
                        key="feedback_workout"
                    )
                    diet_adherence = st.slider(
                        "Diet Adherence (%)", 
                        0, 100, 100,
                        key="feedback_diet"
                    )
                
                with feedback_col2:
                    energy_level = st.selectbox(
                        "Energy Level",
                        ["low", "moderate", "high"],
                        key="feedback_energy"
                    )
                    sleep_consistency = st.selectbox(
                        "Sleep Consistency",
                        ["low", "moderate", "high"],
                        key="feedback_sleep"
                    )
                    mood = st.selectbox(
                        "Overall Mood",
                        ["stressed", "neutral", "positive"],
                        key="feedback_mood"
                    )
                
                if st.button("🔄 Adapt My Plan", key="adapt_plan"):
                    feedback_data = {
                        'current_weight': current_weight,
                        'workout_completion': workout_completion,
                        'diet_adherence': diet_adherence,
                        'energy_level': energy_level,
                        'sleep_consistency': sleep_consistency,
                        'mood': mood
                    }
                    
                    adapted_result = predict_plan(st.session_state.user_data, models, feedback_data)
                    
                    if adapted_result:
                        st.success("✨ Your plan has been adapted!")
                        
                        # Show changes
                        st.markdown("### 📊 What Changed")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric(
                                "Fitness Score",
                                adapted_result['fitness_score'],
                                f"{adapted_result['score_history']['change']:.1f}"
                            )
                        
                        with col2:
                            st.metric(
                                "Recommended Intensity",
                                adapted_result['predictions']['intensity'],
                                f"Diet: {adapted_result['predictions']['diet_type']}"
                            )
                        
                        with col3:
                            st.metric(
                                "Calories",
                                f"{adapted_result['predictions']['macros']['calories']} kcal"
                            )
                        
                        # Show learning summary
                        if adapted_result['learning_summary']:
                            st.markdown("### 🧠 AI Adaptation Notes")
                            for note in adapted_result['learning_summary']:
                                st.info(note)

except Exception as e:
    st.error(f"Error loading models: {str(e)}")
    st.info("Make sure the 'models' folder is in the same directory as this script.")
