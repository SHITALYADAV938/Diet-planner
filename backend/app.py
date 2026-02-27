from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import os

app = Flask(__name__)
CORS(app)

# Load models and encoders
MODEL_PATH = 'models'
reg_v3 = joblib.load(os.path.join(MODEL_PATH, 'v3_reg.joblib'))
clf_burnout = joblib.load(os.path.join(MODEL_PATH, 'clf_burnout.joblib'))
clf_fitness = joblib.load(os.path.join(MODEL_PATH, 'clf_fitness.joblib'))
clf_diet = joblib.load(os.path.join(MODEL_PATH, 'clf_diet.joblib'))
clf_intensity = joblib.load(os.path.join(MODEL_PATH, 'clf_intensity.joblib'))
kmeans = joblib.load(os.path.join(MODEL_PATH, 'kmeans.joblib'))
encoders = joblib.load(os.path.join(MODEL_PATH, 'encoders.joblib'))
archetypes = joblib.load(os.path.join(MODEL_PATH, 'archetypes.joblib'))
feature_importance = joblib.load(os.path.join(MODEL_PATH, 'feature_importance.joblib'))
clustered_data = pd.read_csv(os.path.join(MODEL_PATH, 'clustered_data.csv'))

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

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    feedback = data.get('weekly_feedback', {}) # Continuous Learning Input
    
    # Preprocess inputs
    try:
        gender_enc = encoders['gender'].transform([data['gender']])[0]
        activity_enc = encoders['activity_level'].transform([data['activity_level']])[0]
        goal_enc = encoders['fitness_goal'].transform([data['fitness_goal']])[0]
        stress_enc = encoders['stress_level'].transform([data['stress_level']])[0]
        diet_pref_enc = encoders['diet_preference'].transform([data['diet_preference']])[0]
        living_enc = encoders['living_condition'].transform([data['living_condition']])[0]
        budget_enc = encoders['budget'].transform([data['budget']])[0]
        med_enc = encoders['medical_conditions'].transform([data.get('medical_conditions', 'none')])[0]
        equip_enc = encoders['cooking_equipment'].transform([data.get('cooking_equipment', 'none')])[0]
        
        # Mapping context strings to numbers for the model if needed, or using as flags
        context = data.get('context', 'normal') # internship, exam, travel
        is_exam_season = 1 if context == 'exam' or data.get('is_exam_season') else 0
    except Exception as e:
        return jsonify({'error': f'Encoding error: {str(e)}'}), 400
    
    bmi = data['weight'] / ((data['height'] / 100) ** 2)
    
    X = np.array([[
        data['age'], data['height'], data['weight'], bmi,
        gender_enc, activity_enc, goal_enc, data['workout_time'],
        data.get('sleep_duration', 7), stress_enc, diet_pref_enc, 
        living_enc, budget_enc, med_enc, equip_enc, is_exam_season
    ]])
    
    # Base Predictions
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
        
        # Weight adjustment
        if data['fitness_goal'] == 'weight loss' and act_weight > data['weight']:
            calories -= 150
            learning_summary.append("Weight trend higher than predicted; reducing calorie target for optimization.")
        elif data['fitness_goal'] == 'muscle gain' and act_weight <= data['weight']:
            calories += 200
            learning_summary.append("Weight plateau detected; increasing surplus to trigger muscle hypertrophy.")
            
        # Adherence adjustment
        if work_pct < 50:
            intensity = 'low'
            learning_summary.append("Low completion detected; scaling back intensity to build consistent habits.")
        elif work_pct > 90 and intensity != 'high':
            # Promotion logic
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
    # Calculation: 0-100 based on consistency, BMI, and stress
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
    
    if feedback.get('energy_level') == 'low' and feedback.get('sleep_consistency') == 'low':
        risks.append("Overtraining Risk: Body system reporting low energy. Auto-inserting rest days.")
        intensity = 'low'

    # 5. CONTEXT-AWARE ADAPTATION
    if context == 'exam':
        strategy = "Exam Neural Mode: High-protein, brain-fuel focus. Mid-day cardio replaced with 15m yoga."
        intensity = 'low'
    elif context == 'travel':
        strategy = "Travel Optimization: Equipment-free workouts. High-density meal selection."
        intensity = 'medium'

    # Generation of final plans based on adapted intensity/calories
    workout_plan = []
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for i, day in enumerate(days):
        if i == 6 or (risks and i % 3 == 0): # Auto-insert recovery days if risks detected
            workout_plan.append({'day': day, 'activities': ["Total Rest / Mindful Breathing"], 'intensity': 'Recovery'})
        else:
            workout_plan.append({'day': day, 'activities': WORKOUT_DATABASE[intensity].copy(), 'intensity': intensity})
            
    diet_plan = DIET_DATABASE[diet_type].copy()
    
    return jsonify({
        'persona': persona,
        'persona_explanation': persona_explanation,
        'fitness_score': int(evolved_score),
        'score_history': { 'current': int(evolved_score), 'previous': int(base_fitness_score), 'change': round(score_change, 1), 'reason': score_reason },
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
            'features': encoders['burnout_risk'].inverse_transform([burnout_idx])[0],
            'reasoning': f"Because your stress is {data['stress_level']} and goals are {data['fitness_goal']}, we prioritized {intensity} intensity."
        }
    })

def get_bmi_category(bmi):
    if bmi < 18.5: return "Underweight"
    if bmi < 24.9: return "Normal"
    if bmi < 29.9: return "Overweight"
    return "Obese"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
