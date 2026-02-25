# import pandas as pd
# import numpy as np
# import random

# def generate_balanced_vehicle_data(n_records=7000):
#     # 1. Define 50+ Unique Car Models
#     car_models = [
#         "Tata Nexon", "Tata Sierra", "Tata Harrier", "Tata Safari", "Tata Altroz", 
#         "Tata Tiago", "Tata Tigor", "Tata Punch", "Mahindra XUV700", "Mahindra Thar", 
#         "Mahindra Scorpio-N", "Mahindra Bolero", "Mahindra XUV300", "Mahindra Marazzo",
#         "Maruti Suzuki Swift", "Maruti Suzuki Baleno", "Maruti Suzuki Vitara Brezza", 
#         "Maruti Suzuki Ertiga", "Maruti Suzuki Dzire", "Maruti Suzuki WagonR", 
#         "Maruti Suzuki Alto", "Maruti Suzuki Celerio", "Hyundai Creta", "Hyundai Venue", 
#         "Hyundai i20", "Hyundai Verna", "Hyundai Alcazar", "Hyundai Tucson",
#         "Kia Seltos", "Kia Sonet", "Kia Carens", "Toyota Fortuner", 
#         "Toyota Innova Hycross", "Toyota Urban Cruiser", "Toyota Glanza",
#         "Honda City", "Honda Amaze", "Volkswagen Taigun", "Volkswagen Virtus",
#         "Skoda Kushaq", "Skoda Slavia", "MG Hector", "MG Astor", "Jeep Compass",
#         "Nissan Magnite", "Renault Kiger", "Renault Kwid", "Ford Endeavour", 
#         "Ford EcoSport", "BMW X5", "Mercedes-Benz GLC", "Audi Q5"
#     ]
    
#     # 2. Define Diagnostic States (Balanced)
#     states = ['Healthy', 'P0171_Lean', 'P0300_Misfire', 'P0117_Coolant_High', 'P0101_MAF_Fault', 'P2463_DPF_Soot']
    
#     data = []
    
#     for _ in range(n_records):
#         model = random.choice(car_models)
#         year = random.randint(2015, 2024)
        
#         # Pick a state randomly (Equal probability for each state ~16.6%)
#         state = random.choice(states)
        
#         # --- Base Normal Parameters (Initial random seed) ---
#         rpm = random.uniform(750, 3500)
#         speed = (rpm * 0.038) + random.uniform(-8, 8)
#         load = random.uniform(15, 55)
#         temp = random.uniform(88, 96)
#         maf = (rpm / 100) * 1.8 + random.uniform(-0.5, 0.5)
#         stft = random.uniform(-2, 2)
#         ltft = random.uniform(-2, 2)
#         throttle = (load / 2.2) + random.uniform(5, 10)
#         dtc = "None"
        
#         # --- Injecting Diagnostic Fault Logic ---
#         if state == 'P0171_Lean':
#             # Lean Condition: High positive fuel trims
#             stft = random.uniform(15, 28)
#             ltft = random.uniform(12, 22)
#             dtc = "P0171"
        
#         elif state == 'P0300_Misfire':
#             # Misfire: Rough idle/high load, fluctuating trims
#             rpm += random.uniform(-400, 400)
#             load = random.uniform(60, 85)
#             stft = random.uniform(-8, 8)
#             dtc = "P0300"
            
#         elif state == 'P0117_Coolant_High':
#             # Sensor/Overheat: Temp exceeds safe limits
#             temp = random.uniform(112, 140)
#             dtc = "P0117"
            
#         elif state == 'P0101_MAF_Fault':
#             # MAF Fault: Airflow reading drops significantly relative to RPM
#             maf = (rpm / 100) * 0.4 + random.uniform(-0.1, 0.1)
#             dtc = "P0101"

#         elif state == 'P2463_DPF_Soot':
#             # DPF Soot: Limp mode restriction (Max Speed/RPM) + High Load
#             rpm = min(rpm, 2100)
#             speed = min(speed, 42)
#             load = random.uniform(80, 98)
#             dtc = "P2463"

