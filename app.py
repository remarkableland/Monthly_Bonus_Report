import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from io import BytesIO

st.set_page_config(
    page_title="Remarkable Land Bonus Schedule Generator",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Remarkable Land® Bonus Schedule Generator")
st.markdown("Generate professional bonus schedule PDFs with improved formatting")

# Create tabs for different input methods
tab1, tab2 = st.tabs(["📤 Upload CSV", "✏️ Manual Entry"])

def create_bonus_schedule_pdf(data, month_ending, prior_adjustment=0.00):
    """
    Generate a professional bonus schedule PDF
    
    Args:
        data: DataFrame with columns: Funding Date, State, County, Grantor, APN, 
              Contract Sales Price, Reductions, Cash to Seller, Asset Cost, Gross Profit
        month_ending: Date string for the month ending
        prior_adjustment: Prior adjustment amount (default 0.00)
    """
    buffer = BytesIO()
    
    # Create PDF with narrow margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        topMargin=0.5*inch,
        bottomMargin=0.5*inch,
        leftMargin=0.5*inch,
        rightMargin=0.5*inch
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1f4e78'),
        alignment=TA_CENTER,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_CENTER,
        spaceAfter=12
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.white,
        leading=10
    )
    
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER
    )
    
    notes_style = ParagraphStyle(
        'NotesStyle',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        spaceAfter=4
    )
    
    # Build the document
    story = []
    
    # Title
    title = Paragraph("Remarkable Land<super>®</super> Bonus Schedule", title_style)
    story.append(title)
    
    # Subtitle
    subtitle = Paragraph(f"Month Ending: {month_ending}", subtitle_style)
    story.append(subtitle)
    story.append(Spacer(1, 0.1*inch))
    
    # Table data with wrapped headers
    table_data = [
        # Headers
        [
            Paragraph("<b>Funding<br/>Date</b>", header_style),
            Paragraph("<b>State</b>", header_style),
            Paragraph("<b>County</b>", header_style),
            Paragraph("<b>Grantor</b>", header_style),
            Paragraph("<b>APN</b>", header_style),
            Paragraph("<b>Contract<br/>Sales Price</b>", header_style),
            Paragraph("<b>Reductions</b>", header_style),
            Paragraph("<b>Cash to<br/>Seller</b>", header_style),
            Paragraph("<b>Asset<br/>Cost</b>", header_style),
            Paragraph("<b>Gross<br/>Profit</b>", header_style),
        ],
    ]
    
    # Add data rows
    for _, row in data.iterrows():
        # Format APN with line breaks for long numbers
        apn = str(row['APN'])
        if len(apn) > 15:
            # Add line break in the middle for long APNs
            mid = len(apn) // 2
            apn_formatted = f"{apn[:mid]}<br/>{apn[mid:]}"
        else:
            apn_formatted = apn
        
        table_data.append([
            Paragraph(row['Funding Date'], cell_style),
            Paragraph(str(row['State']), cell_style),
            Paragraph(str(row['County']), cell_style),
            Paragraph(str(row['Grantor']), cell_style),
            Paragraph(apn_formatted, cell_style),
            Paragraph(f"${float(row['Contract Sales Price']):,.2f}", cell_style),
            Paragraph(f"${float(row['Reductions']):,.2f}", cell_style),
            Paragraph(f"${float(row['Cash to Seller']):,.2f}", cell_style),
            Paragraph(f"${float(row['Asset Cost']):,.2f}", cell_style),
            Paragraph(f"${float(row['Gross Profit']):,.2f}", cell_style),
        ])
    
    # Column widths
    col_widths = [
        0.7*inch,   # Funding Date
        0.5*inch,   # State
        0.8*inch,   # County
        0.9*inch,   # Grantor
        1.3*inch,   # APN (widened)
        0.95*inch,  # Contract Sales Price
        0.8*inch,   # Reductions
        0.9*inch,   # Cash to Seller
        0.85*inch,  # Asset Cost
        0.85*inch,  # Gross Profit
    ]
    
    # Create table
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    # Table styling with alternating row colors
    style_commands = [
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e78')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        
        # Data rows
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#1f4e78')),
    ]
    
    # Add alternating row colors
    for i in range(1, len(table_data)):
        if i % 2 == 1:
            style_commands.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#e7f0f7')))
        else:
            style_commands.append(('BACKGROUND', (0, i), (-1, i), colors.white))
    
    table.setStyle(TableStyle(style_commands))
    
    story.append(table)
    story.append(Spacer(1, 0.2*inch))
    
    # Calculate totals
    subtotal = data['Gross Profit'].sum()
    total = subtotal + prior_adjustment
    
    # Totals section
    totals_data = [
        ['', '', '', '', '', '', '', '', 'SUBTOTAL:', f'${subtotal:,.2f}'],
        ['', '', '', '', '', '', '', '', 'PRIOR ADJUSTMENT:', f'${prior_adjustment:,.2f}'],
        ['', '', '', '', '', '', '', '', 'TOTAL:', f'${total:,.2f}'],
    ]
    
    totals_table = Table(totals_data, colWidths=col_widths)
    totals_table.setStyle(TableStyle([
        ('ALIGN', (8, 0), (8, -1), 'RIGHT'),
        ('ALIGN', (9, 0), (9, -1), 'RIGHT'),
        ('FONTNAME', (8, 0), (9, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (8, 0), (9, -1), 10),
        ('LINEABOVE', (8, 0), (9, 0), 1, colors.grey),
        ('LINEABOVE', (8, 2), (9, 2), 2, colors.black),
        ('TEXTCOLOR', (8, 2), (9, 2), colors.HexColor('#1f4e78')),
    ]))
    
    story.append(totals_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Notes section
    notes_title = Paragraph("<b>Notes:</b>", notes_style)
    story.append(notes_title)
    
    notes = [
        "<b>Funding Date:</b> Date funds were available for withdrawal from our account. \"Pending\" funds are not available for withdrawal. Accounting will confirm funding.",
        "<b>Cash to Seller:</b> Net Cash to Seller on HUD Statement.",
        "<b>Asset Cost:</b> Net Cash from Buyer on HUD Statement + $500 (which includes MLS) + Direct Property Expenses, including Photographer, Videographer, Legal, etc.",
        "<b>Reconciliation:</b> All data is subject to a post-payment audit and reconciliation. Future Bonuses will be adjusted accordingly, as required.",
    ]
    
    for note in notes:
        story.append(Paragraph(note, notes_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Signatures section
    sig_title = Paragraph("<b>Signatures:</b>", notes_style)
    story.append(sig_title)
    story.append(Spacer(1, 0.1*inch))
    
    sig_data = [
        ['Brandi Freeman', '_' * 50, 'Lauren Forbis', '_' * 50],
        ['', '', '', ''],
        ['Robert O. Dow', '_' * 50, '', ''],
    ]
    
    sig_table = Table(sig_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 2.5*inch])
    sig_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(sig_table)
    
    # Build the PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer

# Tab 1: Upload CSV
with tab1:
    st.subheader("📤 Upload Bonus Data CSV")
    
    st.markdown("""
    **Required CSV Columns:**
    - Funding Date
    - State
    - County
    - Grantor
    - APN
    - Contract Sales Price
    - Reductions
    - Cash to Seller
    - Asset Cost
    - Gross Profit
    """)
    
    uploaded_file = st.file_uploader("Choose your bonus data CSV file", type=['csv'])
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            
            # Validate required columns
            required_columns = [
                'Funding Date', 'State', 'County', 'Grantor', 'APN',
                'Contract Sales Price', 'Reductions', 'Cash to Seller',
                'Asset Cost', 'Gross Profit'
            ]
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
                st.write("**Available columns:**", list(df.columns))
            else:
                st.success(f"✅ Loaded {len(df)} bonus records successfully!")
                
                # Display preview
                st.subheader("📊 Data Preview")
                st.dataframe(df, use_container_width=True)
                
                # Input fields
                col1, col2 = st.columns(2)
                
                with col1:
                    month_ending = st.text_input(
                        "Month Ending Date",
                        value=datetime.now().strftime("%B %d, %Y"),
                        help="E.g., October 23, 2025"
                    )
                
                with col2:
                    prior_adjustment = st.number_input(
                        "Prior Adjustment",
                        value=0.00,
                        step=0.01,
                        format="%.2f",
                        help="Enter any prior adjustment amount (can be negative)"
                    )
                
                # Generate PDF button
                if st.button("📄 Generate Bonus Schedule PDF", type="primary"):
                    with st.spinner("Generating PDF..."):
                        pdf_buffer = create_bonus_schedule_pdf(df, month_ending, prior_adjustment)
                        
                        # Create filename
                        date_str = datetime.now().strftime("%Y%m%d")
                        filename = f"{date_str}_Remarkable_Land_Bonus_Schedule.pdf"
                        
                        # Download button
                        st.download_button(
                            label="📥 Download Bonus Schedule PDF",
                            data=pdf_buffer,
                            file_name=filename,
                            mime="application/pdf"
                        )
                        
                        st.success("✅ PDF generated successfully!")
                        
                        # Show summary
                        st.subheader("📈 Bonus Summary")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Total Transactions", len(df))
                        
                        with col2:
                            subtotal = df['Gross Profit'].sum()
                            st.metric("Subtotal", f"${subtotal:,.2f}")
                        
                        with col3:
                            total = subtotal + prior_adjustment
                            st.metric("Total (with adjustment)", f"${total:,.2f}")
        
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

# Tab 2: Manual Entry
with tab2:
    st.subheader("✏️ Manual Data Entry")
    
    # Input fields for month ending and prior adjustment
    col1, col2 = st.columns(2)
    
    with col1:
        month_ending_manual = st.text_input(
            "Month Ending Date",
            value=datetime.now().strftime("%B %d, %Y"),
            help="E.g., October 23, 2025",
            key="manual_month"
        )
    
    with col2:
        prior_adjustment_manual = st.number_input(
            "Prior Adjustment",
            value=0.00,
            step=0.01,
            format="%.2f",
            help="Enter any prior adjustment amount",
            key="manual_adjustment"
        )
    
    # Number of transactions
    num_transactions = st.number_input(
        "Number of Transactions",
        min_value=1,
        max_value=20,
        value=2,
        step=1
    )
    
    # Create data entry form
    data_rows = []
    
    st.markdown("---")
    st.markdown("### Enter Transaction Details")
    
    for i in range(num_transactions):
        with st.expander(f"Transaction #{i+1}", expanded=(i < 2)):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                funding_date = st.text_input(
                    "Funding Date",
                    value="10/17/25",
                    key=f"date_{i}"
                )
            
            with col2:
                state = st.text_input(
                    "State",
                    value="TX",
                    key=f"state_{i}",
                    max_chars=2
                )
            
            with col3:
                county = st.text_input(
                    "County",
                    value="",
                    key=f"county_{i}"
                )
            
            with col4:
                grantor = st.text_input(
                    "Grantor",
                    value="",
                    key=f"grantor_{i}"
                )
            
            col1, col2 = st.columns(2)
            
            with col1:
                apn = st.text_input(
                    "APN",
                    value="",
                    key=f"apn_{i}"
                )
            
            with col2:
                contract_price = st.number_input(
                    "Contract Sales Price",
                    value=0.00,
                    step=100.00,
                    format="%.2f",
                    key=f"contract_{i}"
                )
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                reductions = st.number_input(
                    "Reductions",
                    value=0.00,
                    step=10.00,
                    format="%.2f",
                    key=f"reductions_{i}"
                )
            
            with col2:
                cash_to_seller = st.number_input(
                    "Cash to Seller",
                    value=contract_price - reductions,
                    step=10.00,
                    format="%.2f",
                    key=f"cash_{i}"
                )
            
            with col3:
                asset_cost = st.number_input(
                    "Asset Cost",
                    value=0.00,
                    step=100.00,
                    format="%.2f",
                    key=f"cost_{i}"
                )
            
            with col4:
                gross_profit = cash_to_seller - asset_cost
                st.number_input(
                    "Gross Profit",
                    value=gross_profit,
                    step=10.00,
                    format="%.2f",
                    key=f"profit_{i}",
                    disabled=True
                )
            
            # Add to data rows
            data_rows.append({
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
    
    st.markdown("---")
    
    # Generate PDF button
    if st.button("📄 Generate Bonus Schedule PDF from Manual Entry", type="primary"):
        # Validate that at least some data is entered
        if all(row['Grantor'] == '' for row in data_rows):
            st.warning("⚠️ Please enter at least one transaction with grantor name")
        else:
            # Filter out empty rows
            valid_rows = [row for row in data_rows if row['Grantor'] != '']
            
            if valid_rows:
                with st.spinner("Generating PDF..."):
                    df_manual = pd.DataFrame(valid_rows)
                    pdf_buffer = create_bonus_schedule_pdf(
                        df_manual, 
                        month_ending_manual, 
                        prior_adjustment_manual
                    )
                    
                    # Create filename
                    date_str = datetime.now().strftime("%Y%m%d")
                    filename = f"{date_str}_Remarkable_Land_Bonus_Schedule.pdf"
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Bonus Schedule PDF",
                        data=pdf_buffer,
                        file_name=filename,
                        mime="application/pdf"
                    )
                    
                    st.success("✅ PDF generated successfully!")
                    
                    # Show summary
                    st.subheader("📈 Bonus Summary")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Transactions", len(valid_rows))
                    
                    with col2:
                        subtotal = sum(row['Gross Profit'] for row in valid_rows)
                        st.metric("Subtotal", f"${subtotal:,.2f}")
                    
                    with col3:
                        total = subtotal + prior_adjustment_manual
                        st.metric("Total (with adjustment)", f"${total:,.2f}")

# Sidebar with instructions
with st.sidebar:
    st.header("📋 Instructions")
    
    st.markdown("""
    ### How to Use
    
    **Option 1: Upload CSV**
    1. Prepare a CSV file with required columns
    2. Upload the file
    3. Review the data preview
    4. Set month ending date
    5. Add any prior adjustments
    6. Generate and download PDF
    
    **Option 2: Manual Entry**
    1. Set number of transactions
    2. Enter details for each transaction
    3. Set month ending date
    4. Add any prior adjustments
    5. Generate and download PDF
    
    ### Features
    
    ✅ Landscape orientation for wider tables  
    ✅ Narrow 0.5" margins  
    ✅ Wrapped column headers  
    ✅ Wide APN column (1.3")  
    ✅ Professional color scheme  
    ✅ Alternating row colors  
    ✅ Automatic calculations  
    ✅ Signature lines included  
    
    ### PDF Improvements
    
    - **Wider Table:** Uses full page width
    - **Better APN Display:** Extra wide column with line breaks
    - **Clean Headers:** Multi-line wrapped text
    - **Professional Design:** Blue header, alternating rows
    - **Complete Notes:** All standard disclaimers included
    """)
    
    st.markdown("---")
    st.markdown("**Rainmaker AI Mastery Project**")
    st.markdown("Version 1.0")
