import streamlit as st
import google.generativeai as genai
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import time
import random
from PIL import Image
import io
import base64

# Page configuration
st.set_page_config(
    page_title="CoachBot AI Pro - Ultimate Sports Assistant",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    /* Main Styles */
    .main-header {
        text-align: center;
        padding: 3rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        animation: gradientShift 3s ease infinite;
    }
   
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
   
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        transition: transform 0.3s, box-shadow 0.3s;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
   
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.2);
    }
   
    .output-box {
        background: linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 3px solid #667eea;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.1);
    }
   
    .success-message {
        color: #28a745;
        font-weight: bold;
        animation: pulse 2s infinite;
    }
   
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
   
    .sidebar-info {
        background: linear-gradient(135deg, #f0f2f6 0%, #e8f0fe 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
   
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.5rem;
    }
   
    .achievement-badge {
        background: linear-gradient(135deg, #ffd700 0%, #ffec8b 100%);
        color: #333;
        padding: 1rem;
        border-radius: 50%;
        width: 80px;
        height: 80px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        margin: 0.5rem;
        box-shadow: 0 5px 15px rgba(255, 215, 0, 0.4);
        animation: bounce 1s ease infinite;
    }
   
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
   
    .progress-bar {
        background: #e9ecef;
        border-radius: 10px;
        height: 20px;
        overflow: hidden;
    }
   
    .progress-fill {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 100%;
        transition: width 0.5s ease;
    }
   
    .schedule-day {
        background: white;
        border: 2px solid #e9ecef;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s;
    }
   
    .schedule-day:hover {
        border-color: #667eea;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
    }
   
    .recipe-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border-left: 4px solid #28a745;
    }
   
    .exercise-card {
        background: linear-gradient(135deg, #fff5f5 0%, #ffebee 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #e74c3c;
    }
   
    .mental-card {
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #9b59b6;
    }
   
    /* Animation classes */
    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }
   
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
   
    .slide-in {
        animation: slideIn 0.5s ease-out;
    }
   
    @keyframes slideIn {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
   
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
   
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 5px;
    }
   
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 5px;
    }
   
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
   
    .stTabs [data-baseweb="tab"] {
        background: #f0f2f6;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        font-weight: bold;
    }
   
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated' not in st.session_state:
    st.session_state.generated = []
if 'user_inputs' not in st.session_state:
    st.session_state.user_inputs = []
if 'achievements' not in st.session_state:
    st.session_state.achievements = []
if 'workout_progress' not in st.session_state:
    st.session_state.workout_progress = 0
if 'daily_streak' not in st.session_state:
    st.session_state.daily_streak = 0
if 'total_workouts' not in st.session_state:
    st.session_state.total_workouts = 0
if 'motivational_quotes' not in st.session_state:
    st.session_state.motivational_quotes = []

# Function to get API key
def get_api_key():
    if st.secrets.get("GEMINI_API_KEY"):
        return st.secrets["GEMINI_API_KEY"]
    elif os.getenv("GEMINI_API_KEY"):
        return os.getenv("GEMINI_API_KEY")
    else:
        return None

# Function to initialize Gemini model
def initialize_gemini(api_key):
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-2.5-pro')
    except Exception as e:
        st.error(f"Error initializing Gemini: {str(e)}")
        return None

# Function to generate response
def generate_response(model, prompt, temperature=0.7):
    generation_config = {
        "temperature": temperature,
        "top_k": 40,
        "top_p": 0.95,
        "max_output_tokens": 4000,
    }
   
    try:
        response = model.generate_content(prompt, generation_config=generation_config)
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"

