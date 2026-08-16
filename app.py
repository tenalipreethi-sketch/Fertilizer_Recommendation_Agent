import os
import pandas as pd
import streamlit as st

from phase2_agent import (
    predict_fertilizer,
    save_record,
    fertilizer_info,
    soil_encoder,
    crop_encoder
)

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Fertilizer Recommendation AI Agent",
    page_icon="🌱",
    layout="wide"
)

# =========================================================
# TITLE
# =========================================================

st.title("🌱 Fertilizer Recommendation AI Agent")

st.write(
    "Enter soil, crop and environmental details "
    "to receive a suitable fertilizer recommendation."
)

st.divider()

# =========================================================
# FARM INPUT SECTION
# =========================================================

st.subheader("🧾 Farm Input Details")

col1, col2 = st.columns(2)

with col1:

    temperature = st.number_input(
        "🌡️ Temperature (°C)",
        min_value=0.0,
        max_value=60.0,
        value=30.0,
        step=1.0
    )

    humidity = st.number_input(
        "💧 Humidity (%)",
        min_value=0.0,
        max_value=100.0,
        value=60.0,
        step=1.0
    )

    moisture = st.number_input(
        "🌊 Moisture (%)",
        min_value=0.0,
        max_value=100.0,
        value=40.0,
        step=1.0
    )

    soil_type = st.selectbox(
        "🌍 Soil Type",
        list(soil_encoder.classes_)
    )

with col2:

    crop_type = st.selectbox(
        "🌾 Crop Type",
        list(crop_encoder.classes_)
    )

    nitrogen = st.number_input(
        "Nitrogen (N)",
        min_value=0.0,
        value=25.0,
        step=1.0
    )

    potassium = st.number_input(
        "Potassium (K)",
        min_value=0.0,
        value=15.0,
        step=1.0
    )

    phosphorus = st.number_input(
        "Phosphorus (P)",
        min_value=0.0,
        value=20.0,
        step=1.0
    )

st.divider()

# =========================================================
# PREDICTION
# =========================================================

if st.button(
    "🌱 Recommend Fertilizer",
    type="primary",
    use_container_width=True
):

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

    # -----------------------------------------------------
    # RESULT
    # -----------------------------------------------------

    st.subheader("🌿 Recommendation Result")

    result_col1, result_col2 = st.columns(2)

    with result_col1:

        st.metric(
            "Recommended Fertilizer",
            info["display"]
        )

    with result_col2:

        st.metric(
            "Prediction Confidence",
            f"{confidence:.2f}%"
        )

    st.success(
        f"🌱 Recommended Fertilizer: {info['display']}"
    )

    # -----------------------------------------------------
    # FERTILIZER INFORMATION
    # -----------------------------------------------------

    st.subheader("📋 Fertilizer Information")

    st.write(
        f"**Fertilizer Type:** {info['type']}"
    )

    st.info(
        f"Application Guidance: {info['guidance']}"
    )

    # -----------------------------------------------------
    # CONFIDENCE WARNING
    # -----------------------------------------------------

    if confidence < 60:

        st.warning(
            "⚠️ Prediction confidence is relatively low. "
            "Please recheck soil nutrient values or confirm "
            "the recommendation with a soil test."
        )

    # -----------------------------------------------------
    # SAVE RECORD
    # -----------------------------------------------------

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

    st.success(
        "✅ Farm record saved successfully."
    )

# =========================================================
# FARM HISTORY
# =========================================================

st.divider()

st.subheader("📊 Farm Recommendation History")

record_path = os.path.join(
    "records",
    "farm_records.csv"
)

