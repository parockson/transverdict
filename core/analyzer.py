import pandas as pd
import plotly.express as px
import io

def generate_pivot_report(df, index_cols):
    """
    Generates count and percentage tables for error segments.
    Percentages are returned as decimals (e.g., 0.85) for professional formatting.
    """
    # Ensure all segments are represented
    segments = ['External', 'Customer', 'Internal', 'Operational']
    
    # Create pivot for counts
    pivot_count = df.pivot_table(
        index=index_cols, 
        columns='error_segment', 
        aggfunc='size', 
        fill_value=0
    )
    
    # Ensure all segment columns exist in the result
    for seg in segments:
        if seg not in pivot_count.columns:
            pivot_count[seg] = 0
            
    # Calculate Total
    pivot_count['Total'] = pivot_count.sum(axis=1)
    
    # Construct the final report dataframe
    report = pd.DataFrame(index=pivot_count.index)
    
    # Map Segment names to the user-requested column headers
    mapping = {
        'External': ('Ext Count', 'Ext %'),
        'Customer': ('Cust Count', 'Cust %'),
        'Internal': ('Inte Count', 'Inte %'),
        'Operational': ('Success Count', 'Success %')
    }
    
    for seg, (c_name, p_name) in mapping.items():
        report[c_name] = pivot_count[seg]
        # Store as decimal (e.g., 0.1 instead of 10) for Excel/UI formatting
        report[p_name] = (pivot_count[seg] / pivot_count['Total']) if pivot_count['Total'].sum() > 0 else 0
    
    report['Total Transactions'] = pivot_count['Total']
    return report.reset_index()

def export_to_excel(report_dict):
    """
    Exports multiple dataframes to a single Excel file with:
    1. Timezone-unaware datetimes (to prevent ValueErrors)
    2. True Percentage cell formatting
    3. 3-Color Scale conditional formatting for all % columns
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for sheet_name, df in report_dict.items():
            # Create a copy to prevent modifying the source dataframe
            df_export = df.copy()

            # Handle Excel's timezone limitation: strip TZ info from all datetime columns
            for col in df_export.columns:
                if pd.api.types.is_datetime64_any_dtype(df_export[col]):
                    if df_export[col].dt.tz is not None:
                        df_export[col] = df_export[col].dt.tz_localize(None)

            # Clean sheet name for Excel constraints (31 chars, no invalid chars)
            clean_name = str(sheet_name)[:31].replace('/', '_').replace(':', '')
            df_export.to_excel(writer, sheet_name=clean_name, index=False)
            
            workbook = writer.book
            worksheet = writer.sheets[clean_name]
            
            # Format: Display decimal 1.0 as 100%
            percent_fmt = workbook.add_format({'num_format': '0%'})
            
            # Formatting loop
            for i, col in enumerate(df_export.columns):
                if '%' in col or 'Percentage' in col:
                    # Apply 3-color scale (Red-Yellow-Green)
                    worksheet.conditional_format(1, i, len(df_export), i, {
                        'type': '3_color_scale',
                        'min_color': "#F8696B", # Red
                        'mid_color': "#FFEB84", # Yellow
                        'max_color': "#63BE7B"  # Green
                    })
                    # Set the column format to Percentage
                    worksheet.set_column(i, i, 12, percent_fmt)
                else:
                    # Standard width for other columns
                    worksheet.set_column(i, i, 18)
                    
    return output.getvalue()

def generate_visuals(df):
    """
    Generates Plotly charts for the visual dashboard tab.
    """
    # a. Status by Biz Segment (Column Chart)
    fig_a = px.bar(df, x='biz_segment', color='transaction_status', barmode='group', 
                   title="Transaction Status by Business Segment")
    
    # b. Status by Tran Type (Column Chart)
    type_col = next((c for c in df.columns if 'type' in c), 'transaction_type')
    fig_b = px.bar(df, x=type_col, color='transaction_status', barmode='group', 
                   title="Transaction Status by Type")
    
    # c. Distribution of Error Segments (Including Success/Operational)
    fig_c = px.pie(df, names='error_segment', 
                   title="Overall Distribution: Success vs Failure Segments",
                   hole=0.4, # Donut style
                   color_discrete_sequence=px.colors.qualitative.Safe)
    
    # d. Bar charts of the final message when trans status are failed
    df_fails = df[df['transaction_status'].str.lower() == 'failed']
    if not df_fails.empty:
        msg_counts = df_fails['final_message'].value_counts().reset_index()
        msg_counts.columns = ['Final Message', 'Count']
        fig_d = px.bar(msg_counts, x='Final Message', y='Count', 
                       title="Top Failure Reasons (Failed Transactions Only)",
                       color='Count', color_continuous_scale='Reds')
    else:
        fig_d = px.bar(title="No Failures Recorded in Dataset")
    
    return {"fig_a": fig_a, "fig_b": fig_b, "fig_c": fig_c, "fig_d": fig_d}