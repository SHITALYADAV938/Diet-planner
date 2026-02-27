import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder
import joblib
import os

# Create directory for models
os.makedirs('models', exist_ok=True)

def generate_data(n=2000):
    np.random.seed(42)
    
    data = {
        'age': np.random.randint(18, 30, n),
        'gender': np.random.choice(['male', 'female'], n),
        'height': np.random.randint(150, 200, n),
        'weight': np.random.randint(40, 120, n),
        'activity_level': np.random.choice(['sedentary', 'moderate', 'active', 'very active'], n),
        'fitness_goal': np.random.choice(['weight loss', 'muscle gain', 'maintenance', 'overall fitness'], n),
        'workout_time': np.random.randint(20, 120, n),
        'sleep_duration': np.random.randint(4, 10, n),
        'stress_level': np.random.choice(['low', 'medium', 'high'], n),
        'diet_preference': np.random.choice(['vegetarian', 'non-vegetarian'], n),
        'living_condition': np.random.choice(['hostel', 'home', 'pg'], n),
        'budget': np.random.choice(['low', 'medium', 'high'], n),
        'medical_conditions': np.random.choice(['none', 'diabetes', 'hypertension', 'thyroid', 'asthma'], n),
        'cooking_equipment': np.random.choice(['none', 'induction', 'full kitchen'], n),
        'is_exam_season': np.random.choice([0, 1], n, p=[0.8, 0.2])
    }
    
    df = pd.DataFrame(data)
    df['bmi'] = df['weight'] / ((df['height'] / 100) ** 2)
    
    # Target Logic
    def get_fitness_level(row):
        val = 0
        if row['activity_level'] in ['active', 'very active']: val += 2
        if row['workout_time'] > 60: val += 1
        if row['stress_level'] == 'low': val += 1
        if val >= 3: return 'advanced'
        if val >= 1: return 'intermediate'
        return 'beginner'

    def get_burnout_risk(row):
        risk = 0
        if row['stress_level'] == 'high': risk += 2
        if row['sleep_duration'] < 6: risk += 2
        if row['workout_time'] > 90 and row['activity_level'] == 'very active': risk += 1
        if row['is_exam_season'] == 1: risk += 1
        
        if risk >= 4: return 'high'
        if risk >= 2: return 'medium'
        return 'low'

    def get_hydration(row):
        # Base hydration: 30ml per kg
        base = row['weight'] * 0.03
        if row['activity_level'] in ['active', 'very active']: base += 1.0
        if row['workout_time'] > 60: base += 0.5
        return round(base, 1)

    def get_macros(row):
        bmr = 10 * row['weight'] + 6.25 * row['height'] - 5 * row['age']
        bmr += 5 if row['gender'] == 'male' else -161
        mult = {'sedentary': 1.2, 'moderate': 1.5, 'active': 1.7, 'very active': 1.9}[row['activity_level']]
        calories = bmr * mult
        
        if row['is_exam_season'] == 1: calories += 150 # Brain energy
        if row['fitness_goal'] == 'weight loss': calories -= 500
        elif row['fitness_goal'] == 'muscle gain': calories += 400
        
        p = (calories * (0.25 if row['fitness_goal'] == 'muscle gain' else 0.15)) / 4
        f = (calories * 0.25) / 9
        c = (calories - (p * 4) - (f * 9)) / 4
        return pd.Series([calories, p, c, f])

    df['fitness_level'] = df.apply(get_fitness_level, axis=1)
    df['burnout_risk'] = df.apply(get_burnout_risk, axis=1)
    df['hydration'] = df.apply(get_hydration, axis=1)
    df[['calories', 'protein', 'carbs', 'fats']] = df.apply(get_macros, axis=1)
    df['intensity'] = np.where(df['workout_time'] > 80, 'high', np.where(df['workout_time'] > 45, 'medium', 'low'))
    df['diet_type'] = np.where(df['fitness_goal'] == 'weight loss', 'cutting', np.where(df['fitness_goal'] == 'muscle gain', 'bulking', 'balanced'))
    
    # Intelligence Score
    def get_score(row):
        s = 50
        bmi = row['weight'] / ((row['height'] / 100) ** 2)
        if 18.5 <= bmi <= 25: s += 15
        s += {'low': 15, 'medium': 8, 'high': 0}[row['stress_level']]
        s += 10 if row['sleep_duration'] >= 7 else 0
        s += 10 if row['activity_level'] != 'sedentary' else 0
        return min(max(s, 0), 100)
    
    df['fitness_score'] = df.apply(get_score, axis=1)
    
    return df

def train_v3():
    df = generate_data()
    encoders = {}
    cat_cols = ['gender', 'activity_level', 'fitness_goal', 'stress_level', 'diet_preference', 
                'living_condition', 'budget', 'medical_conditions', 'cooking_equipment', 
                'fitness_level', 'diet_type', 'intensity', 'burnout_risk']
    
    for col in cat_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        encoders[col] = le
    
    joblib.dump(encoders, 'models/encoders.joblib')
    
    features = ['age', 'height', 'weight', 'bmi', 'gender', 'activity_level', 'fitness_goal', 
                'workout_time', 'sleep_duration', 'stress_level', 'diet_preference', 
                'living_condition', 'budget', 'medical_conditions', 'cooking_equipment', 'is_exam_season']
    X = df[features]
    
    # Multi-Output Regressor (Macros + Hydration + Score)
    reg = RandomForestRegressor(n_estimators=100)
    reg.fit(X, df[['calories', 'protein', 'carbs', 'fats', 'hydration', 'fitness_score']])
    joblib.dump(reg, 'models/v3_reg.joblib')
    
    # Classifiers
    clf_burnout = RandomForestClassifier(n_estimators=100)
    clf_burnout.fit(X, df['burnout_risk'])
    joblib.dump(clf_burnout, 'models/clf_burnout.joblib')
    
    clf_fitness = RandomForestClassifier(n_estimators=100)
    clf_fitness.fit(X, df['fitness_level'])
    joblib.dump(clf_fitness, 'models/clf_fitness.joblib')
    
    clf_intensity = RandomForestClassifier(n_estimators=100)
    clf_intensity.fit(X, df['intensity'])
    joblib.dump(clf_intensity, 'models/clf_intensity.joblib')

    clf_diet = RandomForestClassifier(n_estimators=100)
    clf_diet.fit(X, df['diet_type'])
    joblib.dump(clf_diet, 'models/clf_diet.joblib')

    kmeans = KMeans(n_clusters=4, random_state=42)
    df['cluster'] = kmeans.fit_predict(X)
    joblib.dump(kmeans, 'models/kmeans.joblib')
    df.to_csv('models/clustered_data.csv', index=False)
    
    importance = dict(zip(features, reg.feature_importances_))
    joblib.dump(importance, 'models/feature_importance.joblib')
    
    print("V3 Intelligence Core Trained.")

if __name__ == "__main__":
    train_v3()
