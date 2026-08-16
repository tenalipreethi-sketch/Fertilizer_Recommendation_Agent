import os
import csv
import joblib
import pandas as pd
from datetime import datetime

# -------------------------------------------------
# PATHS
# -------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
RECORD_DIR = os.path.join(BASE_DIR, "records")

os.makedirs(RECORD_DIR, exist_ok=True)

# -------------------------------------------------
# LOAD MODEL + ENCODERS
# -------------------------------------------------

model = joblib.load(
    os.path.join(MODEL_DIR, "fertilizer_model.pkl")
)

soil_encoder = joblib.load(
    os.path.join(MODEL_DIR, "soil_encoder.pkl")
)

crop_encoder = joblib.load(
    os.path.join(MODEL_DIR, "crop_encoder.pkl")
)

fertilizer_encoder = joblib.load(
    os.path.join(MODEL_DIR, "fertilizer_encoder.pkl")
)

# -------------------------------------------------
# FERTILIZER INFO
# -------------------------------------------------

fertilizer_info = {
    "Urea": {
        "display": "Urea",
        "type": "Nitrogen Fertilizer",
        "guidance": "Use based on crop nitrogen requirement and soil-test recommendation."
    },
    "DAP": {
        "display": "DAP (Diammonium Phosphate)",
        "type": "Nitrogen and Phosphorus Fertilizer",
        "guidance": "Suitable when crop phosphorus requirement is relatively high."
    },
    "28-28": {
        "display": "NPK 28-28",
        "type": "Nitrogen-Phosphorus Fertilizer",
        "guidance": "Apply according to crop stage and soil nutrient requirements."
    },
    "14-35-14": {
        "display": "NPK 14-35-14",
        "type": "NPK Fertilizer",
        "guidance": "Useful where phosphorus demand is relatively high."
    },
    "17-17-17": {
        "display": "NPK 17-17-17",
        "type": "Balanced NPK Fertilizer",
        "guidance": "Provides balanced nitrogen, phosphorus and potassium."
    },
    "20-20": {
        "display": "NPK 20-20",
        "type": "Nitrogen-Phosphorus Fertilizer",
        "guidance": "Use according to soil nutrient status and crop needs."
    },
    "10-26-26": {
        "display": "NPK 10-26-26",
        "type": "NPK Fertilizer",
        "guidance": "Useful where phosphorus and potassium requirements are higher."
    }
}

# -------------------------------------------------
# PREDICTION FUNCTION
# -------------------------------------------------

def predict_fertilizer(
    temperature,
    humidity,
    moisture,
    soil_type,
    crop_type,
    nitrogen,
    potassium,
    phosphorus
):

    soil_code = soil_encoder.transform([soil_type])[0]
    crop_code = crop_encoder.transform([crop_type])[0]

    input_data = pd.DataFrame(
        [[
            temperature,
            humidity,
            moisture,
            soil_code,
            crop_code,
            nitrogen,
            potassium,
            phosphorus
        ]],
        columns=[
            "Temperature",
            "Humidity",
            "Moisture",
            "Soil Type",
            "Crop Type",
            "Nitrogen",
            "Potassium",
            "Phosphorus"
        ]
    )

    prediction_code = model.predict(input_data)[0]

    predicted_fertilizer = fertilizer_encoder.inverse_transform(
        [prediction_code]
    )[0]

    probabilities = model.predict_proba(input_data)[0]
    confidence = float(max(probabilities) * 100)

    return predicted_fertilizer, confidence


# -------------------------------------------------
# SAVE FARM RECORD
# -------------------------------------------------

def save_record(
    temperature,
    humidity,
    moisture,
    soil_type,
    crop_type,
    nitrogen,
    potassium,
    phosphorus,
    fertilizer,
    confidence
):

    file_path = os.path.join(
        RECORD_DIR,
        "farm_records.csv"
    )

    file_exists = os.path.exists(file_path)

    with open(
        file_path,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "Date",
                "Temperature",
                "Humidity",
                "Moisture",
                "Soil Type",
                "Crop Type",
                "Nitrogen",
                "Potassium",
                "Phosphorus",
                "Recommended Fertilizer",
                "Confidence"
            ])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            temperature,
            humidity,
            moisture,
            soil_type,
            crop_type,
            nitrogen,
            potassium,
            phosphorus,
            fertilizer,
            round(confidence, 2)
        ])


# -------------------------------------------------
# TERMINAL AI AGENT
# -------------------------------------------------

if __name__ == "__main__":

    print("\n🌱 FERTILIZER RECOMMENDATION AI AGENT")
    print("=" * 55)

    print("\nAvailable Soil Types:")
    print(", ".join(soil_encoder.classes_))

    print("\nAvailable Crop Types:")
    print(", ".join(crop_encoder.classes_))

    try:

        temperature = float(input("\nTemperature (°C): "))
        humidity = float(input("Humidity (%): "))
        moisture = float(input("Moisture (%): "))

        soil_input = input("Soil Type: ").strip()
        crop_input = input("Crop Type: ").strip()

        soil_lookup = {
            value.lower(): value
            for value in soil_encoder.classes_
        }

        crop_lookup = {
            value.lower(): value
            for value in crop_encoder.classes_
        }

        if soil_input.lower() not in soil_lookup:
            raise ValueError(
                f"Invalid Soil Type: {soil_input}"
            )

        if crop_input.lower() not in crop_lookup:
            raise ValueError(
                f"Invalid Crop Type: {crop_input}"
            )

        soil_type = soil_lookup[soil_input.lower()]
        crop_type = crop_lookup[crop_input.lower()]

        nitrogen = float(input("Nitrogen: "))
        potassium = float(input("Potassium: "))
        phosphorus = float(input("Phosphorus: "))

        fertilizer, confidence = predict_fertilizer(
            temperature,
            humidity,
            moisture,
            soil_type,
            crop_type,
            nitrogen,
            potassium,
            phosphorus
        )

        info = fertilizer_info.get(
            fertilizer,
            {
                "display": fertilizer,
                "type": "Fertilizer",
                "guidance": "Follow local agricultural recommendations."
            }
        )

        print("\n" + "=" * 55)
        print("🌱 FERTILIZER RECOMMENDATION")
        print("=" * 55)

        print(
            f"Recommended Fertilizer : {info['display']}"
        )

        print(
            f"Fertilizer Type        : {info['type']}"
        )

        print(
            f"Confidence             : {confidence:.2f}%"
        )

        print("\n📋 Guidance:")
        print(info["guidance"])

        if confidence < 60:
            print(
                "\n⚠️ Confidence is relatively low. "
                "Recheck the input values or confirm with a soil test."
            )

        save_record(
            temperature,
            humidity,
            moisture,
            soil_type,
            crop_type,
            nitrogen,
            potassium,
            phosphorus,
            fertilizer,
            confidence
        )

        print("\n✅ Farm record saved successfully.")

    except ValueError as error:
        print("\n❌ Input Error:", error)

    except Exception as error:
        print("\n❌ Error:", error)