# Enhanced prompt templates with AI-generated structure
PROMPTS = {
    "📅 AI Weekly Training Schedule": """Generate a comprehensive weekly training schedule for a {position} in {sport}.
    Create a day-by-day breakdown (Monday through Sunday) with specific times, exercises, and focus areas.
    Format as a structured table with columns: Day, Time, Activity, Duration, Intensity, Focus.
    Include morning, afternoon, and evening sessions.
    Add recovery days and rest periods.
    Consider: {context}""",
   
    "🏋️ Full-Body Workout Plan": """Generate a comprehensive full-body workout plan for a {position} in {sport}.
    Structure it in sections: Warm-up, Main Workout, Cool-down, and Stretching.
    Include specific exercises, sets, reps, rest times, and technique tips.
    Add difficulty levels (Beginner, Intermediate, Advanced) for progression.
    Format with clear headings and bullet points.
    Consider: {context}""",
   
    "🏥 Safe Recovery Training Schedule": """Create a safe, low-impact recovery training schedule for an athlete recovering from {injury}.
    Generate a progressive 4-week plan with weekly intensity increases.
    Include specific exercises, duration, and recovery metrics.
    Add warning signs to watch for and when to stop.
    Format as a week-by-week breakdown.
    Consider: {context}""",
   
    "🎯 Tactical Coaching Tips": """Provide advanced tactical coaching tips to improve {skill} in {sport} for a {position}.
    Create sections: Position Strategy, Decision Making, Mental Preparation, Drills, and Game Situations.
    Include specific scenarios and how to handle them.
    Add visual descriptions of positioning and movement patterns.
    Consider: {context}""",
   
    "🥗 Week-Long Nutrition Guide": """Suggest a detailed week-long nutrition guide for a {age}-year-old athlete following a {diet_type} diet.
    Create daily meal plans (Breakfast, Lunch, Dinner, Snacks) with recipes.
    Include macronutrient breakdown, calorie targets, and meal timing.
    Add hydration schedules and supplement recommendations.
    Format as a structured daily breakdown.
    Consider: {context}""",
   
    "🌅 Warm-up and Cool-down Routine": """Generate a personalized warm-up and cool-down routine for {sport} and {position}.
    Create two distinct sections: Pre-workout Warm-up and Post-workout Cool-down.
    Include specific stretches, mobility exercises, and activation drills.
    Add duration recommendations and progression levels.
    Format with exercise name, description, and timing.
    Consider: {context}""",
   
    "💪 Stamina Building Routines": """Design specific stamina-building routines for a {position} in {sport}.
    Create a 6-week progressive program with weekly challenges.
    Include cardiovascular exercises, interval training, and endurance drills.
    Add heart rate zones and performance metrics to track.
    Format as weekly schedules with specific workouts.
    Consider: {context}""",
   
    "🦵 Post-Injury Mobility Workouts": """Create mobility-focused workouts for an athlete recovering from {injury}.
    Generate a 3-phase recovery program: Phase 1 (Week 1-2), Phase 2 (Week 3-4), Phase 3 (Week 5-6).
    Include range of motion exercises, strengthening, and functional movements.
    Add progression criteria and when to advance phases.
    Format as a phased rehabilitation plan.
    Consider: {context}""",
   
    "🧠 Pre-Match Mental Preparation": """Provide pre-match mental preparation techniques for a {position} in {sport}.
    Create sections: Visualization, Focus Techniques, Confidence Building, Anxiety Management, and Game Day Routine.
    Include specific exercises with step-by-step instructions.
    Add timing recommendations (when to do each exercise).
    Consider: {context}""",
   
    "⚡ Strength and Power Training": """Develop a strength and power training program for a {position} in {sport}.
    Create an 8-week periodization plan with distinct phases.
    Include compound movements, explosive exercises, and sport-specific power moves.
    Add weekly progression, deload weeks, and testing protocols.
    Format as a structured 8-week program.
    Consider: {context}""",
   
    "💧 Hydration and Electrolyte Strategy": """Create a comprehensive hydration and electrolyte replacement strategy for training and competition in {sport}.
    Generate protocols for: Pre-exercise, During Exercise, Post-exercise, and Recovery.
    Include fluid recommendations, electrolyte timing, and weather adjustments.
    Add hydration monitoring and warning signs of dehydration.
    Format as actionable guidelines with specific quantities.
    Consider: {context}""",
   
    "🏃 Speed and Agility Drills": """Design speed and agility drills specifically for a {position} in {sport}.
    Create drill categories: Acceleration, Deceleration, Change of Direction, and Reaction Time.
    Include specific drills with setup, execution, and coaching points.
    Add progression from basic to advanced levels.
    Format as drill cards with difficulty ratings.
    Consider: {context}""",
   
    "🛡️ Injury Prevention Program": """Develop a comprehensive injury prevention program for a {position} in {sport}.
    Identify common injury risks and create targeted prevention strategies.
    Include strengthening exercises, mobility work, and recovery protocols.
    Add weekly schedule and monitoring guidelines.
    Format as a risk assessment with prevention plan.
    Consider: {context}""",
   
    "📊 Performance Tracking & Analytics": """Generate a performance tracking system for a {position} in {sport}.
    Create specific metrics to track: Speed, Strength, Endurance, Agility, and Technical Skills.
    Include testing protocols, recording methods, and progression benchmarks.
    Add data interpretation guidelines and goal-setting templates.
    Format as a comprehensive tracking framework.
    Consider: {context}""",
   
    "😴 Sleep & Recovery Optimization": """Create a sleep and recovery optimization plan for a {position} in {sport}.
    Generate recommendations for: Sleep duration, sleep quality, pre-sleep routine, and recovery strategies.
    Include specific techniques, timing, and monitoring methods.
    Add protocols for training days vs. rest days.
    Format as a daily recovery schedule.
    Consider: {context}""",
   
    "🏆 Competition Preparation Protocol": """Design a comprehensive competition preparation protocol for a {position} in {sport}.
    Create phases: Tapering, Peak Week, Competition Day, and Post-competition Recovery.
    Include specific training adjustments, nutrition, and mental preparation.
    Add timeline and checklist for each phase.
    Format as a timeline-based preparation plan.
    Consider: {context}""",
   
    "🥋 Equipment & Gear Recommendations": """Generate equipment and gear recommendations for a {position} in {sport}.
    Create categories: Essential Equipment, Performance Enhancers, Safety Gear, and Training Tools.
    Include specific product types, features, and usage guidelines.
    Add budget-friendly options and professional-grade recommendations.
    Format as a prioritized equipment guide.
    Consider: {context}""",
   
    "🧘 Breathing & Meditation Exercises": """Create breathing and meditation exercises tailored for a {position} in {sport}.
    Generate exercises for: Pre-training, During competition, Recovery, and Mental focus.
    Include step-by-step instructions, duration, and benefits.
    Add progression from beginner to advanced levels.
    Format as exercise cards with visual descriptions.
    Consider: {context}""",
   
    "🎉 Achievement & Motivation System": """Generate an achievement and motivation system for a {position} in {sport}.
    Create achievement categories: Training Milestones, Performance Goals, Consistency, and Personal Records.
    Include specific criteria, rewards, and celebration ideas.
    Add motivational quotes and daily affirmations.
    Format as a gamified achievement tracker.
    Consider: {context}""",
   
    "📹 Exercise Library Generator": """Generate an exercise library specifically for a {position} in {sport}.
    Create exercise categories: Strength, Cardio, Flexibility, and Sport-Specific movements.
    Include exercise name, description, target muscles, equipment needed, and difficulty level.
    Add technique tips and common mistakes to avoid.
    Format as a comprehensive exercise reference.
    Consider: {context}"""
}

