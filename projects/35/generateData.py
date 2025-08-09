from faker import Faker
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Initialize Faker with multiple locales for diverse names
fake = Faker(['en_US', 'ar_SA', 'es_ES', 'fr_FR', 'de_DE'])

# Configuration
NUM_PATIENTS = 1000
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2023, 12, 31)
HOSPITALS = ['General Hospital', 'City Medical Center', 'Regional Trauma Center', 
             'University Hospital', 'Children\'s Hospital']

# Medical configurations
TRIAGE_LEVELS = [1, 2, 3, 4, 5]  # 1=most urgent, 5=least urgent
DISPOSITIONS = ['ADMITTED', 'DISCHARGED', 'TRANSFERRED', 'ELOPED', 'DIED']
DIAGNOSES = [
    'Myocardial infarction', 'Pneumonia', 'Fracture', 'Stroke', 
    'Appendicitis', 'Sepsis', 'Asthma', 'COPD exacerbation',
    'Gastroenteritis', 'UTI', 'Head injury', 'Abdominal pain'
]
PROCEDURES = [
    'CT scan', 'X-ray', 'Blood transfusion', 'Suturing',
    'Intubation', 'ECG', 'Ultrasound', 'IV fluids'
]

def generate_patients(n):
    """Generate patient demographic data"""
    patients = []
    for _ in range(n):
        arrival_time = fake.date_time_between(start_date=START_DATE, end_date=END_DATE)
        discharge_time = arrival_time + timedelta(minutes=random.randint(15, 1440))
        
        patients.append({
            'patient_id': fake.unique.random_number(digits=8),
            'gender': random.choice(['M', 'F']),
            'age': random.randint(1, 100),
            'arrival_time': arrival_time,
            'discharge_time': discharge_time,
            'hospital': random.choice(HOSPITALS),
            'triage_level': random.choices(
                TRIAGE_LEVELS, 
                weights=[0.05, 0.15, 0.35, 0.3, 0.15], 
                k=1
            )[0],
            'disposition': random.choices(
                DISPOSITIONS, 
                weights=[0.4, 0.5, 0.05, 0.03, 0.02], 
                k=1
            )[0],
        })
    return pd.DataFrame(patients)

def generate_vitals(patients_df):
    """Generate vital signs based on triage level"""
    vitals = []
    for _, row in patients_df.iterrows():
        # Base values with variation based on triage level
        urgency_factor = 1 + (5 - row['triage_level']) * 0.2
        
        hr = random.randint(60, 100) * urgency_factor
        sbp = random.randint(90, 140) / urgency_factor
        dbp = random.randint(60, 90) / urgency_factor
        rr = random.randint(12, 20) * urgency_factor
        temp = round(36.5 + random.random(), 1)
        o2sat = random.randint(85, 100)
        
        vitals.append({
            'patient_id': row['patient_id'],
            'heart_rate': min(int(hr), 180),
            'systolic_bp': max(int(sbp), 50),
            'diastolic_bp': max(int(dbp), 30),
            'resp_rate': min(int(rr), 40),
            'temperature': temp,
            'o2_saturation': o2sat,
            'pain_score': random.randint(0, 10),
        })
    return pd.DataFrame(vitals)

def generate_diagnoses(patients_df):
    """Generate diagnoses with probabilities"""
    diagnoses = []
    for _, row in patients_df.iterrows():
        num_diagnoses = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1], k=1)[0]
        for _ in range(num_diagnoses):
            diagnoses.append({
                'patient_id': row['patient_id'],
                'diagnosis': random.choice(DIAGNOSES),
                'severity': random.choice(['Mild', 'Moderate', 'Severe']),
                'icd_code': fake.bothify(text='?##.?').upper(),
            })
    return pd.DataFrame(diagnoses)

def generate_procedures(patients_df):
    """Generate procedures performed"""
    procedures = []
    for _, row in patients_df.iterrows():
        # Higher probability of procedures for more urgent cases
        if row['triage_level'] <= 3 and random.random() > 0.3:
            num_procedures = random.randint(1, 3)
            for _ in range(num_procedures):
                procedures.append({
                    'patient_id': row['patient_id'],
                    'procedure': random.choice(PROCEDURES),
                    'procedure_time': row['arrival_time'] + timedelta(
                        minutes=random.randint(10, 
                            int((row['discharge_time'] - row['arrival_time']).total_seconds() / 60))
                    ),
                })
    return pd.DataFrame(procedures)

def generate_staff_data(patients_df):
    """Generate staff assignment data"""
    staff_roles = ['Physician', 'Nurse', 'Technician', 'Resident', 'Intern']
    staff = []
    
    # Create unique staff members
    staff_pool = [{
        'staff_id': fake.unique.random_number(digits=6),
        'name': fake.name(),
        'role': random.choice(staff_roles),
        'shift': random.choice(['Day', 'Evening', 'Night']),
    } for _ in range(50)]
    
    # Assign staff to patients
    for _, row in patients_df.iterrows():
        num_staff = 1 if row['triage_level'] >= 4 else random.randint(1, 3)
        assigned_staff = random.sample(staff_pool, num_staff)
        
        for staff_member in assigned_staff:
            staff.append({
                'patient_id': row['patient_id'],
                'staff_id': staff_member['staff_id'],
                'staff_name': staff_member['name'],
                'staff_role': staff_member['role'],
                'shift': staff_member['shift'],
            })
    
    return pd.DataFrame(staff)

def generate_synthetic_dataset():
    """Generate complete synthetic ED dataset"""
    print("Generating patient data...")
    patients = generate_patients(NUM_PATIENTS)
    
    print("Generating vital signs...")
    vitals = generate_vitals(patients)
    
    print("Generating diagnoses...")
    diagnoses = generate_diagnoses(patients)
    
    print("Generating procedures...")
    procedures = generate_procedures(patients)
    
    print("Generating staff data...")
    staff = generate_staff_data(patients)
    
    # Calculate length of stay in minutes
    patients['length_of_stay_min'] = (
        patients['discharge_time'] - patients['arrival_time']
    ).dt.total_seconds() / 60
    
    # Save to CSV files
    print("Saving data to CSV files...")
    patients.to_csv('synthetic_patients.csv', index=False)
    vitals.to_csv('synthetic_vitals.csv', index=False)
    diagnoses.to_csv('synthetic_diagnoses.csv', index=False)
    procedures.to_csv('synthetic_procedures.csv', index=False)
    staff.to_csv('synthetic_staff.csv', index=False)
    
    print(f"Synthetic ED dataset generated with {NUM_PATIENTS} patients")

if __name__ == "__main__":
    generate_synthetic_dataset()