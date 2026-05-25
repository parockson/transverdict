import pandas as pd
import plotly.express as px
import io

def generate_pivot_report(df, index_cols):
    """
    Generates count and percentage tables for error segments.
    Percentages are returned as decimals (e.g., 0.85) for professional formatting.
    """
    # Ensure all segments are represented
    segments = ['External', 'Customer', 'Internal', 'Op. Success']
    
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
        'Op. Success': ('Success Count', 'Success %')
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
    2. Professional nested table headers matching the provided visual design
    3. Custom cell borders, fonts (Century Gothic), and alignments
    4. 3-Color Scale conditional formatting for all % columns
    """
    header_mapping = {
        "Transformed Data": "RAW AND TRANSFORMED TRANSACTION DATA",
        "Response Codes": "TRANSACTION STATUSES REPORT BY RESPONSE CODES (TERMINATORS)",
        "Biz Segment": "TRANSACTION STATUSES REPORT BY BIZ SEGMENTS",
        "Client Name": "TRANSACTION STATUSES REPORT BY CLIENTS",
        "Biz & Client": "TRANSACTION STATUSES REPORT BY CLIENTS & BIZ SEGMENTS",
        "Transaction Type": "TRANSACTION STATUSES REPORT BY TRANSACTION TYPES",
        "Final Message Summary": "Distribution of Success and Error Messages"
    }

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # Define formats
        title_format = workbook.add_format({
            'font_name': 'Century Gothic',
            'font_size': 12,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        header_format = workbook.add_format({
            'font_name': 'Century Gothic',
            'font_size': 10,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        data_text_format = workbook.add_format({
            'font_name': 'Century Gothic',
            'font_size': 10,
            'align': 'left',
            'valign': 'vcenter',
            'border': 1
        })
        
        data_count_format = workbook.add_format({
            'font_name': 'Century Gothic',
            'font_size': 10,
            'align': 'center',
            'valign': 'vcenter',
            'num_format': '#,##0',
            'border': 1
        })
        
        data_percent_format = workbook.add_format({
            'font_name': 'Century Gothic',
            'font_size': 10,
            'align': 'center',
            'valign': 'vcenter',
            'num_format': '0%',
            'border': 1
        })
        
        total_label_format = workbook.add_format({
            'font_name': 'Century Gothic',
            'font_size': 10,
            'bold': True,
            'align': 'left',
            'valign': 'vcenter',
            'border': 1
        })
        
        total_count_format = workbook.add_format({
            'font_name': 'Century Gothic',
            'font_size': 10,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'num_format': '#,##0',
            'border': 1
        })
        
        total_percent_format = workbook.add_format({
            'font_name': 'Century Gothic',
            'font_size': 10,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'num_format': '0%',
            'border': 1
        })

        for sheet_name, df in report_dict.items():
            # Create a copy to prevent modifying the source dataframe
            df_export = df.copy()

            # Handle Excel's timezone limitation: strip TZ info from all datetime columns
            for col in df_export.columns:
                if pd.api.types.is_datetime64_any_dtype(df_export[col]):
                    if df_export[col].dt.tz is not None:
                        df_export[col] = df_export[col].dt.tz_localize(None)

            clean_name = str(sheet_name)[:31].replace('/', '_').replace(':', '')
            
            # Create the worksheet
            worksheet = workbook.add_worksheet(clean_name)
            writer.sheets[clean_name] = worksheet
            worksheet.hide_gridlines(2) # Show standard gridlines
            
            col_count = len(df_export.columns)
            
            # 1. Title banner in row 0
            sheet_title = header_mapping.get(sheet_name, f"{sheet_name.upper()} REPORT")
            worksheet.merge_range(0, 0, 0, col_count - 1, sheet_title, title_format)
            worksheet.set_row(0, 26) # Banner row height
            
            is_pivot = sheet_name not in ["Transformed Data", "Final Message Summary"]
            
            if is_pivot:
                # Number of index columns in the pivot report
                num_index_cols = len(df_export.columns) - 9
                
                worksheet.set_row(1, 20)
                worksheet.set_row(2, 20)
                
                # First header row: empty/blank for index columns
                for c in range(num_index_cols):
                    worksheet.write(1, c, "", header_format)
                
                # Merged headers for the segments in row 1
                worksheet.merge_range(1, num_index_cols, 1, num_index_cols + 1, "External", header_format)
                worksheet.merge_range(1, num_index_cols + 2, 1, num_index_cols + 3, "Customer", header_format)
                worksheet.merge_range(1, num_index_cols + 4, 1, num_index_cols + 5, "Internal", header_format)
                worksheet.merge_range(1, num_index_cols + 6, 1, num_index_cols + 7, "Success", header_format)
                worksheet.write(1, num_index_cols + 8, "Total", header_format)
                
                # Second header row: column names for indices and 'Count'/'Count %'
                for c in range(num_index_cols):
                    col_name = str(df_export.columns[c]).replace('_', ' ').title()
                    # Custom override for Response Code to match terminators
                    if col_name.lower() == 'response code':
                        col_name = 'Response Code'
                    worksheet.write(2, c, col_name, header_format)
                
                for c in range(num_index_cols, num_index_cols + 8, 2):
                    worksheet.write(2, c, "Count", header_format)
                    worksheet.write(2, c + 1, "Count %", header_format)
                
                worksheet.write(2, num_index_cols + 8, "count", header_format)
                
                # Write data rows
                for r_idx, row_val in enumerate(df_export.values):
                    row_num = 3 + r_idx
                    worksheet.set_row(row_num, 18)
                    
                    # Index columns (Left aligned text)
                    for c in range(num_index_cols):
                        val_str = str(row_val[c]) if not pd.isna(row_val[c]) else ""
                        worksheet.write(row_num, c, val_str, data_text_format)
                    
                    # Alternating Count and Count % columns
                    for c in range(num_index_cols, num_index_cols + 8, 2):
                        val_count = row_val[c]
                        val_pct = row_val[c + 1]
                        
                        worksheet.write(row_num, c, int(val_count) if not pd.isna(val_count) else 0, data_count_format)
                        worksheet.write(row_num, c + 1, float(val_pct) if not pd.isna(val_pct) else 0.0, data_percent_format)
                        
                    # Total count
                    val_tot = row_val[num_index_cols + 8]
                    worksheet.write(row_num, num_index_cols + 8, int(val_tot) if not pd.isna(val_tot) else 0, data_count_format)
                
                # Calculate and write Grand Total row
                total_row_num = 3 + len(df_export)
                worksheet.set_row(total_row_num, 20)
                
                ext_total = df_export['Ext Count'].sum()
                cust_total = df_export['Cust Count'].sum()
                inte_total = df_export['Inte Count'].sum()
                success_total = df_export['Success Count'].sum()
                transactions_total = df_export['Total Transactions'].sum()
                
                ext_pct = (ext_total / transactions_total) if transactions_total > 0 else 0.0
                cust_pct = (cust_total / transactions_total) if transactions_total > 0 else 0.0
                inte_pct = (inte_total / transactions_total) if transactions_total > 0 else 0.0
                success_pct = (success_total / transactions_total) if transactions_total > 0 else 0.0
                
                # Write labels
                for c in range(num_index_cols):
                    val = "Grand Total" if c == 0 else ""
                    worksheet.write(total_row_num, c, val, total_label_format)
                
                # Write totals
                worksheet.write(total_row_num, num_index_cols, int(ext_total), total_count_format)
                worksheet.write(total_row_num, num_index_cols + 1, float(ext_pct), total_percent_format)
                
                worksheet.write(total_row_num, num_index_cols + 2, int(cust_total), total_count_format)
                worksheet.write(total_row_num, num_index_cols + 3, float(cust_pct), total_percent_format)
                
                worksheet.write(total_row_num, num_index_cols + 4, int(inte_total), total_count_format)
                worksheet.write(total_row_num, num_index_cols + 5, float(inte_pct), total_percent_format)
                
                worksheet.write(total_row_num, num_index_cols + 6, int(success_total), total_count_format)
                worksheet.write(total_row_num, num_index_cols + 7, float(success_pct), total_percent_format)
                
                worksheet.write(total_row_num, num_index_cols + 8, int(transactions_total), total_count_format)
                
                # Apply 3-color scale conditional formatting for the % columns
                # This covers all data rows AND the Grand Total row
                for c in range(num_index_cols + 1, num_index_cols + 8, 2):
                    worksheet.conditional_format(3, c, total_row_num, c, {
                        'type': '3_color_scale',
                        'min_type': 'num',
                        'min_value': 0,
                        'min_color': "#F8696B", # Red
                        'mid_type': 'num',
                        'mid_value': 0.5,
                        'mid_color': "#FFEB84", # Yellow
                        'max_type': 'num',
                        'max_value': 1,
                        'max_color': "#63BE7B"  # Green
                    })
                
                # Column widths
                for c in range(num_index_cols):
                    worksheet.set_column(c, c, 20)
                for c in range(num_index_cols, num_index_cols + 9):
                    worksheet.set_column(c, c, 12)
            
            elif sheet_name == "Final Message Summary":
                # Flat sheet with 4 columns: Error Segment, Final Message, Count, Percentage
                worksheet.set_row(1, 20)
                
                # Column headers
                for c, col_name in enumerate(df_export.columns):
                    worksheet.write(1, c, str(col_name).replace('_', ' ').title(), header_format)
                
                # Data rows
                for r_idx, row_val in enumerate(df_export.values):
                    row_num = 2 + r_idx
                    worksheet.set_row(row_num, 18)
                    worksheet.write(row_num, 0, str(row_val[0]) if not pd.isna(row_val[0]) else "", data_text_format)
                    worksheet.write(row_num, 1, str(row_val[1]) if not pd.isna(row_val[1]) else "", data_text_format)
                    worksheet.write(row_num, 2, int(row_val[2]) if not pd.isna(row_val[2]) else 0, data_count_format)
                    worksheet.write(row_num, 3, float(row_val[3]) if not pd.isna(row_val[3]) else 0.0, data_percent_format)
                
                # Grand Total row
                total_row_num = 2 + len(df_export)
                worksheet.set_row(total_row_num, 20)
                sum_count = df_export['Count'].sum()
                
                worksheet.write(total_row_num, 0, "Grand Total", total_label_format)
                worksheet.write(total_row_num, 1, "", total_label_format)
                worksheet.write(total_row_num, 2, int(sum_count), total_count_format)
                worksheet.write(total_row_num, 3, 1.0, total_percent_format)
                
                # Apply 3-color scale on the Percentage column
                worksheet.conditional_format(2, 3, total_row_num, 3, {
                    'type': '3_color_scale',
                    'min_type': 'num',
                    'min_value': 0,
                    'min_color': "#F8696B",
                    'mid_type': 'num',
                    'mid_value': 0.5,
                    'mid_color': "#FFEB84",
                    'max_type': 'num',
                    'max_value': 1,
                    'max_color': "#63BE7B"
                })
                
                worksheet.set_column(0, 0, 18)
                worksheet.set_column(1, 1, 35)
                worksheet.set_column(2, 3, 15)
                
            else:
                # Transformed Data (Detail list sheet)
                worksheet.set_row(1, 20)
                # Column headers
                for c, col_name in enumerate(df_export.columns):
                    worksheet.write(1, c, str(col_name).replace('_', ' ').title(), header_format)
                
                # Data rows
                for r_idx, row_val in enumerate(df_export.values):
                    row_num = 2 + r_idx
                    worksheet.set_row(row_num, 18)
                    for c in range(col_count):
                        val = row_val[c]
                        if pd.isna(val):
                            val = ""
                        
                        col_label = df_export.columns[c]
                        if '%' in col_label or 'Percentage' in col_label:
                            worksheet.write(row_num, c, float(val) if val != "" else 0.0, data_percent_format)
                        elif pd.api.types.is_numeric_dtype(df_export[col_label]):
                            worksheet.write(row_num, c, int(val) if val != "" else 0, data_count_format)
                        else:
                            worksheet.write(row_num, c, str(val), data_text_format)
                
                # Set dynamic column widths
                for c, col_name in enumerate(df_export.columns):
                    width = max(len(str(col_name)) + 4, 15)
                    worksheet.set_column(c, c, width)
                    
    return output.getvalue()

def generate_visuals(df):
    """
    Generates Plotly charts for the visual dashboard tab.
    """
    # a. Status by Biz Segment (Column Chart)
    df_grouped_a = df.groupby(['biz_segment', 'transaction_status']).size().reset_index(name='count')
    fig_a = px.bar(df_grouped_a, x='biz_segment', y='count', color='transaction_status', barmode='group', 
                   title="Transaction Status by Business Segment")
    
    # b. Status by Tran Type (Column Chart)
    type_col = next((c for c in df.columns if 'type' in c), 'transaction_type')
    df_grouped_b = df.groupby([type_col, 'transaction_status']).size().reset_index(name='count')
    fig_b = px.bar(df_grouped_b, x=type_col, y='count', color='transaction_status', barmode='group', 
                   title="Transaction Status by Type")
    
    # c. Distribution of Error Segments (Including Success/Op. Success)
    df_grouped_c = df.groupby('error_segment').size().reset_index(name='count')
    fig_c = px.pie(df_grouped_c, names='error_segment', values='count',
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