#         data.append({
#             'CAR_MODEL': model,
#             'YEAR': year,
#             'ENGINE_RPM': round(rpm, 1),
#             'VEHICLE_SPEED': max(0, round(speed, 1)),
#             'ENGINE_LOAD': round(load, 1),
#             'COOLANT_TEMP': round(temp, 1),
#             'MAF_GRAMS_SEC': round(maf, 2),
#             'SHORT_TERM_TRIM': round(stft, 2),
#             'LONG_TERM_TRIM': round(ltft, 2),
#             'THROTTLE_POS': round(throttle, 1),
#             'TROUBLE_CODES': dtc
#         })
        
#     return pd.DataFrame(data)

# # 3. Generate 7000 records
# df = generate_balanced_vehicle_data(7000)

# # 4. Save to CSV
# output_filename = 'balanced_multi_car_diagnostic_dataset.csv'
# df.to_csv(output_filename, index=False)

# print(f"Successfully generated {len(df)} records.")
# print(f"File saved as: {output_filename}")
# print("\nClass Distribution:\n", df['TROUBLE_CODES'].value_counts())


import pandas as pd
import numpy as np
import random
import os

def generate_final_dataset(original_csv_path, output_path, n_total=7000):
    print(f"--- Starting Dataset Generation ---")
    
    # 1. LOAD AND CLEAN ORIGINAL DATA
    if os.path.exists(original_csv_path):
        orig_df = pd.read_csv(original_csv_path, low_memory=False)
        print(f"Loaded {len(orig_df)} records from original dataset.")
    else:
        print(f"Error: {original_csv_path} not found. Ensure the file is in the correct directory.")
        return

    def clean_numeric(val):
        if pd.isna(val) or val == '': return np.nan
        if isinstance(val, str):
            val = val.replace('%', '').replace(',', '.')
            try: return float(val)
            except: return np.nan
        return val

    # Map original data to our standard schema
    orig_processed = pd.DataFrame()
    orig_processed['CAR_MODEL'] = orig_df['MARK'].astype(str) + " " + orig_df['MODEL'].astype(str)
    orig_processed['YEAR'] = pd.to_numeric(orig_df['CAR_YEAR'], errors='coerce')
    orig_processed['ENGINE_RPM'] = pd.to_numeric(orig_df['ENGINE_RPM'], errors='coerce')
    orig_processed['VEHICLE_SPEED'] = pd.to_numeric(orig_df['SPEED'], errors='coerce')
    orig_processed['ENGINE_LOAD'] = orig_df['ENGINE_LOAD'].apply(clean_numeric)
    orig_processed['COOLANT_TEMP'] = pd.to_numeric(orig_df['ENGINE_COOLANT_TEMP'], errors='coerce')
    orig_processed['MAF_GRAMS_SEC'] = orig_df['MAF'].apply(clean_numeric)
    orig_processed['SHORT_TERM_TRIM'] = orig_df['SHORT TERM FUEL TRIM BANK 1'].apply(clean_numeric)
    orig_processed['LONG_TERM_TRIM'] = orig_df['LONG TERM FUEL TRIM BANK 2'].apply(clean_numeric)
    orig_processed['THROTTLE_POS'] = orig_df['THROTTLE_POS'].apply(clean_numeric)
    
    # Classify original DTCs (Original data is 99% 'None/Healthy')
    orig_processed['TROUBLE_CODES'] = orig_df['DTC_NUMBER'].apply(
        lambda x: "None" if pd.isna(x) or "OFF" in str(x) or "0 codes" in str(x) else str(x)
    )
    
    # Drop rows with missing core engine data to ensure quality
    orig_processed = orig_processed.dropna(subset=['ENGINE_RPM', 'VEHICLE_SPEED', 'ENGINE_LOAD']).copy()
    
    # We take a sample of 1,500 'Healthy' records from real data to maintain realism
    healthy_sample = orig_processed[orig_processed['TROUBLE_CODES'] == 'None'].sample(n=min(1500, len(orig_processed)), random_state=42)
    real_faults = orig_processed[orig_processed['TROUBLE_CODES'] != 'None']
    base_data = pd.concat([healthy_sample, real_faults])

    # 2. GENERATE SYNTHETIC DATA TO BALANCE CLASSES
    n_synth = n_total - len(base_data)
    print(f"Injecting {n_synth} synthetic fault records across 52 car models...")

    car_models_list = [
        "Tata Nexon", "Tata Sierra", "Tata Harrier", "Tata Safari", "Tata Altroz", 
        "Tata Tiago", "Tata Tigor", "Tata Punch", "Mahindra XUV700", "Mahindra Thar", 
        "Mahindra Scorpio-N", "Mahindra Bolero", "Mahindra XUV300", "Mahindra Marazzo",
        "Maruti Suzuki Swift", "Maruti Suzuki Baleno", "Maruti Suzuki Vitara Brezza", 
        "Maruti Suzuki Ertiga", "Maruti Suzuki Dzire", "Maruti Suzuki WagonR", 
        "Maruti Suzuki Alto", "Maruti Suzuki Celerio", "Hyundai Creta", "Hyundai Venue", 
        "Hyundai i20", "Hyundai Verna", "Hyundai Alcazar", "Hyundai Tucson",
        "Kia Seltos", "Kia Sonet", "Kia Carens", "Toyota Fortuner", 
        "Toyota Innova Hycross", "Toyota Urban Cruiser", "Toyota Glanza",
        "Honda City", "Honda Amaze", "Volkswagen Taigun", "Volkswagen Virtus",
        "Skoda Kushaq", "Skoda Slavia", "MG Hector", "MG Astor", "Jeep Compass",
        "Nissan Magnite", "Renault Kiger", "Renault Kwid", "Ford Endeavour", 
        "Ford EcoSport", "BMW X5", "Mercedes-Benz GLC", "Audi Q5"
    ]
    
    fault_categories = ['P0171_Lean', 'P0300_Misfire', 'P0117_Coolant_High', 'P0101_MAF_Fault', 'P2463_DPF_Soot']
    synth_records = []
    
    for _ in range(n_synth):
        model = random.choice(car_models_list)
        year = random.randint(2016, 2024)
        fault = random.choice(fault_categories)
        
        # Base healthy state
        rpm = random.uniform(800, 3500)
        speed = (rpm * 0.035) + random.uniform(-5, 5)
        load = random.uniform(20, 50)
        temp = random.uniform(88, 96)
        maf = (rpm / 100) * 1.8
        stft, ltft = random.uniform(-2, 2), random.uniform(-2, 2)
        throttle = random.uniform(15, 35)
        dtc = "None"
        
        # Apply Fault Logic
        if fault == 'P0171_Lean':
            stft, ltft, dtc = random.uniform(15, 25), random.uniform(12, 20), "P0171"
        elif fault == 'P0300_Misfire':
            rpm += random.uniform(-400, 400); load = random.uniform(70, 90); dtc = "P0300"
        elif fault == 'P0117_Coolant_High':
            temp, dtc = random.uniform(115, 135), "P0117"
        elif fault == 'P0101_MAF_Fault':
            maf = (rpm / 100) * 0.4; dtc = "P0101"
        elif fault == 'P2463_DPF_Soot':
            rpm, speed, load, dtc = 1900, 38, 92, "P2463" # Limp mode

        synth_records.append({
            'CAR_MODEL': model, 'YEAR': year, 'ENGINE_RPM': round(rpm, 1),
            'VEHICLE_SPEED': max(0, round(speed, 1)), 'ENGINE_LOAD': round(load, 1),
            'COOLANT_TEMP': round(temp, 1), 'MAF_GRAMS_SEC': round(maf, 2),
            'SHORT_TERM_TRIM': round(stft, 2), 'LONG_TERM_TRIM': round(ltft, 2),
            'THROTTLE_POS': round(throttle, 1), 'TROUBLE_CODES': dtc
        })

    # 3. MERGE AND FINALIZE
    final_df = pd.concat([base_data, pd.DataFrame(synth_records)], ignore_index=True)
    
    # Impute missing values (primarily from original data sensor gaps)
    final_df = final_df.fillna(final_df.mean(numeric_only=True))
    
    final_df.to_csv(output_path, index=False)
    print(f"--- Generation Complete ---")
    print(f"Saved to: {output_path}")
    print(f"Unique Models: {final_df['CAR_MODEL'].nunique()}")
    print(f"DTC Distribution:\n{final_df['TROUBLE_CODES'].value_counts()}")

if __name__ == "__main__":
    generate_final_dataset(
        original_csv_path='data/exp1_14drivers_14cars_dailyRoutes.csv',
        output_path='data/combined_balanced_dataset.csv'
    )
