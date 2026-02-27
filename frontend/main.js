document.getElementById('fitness-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    // Explicitly handle all numeric production fields
    const numericFields = ['age', 'height', 'weight', 'workout_time', 'sleep_duration'];
    numericFields.forEach(field => data[field] = Number(data[field]));

    // Loading state
    const btn = e.target.querySelector('button');
    const originalText = btn.innerText;
    btn.innerText = "Processing Intelligence Architecture...";
    btn.disabled = true;

    try {
        const response = await fetch('http://localhost:5000/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        if (result.error) throw new Error(result.error);
        displayIntelligenceBlueprint(result);
    } catch (err) {
        alert("ML Engine Offline: " + err.message);
        console.error(err);
    } finally {
        btn.innerText = originalText;
        btn.disabled = false;
    }
});

function displayIntelligenceBlueprint(data) {
    const resultsSection = document.getElementById('results-section');
    resultsSection.style.display = 'block';

    // Visual Entrance
    const cards = resultsSection.querySelectorAll('.card');
    cards.forEach((card, i) => {
        card.classList.remove('reveal');
        setTimeout(() => card.classList.add('reveal'), i * 150);
    });

    resultsSection.scrollIntoView({ behavior: 'smooth' });

    // Persona & Score
    document.getElementById('persona-val').innerText = data.persona;
    document.getElementById('strategy-val').innerText = data.strategy;
    document.getElementById('score-val').innerText = data.fitness_score;
    document.getElementById('score-factors').innerHTML = data.score_factors
        .map(f => `<div class="status-badge" style="font-size:0.6rem; background:rgba(0,242,254,0.2); color:var(--primary);">${f}</div>`).join('');

    // Summary Card
    document.getElementById('bmi-val').innerText = data.bmi_summary.bmi;
    document.getElementById('bmi-cat').innerText = data.bmi_summary.category;
    document.getElementById('level-val').innerText = data.predictions.fitness_level;
    document.getElementById('type-val').innerText = data.predictions.diet_type;

    // Macros
    document.getElementById('cal-val').innerText = data.predictions.macros.calories;
    document.getElementById('p-val').innerText = data.predictions.macros.protein;
    document.getElementById('c-val').innerText = data.predictions.macros.carbs;
    document.getElementById('f-val').innerText = data.predictions.macros.fats;

    // Explainability
    document.getElementById('logic-val').innerText = data.explainability.logic;
    document.getElementById('impact-val').innerHTML = data.explainability.top_impact_features
        .map(f => `<div class="activity-tag">${f}</div>`).join('');

    // Workout Plan
    const workoutList = document.getElementById('workout-list');
    workoutList.innerHTML = data.plans.workout.map(item => `
        <div class="plan-item">
            <span class="day-badge">${item.day}</span>
            <div class="activity-tags">
                ${item.activities.map(a => `<span class="activity-tag">${a}</span>`).join('')}
            </div>
            <small style="color:var(--text-dim)">Intensity: ${item.intensity}</small>
        </div>
    `).join('');
    document.getElementById('work-swap').innerText = data.plans.smart_substitutions.workout;

    // Diet Plan
    const dietList = document.getElementById('diet-list');
    const meals = ['Breakfast', 'Lunch', 'Snack', 'Dinner'];
    dietList.innerHTML = meals.map(meal => `
        <div class="plan-item">
            <strong>${meal}</strong>
            <p>${data.plans.diet[meal]}</p>
        </div>
    `).join('');
    document.getElementById('meal-swap').innerText = data.plans.smart_substitutions.meal;

    // Shopping List
    document.getElementById('shopping-list').innerHTML = data.plans.shopping_list
        .map(item => `<span class="activity-tag">${item}</span>`).join('');
}
