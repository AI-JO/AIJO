import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def build_stay_mapping(patients_df: pd.DataFrame) -> pd.DataFrame:
    patients_df = patients_df.copy()
    patients_df['stay_id'] = range(1, len(patients_df) + 1)
    patients_df['subject_id'] = patients_df['patient_id']
    return patients_df[['patient_id', 'subject_id', 'stay_id', 'arrival_time', 'discharge_time', 'disposition', 'triage_level']]


def create_edstays(mapped_patients: pd.DataFrame) -> pd.DataFrame:
    edstays = pd.DataFrame({
        'subject_id': mapped_patients['subject_id'],
        'stay_id': mapped_patients['stay_id'],
        'intime': mapped_patients['arrival_time'],
        'outtime': mapped_patients['discharge_time'],
        'disposition': mapped_patients['disposition'].replace({'DISCHARGED': 'HOME'})
    })
    return edstays


def create_triage(mapped_patients: pd.DataFrame, vitals_df: pd.DataFrame) -> pd.DataFrame:
    triage = mapped_patients[['subject_id', 'stay_id', 'triage_level']].copy()
    if 'pain_score' in vitals_df.columns:
        triage = triage.merge(
            vitals_df[['patient_id', 'pain_score']],
            left_on='subject_id',
            right_on='patient_id',
            how='left'
        )
        triage = triage.drop(columns=['patient_id'])
    return triage


def create_vitalsign(mapped_patients: pd.DataFrame, vitals_df: pd.DataFrame) -> pd.DataFrame:
    vit = vitals_df.rename(columns={
        'heart_rate': 'heartrate',
        'systolic_bp': 'sbp',
        'diastolic_bp': 'dbp',
        'resp_rate': 'resprate',
        'o2_saturation': 'o2sat'
    }).copy()
    vit = vit.merge(mapped_patients[['patient_id', 'subject_id', 'stay_id']], on='patient_id', how='left')
    vit = vit[['subject_id', 'stay_id', 'heartrate', 'sbp', 'dbp', 'resprate', 'o2sat']]
    return vit


def create_diagnosis(mapped_patients: pd.DataFrame, diagnoses_df: pd.DataFrame) -> pd.DataFrame:
    diag = diagnoses_df.copy()
    if 'icd_code' not in diag.columns:
        diag['icd_code'] = 'R69'
    diag['icd_version'] = 10
    diag = diag.merge(mapped_patients[['patient_id', 'stay_id']], on='patient_id', how='left')
    diag = diag[['stay_id', 'icd_code', 'icd_version']]
    return diag


def main():
    ensure_data_dir()

    # Read synthetic data from data/ if present there
    src_dir = DATA_DIR if os.path.exists(os.path.join(DATA_DIR, 'synthetic_patients.csv')) else os.path.dirname(__file__)
    patients = pd.read_csv(os.path.join(src_dir, 'synthetic_patients.csv'), parse_dates=['arrival_time', 'discharge_time'])
    vitals = pd.read_csv(os.path.join(src_dir, 'synthetic_vitals.csv'))
    diagnoses = pd.read_csv(os.path.join(src_dir, 'synthetic_diagnoses.csv'))

    mapped_patients = build_stay_mapping(patients)

    edstays = create_edstays(mapped_patients)
    triage = create_triage(mapped_patients, vitals)
    vitalsign = create_vitalsign(mapped_patients, vitals)
    diagnosis = create_diagnosis(mapped_patients, diagnoses)

    edstays.to_csv(os.path.join(DATA_DIR, 'edstays.csv'), index=False)
    triage.to_csv(os.path.join(DATA_DIR, 'triage.csv'), index=False)
    vitalsign.to_csv(os.path.join(DATA_DIR, 'vitalsign.csv'), index=False)
    diagnosis.to_csv(os.path.join(DATA_DIR, 'diagnosis.csv'), index=False)

    print('Wrote data files to', DATA_DIR)


if __name__ == '__main__':
    main() 