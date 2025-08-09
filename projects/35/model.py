import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt
import seaborn as sns

# Load MIMIC-IV-ED tables (replace with your actual file paths)
def load_mimic_ed_data(data_dir):
    """
    Load core MIMIC-IV-ED tables needed for patient flow analysis
    """
    try:
        edstays = pd.read_csv(f'{data_dir}/edstays.csv')
        triage = pd.read_csv(f'{data_dir}/triage.csv')
        vitalsign = pd.read_csv(f'{data_dir}/vitalsign.csv')
        diagnosis = pd.read_csv(f'{data_dir}/diagnosis.csv')
        
        print("Data loaded successfully")
        return edstays, triage, vitalsign, diagnosis
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None, None, None

# Preprocess and merge data
def preprocess_data(edstays, triage, vitalsign, diagnosis):
    """
    Clean and merge MIMIC-IV-ED tables for analysis
    """
    # Merge triage and vital signs with ED stays
    df = pd.merge(edstays, triage, on=['subject_id', 'stay_id'], how='left')
    df = pd.merge(df, vitalsign, on=['subject_id', 'stay_id'], how='left')
    
    # Calculate length of stay in minutes
    df['intime'] = pd.to_datetime(df['intime'])
    df['outtime'] = pd.to_datetime(df['outtime'])
    df['los_minutes'] = (df['outtime'] - df['intime']).dt.total_seconds() / 60
    
    # Add diagnostic categories (simplified example)
    df = pd.merge(df, diagnosis[['stay_id', 'icd_code', 'icd_version']], 
                 on='stay_id', how='left')
    
    # Create urgency categories based on vital signs
    df['urgency'] = np.where(
        (df['heartrate'] > 120) | (df['sbp'] < 90) | (df['resprate'] > 24),
        'high',
        np.where(
            (df['heartrate'] > 100) | (df['sbp'] < 100) | (df['resprate'] > 20),
            'medium',
            'low'
        )
    )
    
    # Handle missing values
    for col in ['heartrate', 'sbp', 'dbp', 'resprate', 'o2sat']:
        df[col].fillna(df[col].median(), inplace=True)
    
    return df

# Feature engineering for prediction model
def create_features(df):
    """
    Create features for patient flow prediction
    """
    # Time-based features
    df['arrival_hour'] = df['intime'].dt.hour
    df['arrival_dayofweek'] = df['intime'].dt.dayofweek
    
    # Vital sign abnormalities
    df['tachycardia'] = (df['heartrate'] > 100).astype(int)
    df['hypotension'] = (df['sbp'] < 90).astype(int)
    df['tachypnea'] = (df['resprate'] > 20).astype(int)
    df['hypoxia'] = (df['o2sat'] < 90).astype(int)
    
    # Demographic features
    df['age'] = (pd.to_datetime('2100-01-01') - df['intime']).dt.days / 365.25
    
    return df

# Build prediction model for patient disposition
def build_prediction_model(df):
    """
    Train a model to predict patient disposition (admitted vs discharged)
    """
    # Define features and target
    features = ['age', 'heartrate', 'sbp', 'resprate', 'o2sat', 
                'tachycardia', 'hypotension', 'tachypnea', 'hypoxia',
                'arrival_hour', 'arrival_dayofweek']
    target = 'disposition'
    
    # Filter and prepare data
    model_df = df[df['disposition'].isin(['ADMITTED', 'HOME'])].copy()
    model_df['target'] = (model_df['disposition'] == 'ADMITTED').astype(int)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        model_df[features], model_df['target'], test_size=0.2, random_state=42
    )
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")
    print(classification_report(y_test, y_pred))
    
    # Feature importance
    feat_importance = pd.DataFrame({
        'feature': features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x='importance', y='feature', data=feat_importance)
    plt.title('Feature Importance for Admission Prediction')
    plt.tight_layout()
    plt.show()
    
    return model

# Analyze patient flow patterns
def analyze_patient_flow(df):
    """
    Generate insights about ED patient flow
    """
    # Arrival patterns
    plt.figure(figsize=(12, 6))
    df['arrival_hour'].value_counts().sort_index().plot(kind='bar')
    plt.title('Patient Arrivals by Hour of Day')
    plt.xlabel('Hour of Day')
    plt.ylabel('Number of Patients')
    plt.show()
    
    # Length of stay analysis
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='disposition', y='los_minutes', data=df)
    plt.ylim(0, df['los_minutes'].quantile(0.95))  # Remove extreme outliers
    plt.title('Length of Stay by Disposition')
    plt.ylabel('Minutes in ED')
    plt.xticks(rotation=45)
    plt.show()
    
    # Urgency level distribution
    urgency_dist = df['urgency'].value_counts(normalize=True)
    print("\nPatient Urgency Level Distribution:")
    print(urgency_dist)

# Main execution
if __name__ == "__main__":
    # Set your MIMIC-IV-ED data directory
    DATA_DIR = "data/"
    
    # Load data
    edstays, triage, vitalsign, diagnosis = load_mimic_ed_data(DATA_DIR)
    
    if edstays is not None:
        # Preprocess and merge data
        df = preprocess_data(edstays, triage, vitalsign, diagnosis)
        
        # Feature engineering
        df = create_features(df)
        
        # Basic analysis
        analyze_patient_flow(df)
        
        # Build prediction model
        model = build_prediction_model(df)
        
        # Save processed data for future use
        df.to_csv('processed_mimic_ed_data.csv', index=False)
        print("Processing complete. Data saved to processed_mimic_ed_data.csv")