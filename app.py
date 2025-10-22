import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(
    page_title="Bonus Schedule Generator",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Remarkable Land Bonus Schedule Generator")
st.markdown("Generate bonus schedules from Close.com export data")

# Configuration Section
st.sidebar.header("Configuration")

# Month/Period Selection
month_ending = st.sidebar.date_input(
    "Month Ending Date",
    value=datetime.now().replace(day=1) if datetime.now().day == 1 else datetime.now()
)

# Team Member Names (for signatures)
st.sidebar.subheader("Team Members")
team_members = st.sidebar.text_area(
    "Enter team member names (one per line)",
    value="Brandi Freeman\nRyan Nettleship\nLauren Forbis\nRobert O. Dow",
    height=150
)
team_list = [name.strip() for name in team_members.split('\n') if name.strip()]

# Additional Costs Configuration
st.sidebar.subheader("Standard Costs")
mls_cost = st.sidebar.number_input("MLS Cost", value=500, min_value=0)

# Prior Adjustment
prior_adjustment = st.sidebar.number_input(
    "Prior Adjustment Amount", 
    value=0.00,
    format="%.2f",
    help="Adjustments from previous bonus schedules"
)

# File Upload
uploaded_file = st.file_uploader(
    "Upload Close.com Export CSV", 
    type=['csv'],
    help="Upload your 'Selling_Land_leads' export from Close.com"
)

def extract_county_from_display_name(display_name):
    """Extract county from display name like 'TX Hidalgo Mujica...'"""
    if pd.isna(display_name):
        return "Unknown"
    parts = str(display_name).split()
    if len(parts) >= 2:
        return parts[1]  # Second word is typically the county
    return "Unknown"

def extract_grantor_from_display_name(display_name):
    """Extract grantor name from display name like 'OK McIntosh Engebretson...'"""
    if pd.isna(display_name):
        return "Unknown"
    parts = str(display_name).split()
    if len(parts) >= 3:
        return parts[2]  # Third word is typically the grantor
    return "Unknown"

def process_close_export(df, month_ending_date):
    """Process Close.com export and extract relevant fields"""
    
    # Filter for sold properties in the specified month
    df['primary_opportunity_date_won'] = pd.to_datetime(df['primary_opportunity_date_won'], errors='coerce')
    
    # Filter by month and year
    month_start = pd.Timestamp(month_ending_date.replace(day=1))
    if month_ending_date.month == 12:
        month_end = pd.Timestamp(month_ending_date.replace(year=month_ending_date.year + 1, month=1, day=1))
    else:
        month_end = pd.Timestamp(month_ending_date.replace(month=month_ending_date.month + 1, day=1))
    
    df_filtered = df[
        (df['primary_opportunity_date_won'] >= month_start) & 
        (df['primary_opportunity_date_won'] < month_end) &
        (df['primary_opportunity_status_label'] == 'Sold')
    ].copy()
    
    if len(df_filtered) == 0:
        return None
    
    # Extract required fields
    results = []
    for _, row in df_filtered.iterrows():
        # Extract data from available fields
        funding_date = pd.to_datetime(row['custom.Asset_Date_Sold']).strftime('%m/%d/%y') if pd.notna(row['custom.Asset_Date_Sold']) else ''
        state = row['custom.All_State'] if pd.notna(row['custom.All_State']) else ''
        county = extract_county_from_display_name(row['display_name'])
        grantor = extract_grantor_from_display_name(row['display_name'])
        apn = row['custom.All_APN'] if pd.notna(row['custom.All_APN']) else ''
        
        # Financial data
        contract_price = float(row['custom.Asset_Gross_Sales_Price']) if pd.notna(row['custom.Asset_Gross_Sales_Price']) else 0.0
        closing_costs = float(row['custom.Asset_Closing_Costs']) if pd.notna(row['custom.Asset_Closing_Costs']) else 0.0
        cost_basis = float(row['custom.Asset_Cost_Basis']) if pd.notna(row['custom.Asset_Cost_Basis']) else 0.0
        
        # Calculate derived values
        reductions = closing_costs  # Using closing costs as "reductions"
        cash_to_seller = contract_price - reductions
        asset_cost = cost_basis + mls_cost  # Add MLS cost to cost basis
        gross_profit = cash_to_seller - asset_cost
        
        results.append({
            'Funding Date': funding_date,
            'State': state,
            'County': county,
            'Grantor': grantor,
            'APN': apn,
            'Contract Sales Price': contract_price,
            'Reductions': reductions,
            'Cash to Seller': cash_to_seller,
            'Asset Cost': asset_cost,
            'Gross Profit': gross_profit
        })
    
    return pd.DataFrame(results)

def format_currency(value):
    """Format number as currency"""
    return f"${value:,.2f}"

def create_bonus_schedule_dataframe(processed_df):
    """Create formatted bonus schedule dataframe"""
    # Format currency columns
    for col in ['Contract Sales Price', 'Reductions', 'Cash to Seller', 'Asset Cost', 'Gross Profit']:
        processed_df[col] = processed_df[col].apply(format_currency)
    
    return processed_df

def export_to_excel(processed_df, month_ending_date, subtotal, prior_adj, total):
    """Export bonus schedule to Excel with formatting"""
    output = io.BytesIO()
    
    # Create Excel writer
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Write main data
        processed_df.to_excel(writer, sheet_name='Bonus Schedule', index=False, startrow=2)
        
        # Get workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Bonus Schedule']
        
        # Add header
        worksheet['A1'] = f'Remarkable Land® Bonus Schedule'
        worksheet['A2'] = f'Month Ending: {month_ending_date.strftime("%m/%d/%Y")}'
        
        # Add totals
        last_row = len(processed_df) + 4
        worksheet[f'I{last_row}'] = 'SUBTOTAL'
        worksheet[f'J{last_row}'] = subtotal
        
        worksheet[f'I{last_row+1}'] = 'PRIOR ADJUSTMENT'
        worksheet[f'J{last_row+1}'] = prior_adj
        
        worksheet[f'I{last_row+2}'] = 'TOTAL'
        worksheet[f'J{last_row+2}'] = total
        
        # Bold the header
        from openpyxl.styles import Font, Alignment
        worksheet['A1'].font = Font(bold=True, size=14)
        worksheet['A2'].font = Font(bold=True)
        
        # Bold totals
        for row_num in [last_row, last_row+1, last_row+2]:
            worksheet[f'I{row_num}'].font = Font(bold=True)
            worksheet[f'J{row_num}'].font = Font(bold=True)
        
        # Adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    output.seek(0)
    return output

# Main Processing
if uploaded_file is not None:
    try:
        # Read the CSV
        df = pd.read_csv(uploaded_file)
        
        st.success(f"✅ Loaded {len(df)} records from Close.com export")
        
        # Process the data
        with st.spinner("Processing sales data..."):
            processed_df = process_close_export(df, month_ending)
        
        if processed_df is None or len(processed_df) == 0:
            st.warning(f"⚠️ No sold properties found for {month_ending.strftime('%B %Y')}")
        else:
            # Calculate totals
            # Parse currency strings back to float for calculation
            gross_profits = []
            for val in processed_df['Gross Profit']:
                clean_val = val.replace('$', '').replace(',', '')
                gross_profits.append(float(clean_val))
            
            subtotal = sum(gross_profits)
            total = subtotal + prior_adjustment
            
            # Display Summary
            st.header("📊 Bonus Schedule Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Properties Sold", len(processed_df))
            with col2:
                st.metric("Subtotal", format_currency(subtotal))
            with col3:
                st.metric("Prior Adjustment", format_currency(prior_adjustment))
            with col4:
                st.metric("Total Bonus", format_currency(total))
            
            st.divider()
            
            # Display the bonus schedule
            st.header("💰 Bonus Schedule Details")
            
            # Format for display
            display_df = processed_df.copy()
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Add totals row
            st.markdown("---")
            col1, col2, col3 = st.columns([2, 1, 1])
            with col2:
                st.markdown("**SUBTOTAL:**")
                st.markdown("**PRIOR ADJUSTMENT:**")
                st.markdown("**TOTAL:**")
            with col3:
                st.markdown(f"**{format_currency(subtotal)}**")
                st.markdown(f"**{format_currency(prior_adjustment)}**")
                st.markdown(f"**{format_currency(total)}**")
            
            st.divider()
            
            # Notes Section
            st.header("📝 Notes")
            st.markdown("""
            **Funding Date:** Date funds were available for withdrawal from our account. 
            "Pending" funds are not available for withdrawal. Accounting will confirm funding.
            
            **Cash to Seller:** Net Cash to Seller on HUD Statement.
            
            **Asset Cost:** Net Cash from Buyer on HUD Statement + $500 (which includes MLS) + 
            Direct Property Expenses, including Photographer, Videographer, Legal, etc.
            
            **Reconciliation:** All data is subject to a post-payment audit and reconciliation. 
            Future Bonuses will be adjusted accordingly, as required.
            """)
            
            # Signature Section
            st.header("✍️ Signatures")
            
            # Create signature placeholders
            num_cols = min(len(team_list), 4)
            if num_cols > 0:
                cols = st.columns(num_cols)
                for idx, name in enumerate(team_list):
                    with cols[idx % num_cols]:
                        st.markdown(f"**{name}** ☐")
            
            st.divider()
            
            # Export Options
            st.header("📥 Download Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Excel Export
                excel_data = export_to_excel(
                    processed_df.copy(), 
                    month_ending, 
                    format_currency(subtotal),
                    format_currency(prior_adjustment),
                    format_currency(total)
                )
                
                filename = f"{month_ending.strftime('%Y%m%d')}_Remarkable_Land_Bonus_Schedule.xlsx"
                
                st.download_button(
                    label="📊 Download Excel",
                    data=excel_data,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            with col2:
                # CSV Export
                csv = processed_df.to_csv(index=False)
                csv_filename = f"{month_ending.strftime('%Y%m%d')}_Remarkable_Land_Bonus_Schedule.csv"
                
                st.download_button(
                    label="📄 Download CSV",
                    data=csv,
                    file_name=csv_filename,
                    mime="text/csv"
                )
    
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.exception(e)

else:
    # Instructions
    st.info("👆 Upload your Close.com 'Selling_Land_leads' export CSV to generate the bonus schedule")
    
    st.markdown("""
    ### 📋 Instructions:
    
    1. **Export from Close.com:**
       - Go to your "Selling Land" organization
       - Filter for sold properties
       - Export as CSV
    
    2. **Configure Settings:**
       - Set the month ending date (left sidebar)
       - Adjust team member names for signatures
       - Set any prior adjustments if needed
    
    3. **Upload & Generate:**
       - Upload your CSV file
       - Review the generated bonus schedule
       - Download as Excel or CSV
    
    ### 💡 Tips:
    - The app automatically filters for properties sold in the selected month
    - Asset Cost = Cost Basis + $500 (MLS) + Direct Expenses
    - Gross Profit = Cash to Seller - Asset Cost
    - All currency values are formatted automatically
    """)
    
    # Sample data structure
    with st.expander("📊 Expected CSV Structure"):
        st.markdown("""
        The CSV should contain these key columns:
        - `primary_opportunity_date_won` - Closing date
        - `custom.Asset_Date_Sold` - Funding date
        - `custom.All_State` - Property state
        - `custom.All_APN` - Property APN
        - `custom.Asset_Gross_Sales_Price` - Contract price
        - `custom.Asset_Closing_Costs` - Reductions/costs
        - `custom.Asset_Cost_Basis` - Original cost basis
        - `display_name` - Property name (contains county and grantor)
        """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    Built for Remarkable Land® | Bonus Schedule Generator v1.0
    </div>
    """,
    unsafe_allow_html=True
)
