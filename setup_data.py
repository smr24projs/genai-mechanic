import pandas as pd
import json
import os

# 1. Generate Dummy DTC Codes
dtc_data = {
    "code": ["P0300", "P0171", "P0420", "P0442", "OEM-991"],
    "description": [
        "Random/Multiple Cylinder Misfire Detected",
        "System Too Lean (Bank 1)",
        "Catalyst System Efficiency Below Threshold",
        "Evaporative Emission System Leak Detected (Small Leak)",
        "Hybrid Battery Cooling Fan Malfunction (Synthetic)"
    ],
    "symptoms": [
        "Rough idle, jerking, flashing CEL",
        "Hesitation, poor fuel economy",
        "Sulfur smell, check engine light",
        "Gas smell near cap",
        "Overheating warning, fan noise"
    ]
}

# 2. Generate Dummy Parts Catalog
parts_data = [
    {"part_id": "IGN-001", "name": "Ignition Coil Pack", "price": 45.00, "compatibility": ["P0300"]},
    {"part_id": "SPK-99", "name": "Spark Plug (Iridium)", "price": 12.50, "compatibility": ["P0300"]},
    {"part_id": "O2S-12", "name": "Upstream O2 Sensor", "price": 89.00, "compatibility": ["P0171"]},
    {"part_id": "VAC-HOSE", "name": "Vacuum Hose Kit", "price": 15.00, "compatibility": ["P0171", "P0442"]},
    {"part_id": "CAT-CONV", "name": "Catalytic Converter", "price": 450.00, "compatibility": ["P0420"]}
]

def run_setup():
    # Ensure directory exists
    os.makedirs("data", exist_ok=True)
    
    # Save CSV
    df = pd.DataFrame(dtc_data)
    df.to_csv("data/dtc_codes.csv", index=False)
    print("✅ Created data/dtc_codes.csv")
    
    # Save JSON
    with open("data/parts_catalog.json", "w") as f:
        json.dump(parts_data, f, indent=2)
    print("✅ Created data/parts_catalog.json")

if __name__ == "__main__":
    run_setup()