if os.path.exists(record_path):

    history_df = pd.read_csv(record_path)

    if not history_df.empty:

        history_df = history_df.reset_index(drop=True)

        # -------------------------------------------------
        # HISTORY TITLE + CLEAR ALL
        # -------------------------------------------------

        title_col, clear_col = st.columns([5, 1])

        with title_col:

            st.write("### 🗂 Recent Farm Records")

        with clear_col:

            if st.button(
                "🧹 Clear All",
                use_container_width=True
            ):

                st.session_state["confirm_clear"] = True

        # -------------------------------------------------
        # CLEAR ALL CONFIRMATION
        # -------------------------------------------------

        if st.session_state.get(
            "confirm_clear",
            False
        ):

            st.warning(
                "⚠️ Delete all farm history?"
            )

            yes_col, no_col = st.columns(2)

            with yes_col:

                if st.button(
                    "✅ Yes, Delete All",
                    type="primary",
                    use_container_width=True
                ):

                    os.remove(record_path)

                    st.session_state[
                        "confirm_clear"
                    ] = False

                    st.rerun()

            with no_col:

                if st.button(
                    "❌ Cancel",
                    use_container_width=True
                ):

                    st.session_state[
                        "confirm_clear"
                    ] = False

                    st.rerun()

        # =================================================
        # FARM RECORD TABLE WITH DELETE COLUMN
        # =================================================

        st.markdown("---")

        # Table column widths
        widths = [
            2.3, 0.9, 0.9, 0.9,
            1.2, 1.3, 0.8, 0.8,
            0.9, 1.6, 1.1, 0.6
        ]

        # -------------------------------------------------
        # TABLE HEADER
        # -------------------------------------------------

        header = st.columns(widths)

        headers = [
            "Date",
            "Temp",
            "Humidity",
            "Moisture",
            "Soil",
            "Crop",
            "N",
            "K",
            "P",
            "Fertilizer",
            "Confidence",
            "🗑️"
        ]

        for column, name in zip(
            header,
            headers
        ):

            column.markdown(
                f"**{name}**"
            )

        st.markdown("---")

        # -------------------------------------------------
        # SHOW LAST 10 RECORDS
        # -------------------------------------------------

        recent_indices = list(
            history_df.tail(10).index
        )

        recent_indices.reverse()

        for index in recent_indices:

            row = history_df.loc[index]

            cols = st.columns(widths)

            cols[0].write(row["Date"])

            cols[1].write(
                f"{row['Temperature']}"
            )

            cols[2].write(
                f"{row['Humidity']}"
            )

            cols[3].write(
                f"{row['Moisture']}"
            )

            cols[4].write(
                row["Soil Type"]
            )

            cols[5].write(
                row["Crop Type"]
            )

            cols[6].write(
                row["Nitrogen"]
            )

            cols[7].write(
                row["Potassium"]
            )

            cols[8].write(
                row["Phosphorus"]
            )

            cols[9].write(
                row["Recommended Fertilizer"]
            )

            cols[10].write(
                f"{row['Confidence']}%"
            )

            # ---------------------------------------------
            # SMALL DUSTBIN BUTTON
            # ---------------------------------------------

            if cols[11].button(
                "🗑️",
                key=f"delete_record_{index}",
                help="Delete this record"
            ):

                st.session_state[
                    "delete_index"
                ] = index

        # -------------------------------------------------
        # SINGLE RECORD DELETE CONFIRMATION
        # -------------------------------------------------

        if "delete_index" in st.session_state:

            delete_index = st.session_state[
                "delete_index"
            ]

            st.warning(
                "⚠️ Are you sure you want to delete "
                "this farm record?"
            )

            delete_yes, delete_no = st.columns(2)

            with delete_yes:

                if st.button(
                    "🗑️ Delete Record",
                    type="primary",
                    use_container_width=True
                ):

                    history_df = history_df.drop(
                        index=delete_index
                    )

                    history_df.to_csv(
                        record_path,
                        index=False
                    )

                    del st.session_state[
                        "delete_index"
                    ]

                    st.rerun()

            with delete_no:

                if st.button(
                    "❌ Cancel",
                    use_container_width=True
                ):

                    del st.session_state[
                        "delete_index"
                    ]

                    st.rerun()

        # -------------------------------------------------
        # TOTAL RECORD COUNT
        # -------------------------------------------------

        st.caption(
            f"Total recommendations saved: "
            f"{len(history_df)}"
        )

        # =================================================
        # DISTRIBUTION CHART
        # =================================================

        st.divider()

        st.write(
            "### 🌱 Fertilizer Recommendation Distribution"
        )

        fertilizer_counts = (
            history_df[
                "Recommended Fertilizer"
            ]
            .value_counts()
        )

        st.bar_chart(
            fertilizer_counts,
            use_container_width=True
        )

    else:

        st.info(
            "No farm records are available yet."
        )

else:

    st.info(
        "No farm records yet. "
        "Make your first fertilizer recommendation above."
    )

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🌱 Fertilizer Recommendation AI Agent | "
    "Machine Learning based decision support system"
)