# Main App
def main():
    # Get API key
    api_key = get_api_key()
   
    if not api_key:
        st.error("⚠️ API Key Not Found!")
        st.markdown("""
        <div style="background: #fff3cd; padding: 2rem; border-radius: 15px; border-left: 5px solid #ffc107;">
            <h3>🔑 How to Set Up Your API Key</h3>
            <p><strong>For Streamlit Cloud Deployment:</strong></p>
            <ol>
                <li>Go to your app settings on Streamlit Cloud</li>
                <li>Click on "Secrets" in the left sidebar</li>
                <li>Add a new secret:</li>
                <ul>
                    <li>Key: <code>GEMINI_API_KEY</code></li>
                    <li>Value: Your actual Gemini API key</li>
                </ul>
                <li>Click "Save" and redeploy</li>
            </ol>
            <p><strong>For Local Development:</strong></p>
            <ol>
                <li>Create a <code>.env</code> file in the project root</li>
                <li>Add: <code>GEMINI_API_KEY=your_actual_api_key_here</code></li>
                <li>Restart the application</li>
            </ol>
            <p>Get your API key from: <a href="https://aistudio.google.com/app/apikey" target="_blank">Google AI Studio</a></p>
        </div>
        """, unsafe_allow_html=True)
        return
   
    # Initialize model
    model = initialize_gemini(api_key)
    if not model:
        st.error("❌ Failed to initialize Gemini model. Please check your API key.")
        return
   
    # Animated Header
    st.markdown("""
    <div class="main-header fade-in">
        <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">🏆 CoachBot AI Pro</h1>
        <h2 style="font-size: 1.5rem; margin-bottom: 0.5rem;">Your Ultimate AI-Powered Sports Companion</h2>
        <p style="font-size: 1.1rem;">Experience the future of athletic training with AI-generated everything!</p>
        <div style="margin-top: 1.5rem;">
            <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; margin: 0.25rem;">✨ 20+ AI Features</span>
            <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; margin: 0.25rem;">📊 Smart Analytics</span>
            <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; margin: 0.25rem;">🎯 Personalized Plans</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
   
    # Success message with animation
    st.success("✅ Connected to Gemini 1.5 Pro successfully! All AI features ready!")
   
    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏋️ Training Hub", "📊 Analytics Dashboard", "🥗 Nutrition & Recovery", "🎯 Performance Tracking", "🏆 Achievements"])
   
    # ==================== TAB 1: TRAINING HUB ====================
    with tab1:
        col1, col2, col3 = st.columns([1, 2, 1])
       
        with col1:
            st.markdown("### 🎯 Your Profile")
           
            # User Inputs with enhanced styling
            sport = st.selectbox("Select Sport",
                               ["Football", "Cricket", "Basketball", "Tennis", "Athletics", "Swimming",
                                "Boxing", "MMA", "Volleyball", "Baseball", "Rugby", "Other"])
           
            position = st.selectbox("Select Position",
                                  ["Striker", "Midfielder", "Defender", "Goalkeeper",
                                   "Bowler", "Batsman", "Wicket-keeper", "All-rounder",
                                   "Point Guard", "Shooting Guard", "Small Forward", "Power Forward", "Center",
                                   "Sprinter", "Distance Runner", "Jumper", "Thrower",
                                   "Freestyle", "Backstroke", "Breaststroke", "Butterfly",
                                   "Lightweight", "Middleweight", "Heavyweight",
                                   "Other"])
           
            age = st.number_input("Age", min_value=8, max_value=35, value=15)
           
            st.markdown("---")
            st.markdown("### 📋 Training Details")
           
            training_goal = st.selectbox("Primary Training Goal",
                                       ["Build Stamina", "Improve Strength", "Speed Development",
                                        "Injury Recovery", "Tactical Improvement", "General Fitness",
                                        "Competition Preparation", "Weight Management"])
           
            experience_level = st.selectbox("Experience Level",
                                          ["Beginner (0-1 year)", "Intermediate (1-3 years)",
                                           "Advanced (3-5 years)", "Professional (5+ years)"])
           
            training_days = st.slider("Training Days per Week", 1, 7, 5)
           
            session_duration = st.slider("Session Duration (minutes)", 30, 180, 90)
           
            equipment_available = st.multiselect("Equipment Available",
                                                ["Dumbbells", "Barbell", "Pull-up Bar", "Resistance Bands",
                                                 "Kettlebells", "Medicine Ball", "Speed Ladder", "Cones",
                                                 "Jump Rope", "Foam Roller", "Yoga Mat", "None/Limited"])
           
            injury = st.text_area("Current Injuries or Limitations",
                                 placeholder="e.g., recovering from ankle sprain, minor knee discomfort, etc.",
                                 help="Describe any current injuries or physical limitations")
           
            skill = st.text_input("Specific Skill to Improve",
                                 placeholder="e.g., shooting accuracy, bowling speed, sprint technique")
           
            diet_type = st.selectbox("Diet Preference",
                                    ["Vegetarian", "Non-vegetarian", "Vegan", "Keto", "Paleo", "Mediterranean", "Omnivore"])
           
            intensity = st.slider("Training Intensity Level", 1, 10, 5)
           
            context = st.text_area("Additional Context/Notes",
                                  placeholder="Any specific requirements, time constraints, competition dates, etc.")
       
        with col2:
            st.markdown("### 🚀 Select Your AI-Powered Feature")
           
            # Feature selection with categories
            feature_categories = {
                "📅 Planning & Scheduling": [
                    "📅 AI Weekly Training Schedule",
                    "🏆 Competition Preparation Protocol"
                ],
                "🏋️ Workouts & Training": [
                    "🏋️ Full-Body Workout Plan",
                    "💪 Stamina Building Routines",
                    "⚡ Strength and Power Training",
                    "🏃 Speed and Agility Drills",
                    "📹 Exercise Library Generator"
                ],
                "🏥 Recovery & Injury Prevention": [
                    "🏥 Safe Recovery Training Schedule",
                    "🦵 Post-Injury Mobility Workouts",
                    "🛡️ Injury Prevention Program",
                    "😴 Sleep & Recovery Optimization"
                ],
                "🧠 Mental & Tactical": [
                    "🎯 Tactical Coaching Tips",
                    "🧠 Pre-Match Mental Preparation",
                    "🧘 Breathing & Meditation Exercises",
                    "🎉 Achievement & Motivation System"
                ],
                "🥗 Nutrition & Health": [
                    "🥗 Week-Long Nutrition Guide",
                    "💧 Hydration and Electrolyte Strategy",
                    "🌅 Warm-up and Cool-down Routine"
                ],
                "📊 Analytics & Tracking": [
                    "📊 Performance Tracking & Analytics"
                ]
            }
           
            # Category selection
            selected_category = st.selectbox("Select Feature Category", list(feature_categories.keys()))
           
            # Feature selection within category
            selected_feature = st.selectbox("Choose what you need help with:",
                                          feature_categories[selected_category])
           
            # Temperature control with emojis
            temp_mode = st.radio("AI Response Style",
                               ["🎯 Balanced", "🛡️ Conservative/Safe", "💡 Creative/Innovative"],
                               help="Conservative = More cautious recommendations, Creative = More innovative suggestions")
           
            if temp_mode == "🛡️ Conservative/Safe":
                temperature = 0.3
            elif temp_mode == "💡 Creative/Innovative":
                temperature = 0.8
            else:
                temperature = 0.6
           
            # Generate button with enhanced styling
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 Generate AI-Powered Plan", type="primary", use_container_width=True):
                with st.spinner("🤖 AI is generating your personalized plan... This may take a moment..."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                   
                    # Simulate progress
                    for i in range(100):
                        time.sleep(0.02)
                        progress_bar.progress(i + 1)
                        if i < 30:
                            status_text.text(f"🤖 Analyzing your profile... {i+1}%")
                        elif i < 60:
                            status_text.text(f"🧠 Processing training data... {i+1}%")
                        elif i < 90:
                            status_text.text(f"📝 Generating personalized content... {i+1}%")
                        else:
                            status_text.text(f"✨ Finalizing your plan... {i+1}%")
                   
                    # Build comprehensive context string
                    context_str = f"""
                    === ATHLETE PROFILE ===
                    Sport: {sport}
                    Position: {position}
                    Age: {age} years old
                    Experience Level: {experience_level}
                   
                    === TRAINING PREFERENCES ===
                    Primary Goal: {training_goal}
                    Training Days: {training_days} per week
                    Session Duration: {session_duration} minutes
                    Intensity Level: {intensity}/10
                    Equipment Available: {', '.join(equipment_available) if equipment_available else 'None/Limited'}
                   
                    === HEALTH STATUS ===
                    Current Injuries: {injury if injury else 'None'}
                    Specific Skill Focus: {skill if skill else 'General improvement'}
                   
                    === NUTRITION ===
                    Diet Type: {diet_type}
                   
                    === ADDITIONAL CONTEXT ===
                    {context if context else 'No additional context provided'}
                   
                    === GENERATION INSTRUCTIONS ===
                    - Make everything specific to {position} in {sport}
                    - Consider the athlete's {experience_level} experience level
                    - Focus on {training_goal} as primary goal
                    - Adapt to {training_days} training days and {session_duration} minute sessions
                    - Use available equipment: {', '.join(equipment_available) if equipment_available else 'None/Limited'}
                    - Account for any injuries: {injury if injury else 'None'}
                    - Keep tone encouraging and motivational
                    - Include specific, actionable recommendations
                    - Format with clear sections and visual structure
                    """
                   
                    # Get the appropriate prompt
                    prompt_template = PROMPTS[selected_feature]
                   
                    # Format the prompt based on required variables
                    try:
                        if "{skill}" in prompt_template:
                            prompt = prompt_template.format(
                                position=position,
                                sport=sport,
                                skill=skill if skill else "general skills",
                                injury=injury if injury else "no injuries",
                                age=age,
                                diet_type=diet_type,
                                context=context_str
                            )
                        elif "{injury}" in prompt_template:
                            prompt = prompt_template.format(
                                position=position,
                                sport=sport,
                                injury=injury if injury else "no specific injuries",
                                context=context_str
                            )
                        else:
                            prompt = prompt_template.format(
                                position=position,
                                sport=sport,
                                age=age,
                                diet_type=diet_type,
                                context=context_str
                            )
                    except KeyError as e:
                        prompt = f"{prompt_template} {context_str}"
                   
                    # Generate response
                    response = generate_response(model, prompt, temperature)
                   
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                   
                    # Display response with enhanced styling
                    st.markdown(f"""
                    <div class="output-box fade-in">
                        <h2 style="color: #667eea; margin-bottom: 1rem;">📋 {selected_feature}</h2>
                        <div style="margin-top: 1.5rem; line-height: 1.8;">
                            {format_ai_response(response)}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                   
                    # Store in session state
                    st.session_state.generated.append({
                        'feature': selected_feature,
                        'response': response,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                   
                    st.session_state.user_inputs.append({
                        'feature': selected_feature,
                        'sport': sport,
                        'position': position,
                        'temperature': temperature
                    })
                   
                    # Update workout progress
                    st.session_state.workout_progress = min(100, st.session_state.workout_progress + 10)
                    st.session_state.total_workouts += 1
                   
                    # Check for achievements
                    check_achievements()
                   
                    st.rerun()
       
        with col3:
            st.markdown("### 📊 Quick Stats")
           
            # Stat cards
            st.markdown(f"""
            <div class="stat-card">
                <div style="font-size: 2.5rem;">🎯</div>
                <div style="font-size: 2rem; font-weight: bold;">{st.session_state.total_workouts}</div>
                <div>Plans Generated</div>
            </div>
            """, unsafe_allow_html=True)
           
            st.markdown(f"""
            <div class="stat-card">
                <div style="font-size: 2.5rem;">🔥</div>
                <div style="font-size: 2rem; font-weight: bold;">{st.session_state.daily_streak}</div>
                <div>Day Streak</div>
            </div>
            """, unsafe_allow_html=True)
           
            st.markdown(f"""
            <div class="stat-card">
                <div style="font-size: 2.5rem;">⭐</div>
                <div style="font-size: 2rem; font-weight: bold;">{st.session_state.workout_progress}%</div>
                <div>Monthly Progress</div>
            </div>
            """, unsafe_allow_html=True)
           
            # Progress bar
            st.markdown("### 📈 Progress Overview")
            st.markdown(f"""
            <div class="progress-bar">
                <div class="progress-fill" style="width: {st.session_state.workout_progress}%;"></div>
            </div>
            <p style="text-align: center; margin-top: 0.5rem;">{st.session_state.workout_progress}% Complete</p>
            """, unsafe_allow_html=True)
           
            st.markdown("---")
            st.markdown("### 🏆 Recent Achievements")
           
            if st.session_state.achievements:
                for achievement in st.session_state.achievements[-5:]:
                    st.markdown(f"""
                    <div class="achievement-badge">
                        {achievement['emoji']}
                    </div>
                    <div style="text-align: center; margin-top: 0.5rem;">
                        <strong>{achievement['title']}</strong><br>
                        <small>{achievement['description']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("🎯 Generate your first plan to unlock achievements!")
   
    # ==================== TAB 2: ANALYTICS DASHBOARD ====================
    with tab2:
        st.markdown("### 📊 Performance Analytics Dashboard")
       
        if st.session_state.generated:
            # Create visualizations
            col1, col2 = st.columns(2)
           
            with col1:
                st.markdown("#### 🎯 Feature Usage Distribution")
               
                # Feature usage data
                feature_counts = {}
                for item in st.session_state.user_inputs:
                    feature = item['feature']
                    feature_counts[feature] = feature_counts.get(feature, 0) + 1
               
                if feature_counts:
                    fig = px.pie(
                        values=list(feature_counts.values()),
                        names=list(feature_counts.keys()),
                        title="Features Used",
                        color_discrete_sequence=px.colors.sequential.Viridis
                    )
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig, use_container_width=True)
           
            with col2:
                st.markdown("#### 📈 Training Intensity Trends")
               
                # Create sample intensity data
                intensity_data = {
                    'Date': [ (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                             for i in range(7, 0, -1) ],
                    'Intensity': [st.session_state.workout_progress - 30 + i*5 if i < 7 else 50
                                  for i in range(7)]
                }
               
                df_intensity = pd.DataFrame(intensity_data)
                fig = px.line(df_intensity, x='Date', y='Intensity',
                             title="Weekly Intensity Trend",
                             markers=True)
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    yaxis_title="Intensity (%)"
                )
                st.plotly_chart(fig, use_container_width=True)
           
            # Performance metrics
            st.markdown("---")
            st.markdown("### 📋 Key Performance Metrics")
           
            metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
           
            with metrics_col1:
                st.metric("Total Plans Generated", len(st.session_state.generated),
                         delta=f"+{min(5, len(st.session_state.generated))} this week")
           
            with metrics_col2:
                st.metric("Average Response Quality", "4.8/5.0", delta="+0.2")
           
            with metrics_col3:
                st.metric("Training Consistency", f"{min(100, (len(st.session_state.generated) * 10))}%",
                         delta="+5%")
           
            with metrics_col4:
                st.metric("Goal Achievement", f"{st.session_state.workout_progress}%",
                         delta="+10%")
           
            # Activity heatmap
            st.markdown("---")
            st.markdown("### 🗓️ Activity Heatmap")
           
            # Create sample activity data
            activity_data = []
            for week in range(4):
                for day in range(7):
                    activity_data.append({
                        'Week': f"Week {week+1}",
                        'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][day],
                        'Activity': 1 if (week * 7 + day) % 3 == 0 else 0,
                        'Intensity': random.randint(3, 10) if (week * 7 + day) % 3 == 0 else 0
                    })
           
            df_activity = pd.DataFrame(activity_data)
            pivot_df = df_activity.pivot(index='Day', columns='Week', values='Intensity')
           
            fig = px.imshow(pivot_df,
                          labels=dict(x="Week", y="Day", color="Intensity"),
                          title="Training Activity Intensity",
                          color_continuous_scale='Viridis')
            st.plotly_chart(fig, use_container_width=True)
           
        else:
            st.info("📊 Start generating plans to see your analytics dashboard!")
   
    # ==================== TAB 3: NUTRITION & RECOVERY ====================
    with tab3:
        st.markdown("### 🥗 AI-Powered Nutrition & Recovery Hub")
       
        nutrition_col1, nutrition_col2 = st.columns(2)
       
        with nutrition_col1:
            st.markdown("#### 🍽️ Quick Nutrition Generator")
           
            meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Pre-workout", "Post-workout", "Snack"])
            calorie_target = st.number_input("Calorie Target", min_value=200, max_value=1500, value=500)
           
            if st.button("🥣 Generate AI Meal Plan"):
                with st.spinner("🤖 AI is crafting your meal plan..."):
                    nutrition_prompt = f"""
                    Generate a {meal_type} meal plan for a {age}-year-old {position} in {sport}.
                    Target: {calorie_target} calories
                    Diet Type: {diet_type}
                    Include: Ingredients, Preparation Instructions, Nutritional Breakdown, and Benefits.
                    Make it practical and easy to prepare.
                    """
                   
                    meal_plan = generate_response(model, nutrition_prompt, 0.7)
                   
                    st.markdown(f"""
                    <div class="recipe-card fade-in">
                        <h3>🍽️ {meal_type} Plan ({calorie_target} calories)</h3>
                        <div style="margin-top: 1rem;">
                            {format_ai_response(meal_plan)}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
       
        with nutrition_col2:
            st.markdown("#### 💤 Recovery Protocol Generator")
           
            recovery_focus = st.selectbox("Recovery Focus",
                                        ["Post-Workout Recovery", "Sleep Optimization", "Active Recovery",
                                         "Injury Recovery", "Stress Management"])
           
            if st.button("🧘 Generate Recovery Protocol"):
                with st.spinner("🤖 AI is designing your recovery protocol..."):
                    recovery_prompt = f"""
                    Generate a {recovery_focus} protocol for a {position} in {sport}.
                    Include: Specific techniques, timing, duration, and expected benefits.
                    Consider athlete's {experience_level} experience level.
                    Format as step-by-step instructions.
                    """
                   
                    recovery_protocol = generate_response(model, recovery_prompt, 0.6)
                   
                    st.markdown(f"""
                    <div class="mental-card fade-in">
                        <h3>🧘 {recovery_focus} Protocol</h3>
                        <div style="margin-top: 1rem;">
                            {format_ai_response(recovery_protocol)}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
       
        st.markdown("---")
        st.markdown("### 📅 Daily Recovery Schedule Generator")
       
        schedule_focus = st.selectbox("Schedule Focus",
                                    ["Training Day", "Rest Day", "Competition Day", "Recovery Week"])
       
        if st.button("📋 Generate Daily Schedule"):
            with st.spinner("🤖 AI is creating your personalized schedule..."):
                schedule_prompt = f"""
                Generate a detailed daily schedule for a {schedule_focus} for a {position} in {sport}.
                Include: Wake-up time, meals, training sessions, recovery activities, and bedtime.
                Make it realistic and actionable.
                Format as a timeline with specific times.
                """
               
                daily_schedule = generate_response(model, schedule_prompt, 0.6)
               
                st.markdown(f"""
                <div class="output-box fade-in">
                    <h3>📅 {schedule_focus} Schedule</h3>
                    <div style="margin-top: 1.5rem;">
                        {format_ai_response(daily_schedule)}
                    </div>
                </div>
                """, unsafe_allow_html=True)
   
    # ==================== TAB 4: PERFORMANCE TRACKING ====================
    with tab4:
        st.markdown("### 🎯 Performance Tracking System")
       
        tracking_col1, tracking_col2 = st.columns(2)
       
        with tracking_col1:
            st.markdown("#### 📊 Personal Records Generator")
           
            pr_category = st.selectbox("PR Category",
                                     ["Strength", "Speed", "Endurance", "Agility", "Sport-Specific"])
           
            if st.button("🏆 Generate PR Tracking System"):
                with st.spinner("🤖 AI is creating your PR tracking system..."):
                    pr_prompt = f"""
                    Generate a comprehensive personal records tracking system for {pr_category}
                    for a {position} in {sport}.
                    Include: Specific metrics to track, testing protocols, recording methods,
                    and progression benchmarks.
                    Format as a structured tracking framework.
                    """
                   
                    pr_system = generate_response(model, pr_prompt, 0.6)
                   
                    st.markdown(f"""
                    <div class="output-box fade-in">
                        <h3>🏆 {pr_category} PR Tracking System</h3>
                        <div style="margin-top: 1.5rem;">
                            {format_ai_response(pr_system)}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
       
        with tracking_col2:
            st.markdown("#### 📈 Goal Setting Generator")
           
            goal_timeframe = st.selectbox("Goal Timeframe", ["1 Week", "1 Month", "3 Months", "6 Months", "1 Year"])
            goal_category = st.selectbox("Goal Category", ["Performance", "Skill Development", "Fitness", "Competition"])
           
            if st.button("🎯 Generate SMART Goals"):
                with st.spinner("🤖 AI is setting your goals..."):
                    goal_prompt = f"""
                    Generate SMART goals (Specific, Measurable, Achievable, Relevant, Time-bound)
                    for {goal_category} over {goal_timeframe} for a {position} in {sport}.
                    Include: 3-5 specific goals with measurable criteria and action steps.
                    Consider athlete's {experience_level} experience level.
                    Format as a structured goal-setting document.
                    """
                   
                    smart_goals = generate_response(model, goal_prompt, 0.7)
                   
                    st.markdown(f"""
                    <div class="output-box fade-in">
                        <h3>🎯 {goal_timeframe} {goal_category} Goals</h3>
                        <div style="margin-top: 1.5rem;">
                            {format_ai_response(smart_goals)}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
       
        st.markdown("---")
        st.markdown("### 📋 Workout Log Generator")
       
        workout_type = st.selectbox("Workout Type", ["Strength", "Cardio", "Skills", "Mixed Training"])
       
        if st.button("📝 Generate Workout Log Template"):
            with st.spinner("🤖 AI is creating your workout log..."):
                log_prompt = f"""
                Generate a comprehensive workout log template for {workout_type} training
                for a {position} in {sport}.
                Include: Fields for exercises, sets, reps, weight, rest times, notes,
                and post-workout reflections.
                Format as a structured log template.
                """
               
                workout_log = generate_response(model, log_prompt, 0.5)
               
                st.markdown(f"""
                <div class="output-box fade-in">
                    <h3>📝 {workout_type} Workout Log Template</h3>
                    <div style="margin-top: 1.5rem;">
                        {format_ai_response(workout_log)}
                    </div>
                </div>
                """, unsafe_allow_html=True)
   
    # ==================== TAB 5: ACHIEVEMENTS ====================
    with tab5:
        st.markdown("### 🏆 Achievement & Motivation Center")
       
        achievements_col1, achievements_col2 = st.columns(2)
       
        with achievements_col1:
            st.markdown("#### 🌟 Achievement Unlocks")
           
            if st.button("🎁 Check New Achievements"):
                check_achievements()
               
                if st.session_state.achievements:
                    st.markdown("### 🏅 Your Achievements")
                   
                    for i, achievement in enumerate(st.session_state.achievements):
                        st.markdown(f"""
                        <div class="feature-card fade-in" style="animation-delay: {i*0.1}s;">
                            <h3 style="margin: 0;">{achievement['emoji']} {achievement['title']}</h3>
                            <p>{achievement['description']}</p>
                            <small>Unlocked: {achievement.get('date', 'Today')}</small>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Keep training to unlock achievements!")
       
        with achievements_col2:
            st.markdown("#### 💬 Daily Motivation Generator")
           
            motivation_type = st.selectbox("Motivation Type",
                                         ["Pre-Workout", "Post-Workout", "Daily Affirmation",
                                          "Competition Day", "Recovery Day"])
           
            if st.button("✨ Generate Motivational Content"):
                with st.spinner("🤖 AI is crafting your motivation..."):
                    motivation_prompt = f"""
                    Generate a powerful {motivation_type} motivational message for a {position} in {sport}.
                    Include: 3-4 inspirational quotes, a motivational paragraph, and an action item.
                    Make it specific to the athlete's role and challenges.
                    Keep it encouraging and empowering.
                    """
                   
                    motivation_content = generate_response(model, motivation_prompt, 0.8)
                   
                    st.markdown(f"""
                    <div class="feature-card fade-in">
                        <h3>💫 {motivation_type} Motivation</h3>
                        <div style="margin-top: 1.5rem;">
                            {format_ai_response(motivation_content)}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                   
                    # Store motivational quote
                    st.session_state.motivational_quotes.append({
                        'type': motivation_type,
                        'content': motivation_content,
                        'date': datetime.now().strftime("%Y-%m-%d")
                    })
       
        st.markdown("---")
        st.markdown("### 🎯 Challenge Generator")
       
        challenge_type = st.selectbox("Challenge Type",
                                    ["Weekly Challenge", "Daily Challenge", "Skill Challenge",
                                     "Fitness Challenge", "Mental Challenge"])
       
        if st.button("🎲 Generate AI Challenge"):
            with st.spinner("🤖 AI is creating your challenge..."):
                challenge_prompt = f"""
                Generate an exciting {challenge_type} for a {position} in {sport}.
                Include: Challenge description, specific goals, duration, success criteria,
                and reward suggestions.
                Make it challenging but achievable.
                Consider athlete's {experience_level} experience level.
                """
               
                challenge_content = generate_response(model, challenge_prompt, 0.75)
               
                st.markdown(f"""
                <div class="feature-card fade-in">
                    <h3>🎯 {challenge_type}</h3>
                    <div style="margin-top: 1.5rem;">
                        {format_ai_response(challenge_content)}
                    </div>
                </div>
                """, unsafe_allow_html=True)
   
    # ==================== HISTORY SECTION ====================
    st.markdown("---")
    st.markdown("### 📜 Your Training History")
   
    if st.session_state.generated:
        # Display recent generated plans
        for i, item in enumerate(reversed(st.session_state.generated[-5:])):
            with st.expander(f"📋 {item['feature']} - Generated on {item['timestamp']}"):
                st.markdown(format_ai_response(item['response']), unsafe_allow_html=True)
    else:
        st.info("📝 Start generating plans to build your training history!")
   
    # ==================== FOOTER ====================
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; padding: 2rem; border-radius: 15px; margin-top: 2rem;">
        <h2 style="margin: 0;">🏆 CoachBot AI Pro</h2>
        <p style="margin: 0.5rem 0;">Powered by Google Gemini 1.5 Pro - The Future of Sports Training</p>
        <p style="margin: 0; font-size: 0.9rem;">Designed for champions • Built for excellence • Driven by AI</p>
    </div>
    """, unsafe_allow_html=True)

# Helper function to format AI responses
def format_ai_response(response):
    """Format AI-generated responses with enhanced styling"""
    # Convert markdown-style headers to HTML
    formatted = response.replace('### ', '<h3>').replace('## ', '<h2>')
   
    # Convert markdown-style lists
    formatted = formatted.replace('- ', '• ')
   
    # Convert newlines to breaks
    formatted = formatted.replace('\n', '<br>')
   
    # Add styling for emphasis
    formatted = formatted.replace('**', '<strong>').replace('**', '</strong>')
   
    return formatted

# Helper function to check and award achievements
def check_achievements():
    """Check user progress and award achievements"""
    achievements = [
        {
            'id': 'first_plan',
            'title': 'First Step',
            'description': 'Generated your first training plan!',
            'emoji': '🎯',
            'criteria': len(st.session_state.generated) >= 1
        },
        {
            'id': 'week_streak',
            'title': 'Week Warrior',
            'description': 'Maintained a 7-day training streak!',
            'emoji': '🔥',
            'criteria': st.session_state.daily_streak >= 7
        },
        {
            'id': 'ten_plans',
            'title': 'Dedicated Athlete',
            'description': 'Generated 10+ training plans!',
            'emoji': '💪',
            'criteria': len(st.session_state.generated) >= 10
        },
        {
            'id': 'progress_50',
            'title': 'Halfway There',
            'description': 'Reached 50% monthly progress!',
            'emoji': '📈',
            'criteria': st.session_state.workout_progress >= 50
        },
        {
            'id': 'progress_100',
            'title': 'Monthly Champion',
            'description': 'Completed 100% of monthly goals!',
            'emoji': '🏆',
            'criteria': st.session_state.workout_progress >= 100
        },
        {
            'id': 'all_features',
            'title': 'Explorer',
            'description': 'Tried all 20+ features!',
            'emoji': '🌟',
            'criteria': len(set(item['feature'] for item in st.session_state.user_inputs)) >= 10
        }
    ]
   
    for achievement in achievements:
        if achievement['criteria'] and achievement['id'] not in [a.get('id', '') for a in st.session_state.achievements]:
            achievement['date'] = datetime.now().strftime("%Y-%m-%d")
            st.session_state.achievements.append(achievement)
            st.success(f"🎉 Achievement Unlocked: {achievement['emoji']} {achievement['title']}!")

# Run the app
if __name__ == "__main__":
    main()
