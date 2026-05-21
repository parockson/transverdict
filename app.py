import streamlit as st
import pandas as pd
import time
from core.cleaner import clean_transaction_data
from core.segmenter import process_segmentation
from core.analyzer import generate_pivot_report, export_to_excel, generate_visuals

# Page Configuration
st.set_page_config(page_title="TransVerdict Batch Processor", layout="wide")

# Custom CSS for UI polish
st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("⚖️ TransVerdict: Automated Batch Analysis")
st.markdown("Upload your transaction data below. The system will clean, segment, and analyze all metrics in one pass.")

# Metabase Download Source Notice
st.info("💡 **Important Notice:** Please download your transaction data **only** from this [Metabase Link](https://metabase.korba365.com/question/4590-user-transaction-table) before uploading.")

# --- FILE UPLOAD ---
uploaded_file = st.file_uploader("Drop your CSV or Excel file here", type=['csv', 'xlsx'])

if uploaded_file:
    # Action Button
    if st.button("🚀 Process Data & Generate Reports"):
        # Initializing Progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # PHASE 1: INGESTION
            status_text.info("Phase 1/4: Reading data file...")
            if uploaded_file.name.endswith('.csv'):
                df_raw = pd.read_csv(uploaded_file)
            else:
                df_raw = pd.read_excel(uploaded_file)
            progress_bar.progress(25)
            time.sleep(0.3)

            # PHASE 2: PROCESSING
            status_text.info("Phase 2/4: Applying cleaning and segmentation logic...")
            df_clean = clean_transaction_data(df_raw)
            df_final = process_segmentation(df_clean)
            progress_bar.progress(50)
            time.sleep(0.3)

            # PHASE 3: STATISTICAL REPORTS
            status_text.info("Phase 3/4: Compiling pivot tables and Excel export...")
            
            # Dynamic Column Discovery
            type_col = next((c for c in df_final.columns if 'type' in c), 'transaction_type')
            resp_col = next((c for c in df_final.columns if 'response' in c), 'response_code')
            client_col = 'client_name'

            # Build all requested reports
            reports_dict = {
                "Transformed Data": df_final,
                "Response Codes": generate_pivot_report(df_final, [resp_col]),
                "Biz Segment": generate_pivot_report(df_final, ["biz_segment"]),
                "Client Name": generate_pivot_report(df_final, [client_col]),
                "Biz & Client": generate_pivot_report(df_final, ["biz_segment", client_col]),
                "Transaction Type": generate_pivot_report(df_final, [type_col])
            }

            # 2f. Final Message Summary
            # Group by both error_segment and final_message to show counts and percentages
            msg_summary = df_final.groupby(['error_segment', 'final_message'], as_index=False).size()
            msg_summary.columns = ['Error Segment', 'Final Message', 'Count']
            msg_summary['Percentage'] = msg_summary['Count'] / msg_summary['Count'].sum()
            msg_summary = msg_summary.sort_values(by='Count', ascending=False).reset_index(drop=True)
            reports_dict["Final Message Summary"] = msg_summary

            # Generate formatted Excel binary
            excel_binary = export_to_excel(reports_dict)
            progress_bar.progress(75)
            time.sleep(0.3)

            # PHASE 4: VISUALS
            status_text.info("Phase 4/4: Generating interactive plots...")
            visuals = generate_visuals(df_final)
            progress_bar.progress(100)
            status_text.success("Analysis Complete!")

            # --- DISPLAY RESULTS ---
            st.divider()

            # Download Actions
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                st.download_button(
                    label="📥 Download Formatted Excel Report",
                    data=excel_binary,
                    file_name="TransVerdict_Analysis_Full.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    width='stretch'
                )
            with col_dl2:
                csv = df_final.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Cleaned CSV", data=csv, width='stretch')

            # UI Viewport
            tab_data, tab_reports, tab_plots = st.tabs(["📋 Transformed Data", "📑 Analysis Tables", "📊 Visual Dashboard"])

            with tab_data:
                st.subheader("Final Processed Dataset")
                st.dataframe(df_final.head(1000), width='stretch', hide_index=True)
                st.caption("ℹ️ Showing the first 1,000 rows as a preview. Use the download buttons above to obtain the complete dataset.")

            with tab_reports:
                st.subheader("Statistical Breakdowns")
                for title, rdf in reports_dict.items():
                    if title != "Transformed Data":
                        st.write(f"**{title}**")
                        # Identify % columns to format them as percentages in the UI
                        pct_cols = [c for c in rdf.columns if '%' in c or 'Percentage' in c]
                        st.dataframe(
                            rdf, 
                            width='stretch', 
                            hide_index=True,
                            column_config={c: st.column_config.NumberColumn(format="%.2f%%") for c in pct_cols}
                        )
                        st.markdown("---")

            with tab_plots:
                # Layout based on user request (3a-d)
                c1, c2 = st.columns(2)
                with c1:
                    st.plotly_chart(visuals['fig_a'], width='stretch')
                with c2:
                    st.plotly_chart(visuals['fig_b'], width='stretch')
                
                st.plotly_chart(visuals['fig_c'], width='stretch')
                st.plotly_chart(visuals['fig_d'], width='stretch')

        except Exception as e:
            st.error(f"An error occurred during processing: {e}")
            st.exception(e)

else:
    st.info("👋 Welcome! Please upload your transaction file to enable the processing button.")