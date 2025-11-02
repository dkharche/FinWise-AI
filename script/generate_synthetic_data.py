#!/usr/bin/env python3
"""
Generate synthetic financial documents for testing FinWise-AI.

Usage:
    python scripts/generate_synthetic_data.py --num 100
"""

import os
import sys
import random
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from faker import Faker
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import io

# Initialize
fake = Faker()
Faker.seed(42)
random.seed(42)

# Output directory
OUTPUT_DIR = Path("data/synthetic_documents")

class SyntheticDataGenerator:
    """Generate synthetic financial documents."""
    
    def __init__(self, num_documents=100):
        self.num_documents = num_documents
        self.fake = Faker()
        self.styles = getSampleStyleSheet()
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
    def generate_all(self):
        """Generate all types of documents."""
        print(f"\n{'='*70}")
        print(f"🚀 GENERATING {self.num_documents} SYNTHETIC FINANCIAL DOCUMENTS")
        print(f"{'='*70}\n")
        
        # Calculate distribution
        num_statements = int(self.num_documents * 0.6)  # 60%
        num_invoices = int(self.num_documents * 0.3)    # 30%
        num_reports = self.num_documents - num_statements - num_invoices  # 10%
        
        print(f"📊 Distribution:")
        print(f"  • Bank Statements (text-heavy): {num_statements} ({num_statements/self.num_documents*100:.0f}%)")
        print(f"  • Invoices (with tables):       {num_invoices} ({num_invoices/self.num_documents*100:.0f}%)")
        print(f"  • Financial Reports (charts):   {num_reports} ({num_reports/self.num_documents*100:.0f}%)")
        print(f"\n{'='*70}\n")
        
        # Generate bank statements
        print("📄 Generating Bank Statements...")
        for i in range(num_statements):
            self.generate_bank_statement(i)
            if (i + 1) % 10 == 0:
                print(f"  ✓ {i + 1}/{num_statements} completed")
        print(f"  ✅ All {num_statements} bank statements generated!\n")
        
        # Generate invoices
        print("🧾 Generating Invoices...")
        for i in range(num_invoices):
            self.generate_invoice(i)
            if (i + 1) % 10 == 0:
                print(f"  ✓ {i + 1}/{num_invoices} completed")
        print(f"  ✅ All {num_invoices} invoices generated!\n")
        
        # Generate reports
        print("📊 Generating Financial Reports...")
        for i in range(num_reports):
            self.generate_financial_report(i)
        print(f"  ✅ All {num_reports} reports generated!\n")
        
        print(f"{'='*70}")
        print(f"✅ SUCCESS! Generated {self.num_documents} documents")
        print(f"📁 Location: {OUTPUT_DIR.absolute()}")
        print(f"{'='*70}\n")
    
    def generate_bank_statement(self, index):
        """Generate a synthetic bank statement (text-heavy)."""
        filename = OUTPUT_DIR / f"bank_statement_{index:03d}.pdf"
        doc = SimpleDocTemplate(str(filename), pagesize=letter)
        story = []
        
        # Header
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        story.append(Paragraph("BANK STATEMENT", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Account info
        account_number = self.fake.iban()
        account_holder = self.fake.name()
        start_date = self.fake.date_between(start_date='-90d', end_date='-60d')
        end_date = start_date + timedelta(days=30)
        
        info_style = self.styles['Normal']
        story.append(Paragraph(f"<b>Account Holder:</b> {account_holder}", info_style))
        story.append(Paragraph(f"<b>Account Number:</b> {account_number}", info_style))
        story.append(Paragraph(f"<b>Statement Period:</b> {start_date} to {end_date}", info_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Generate transactions
        num_transactions = random.randint(20, 50)
        transactions = [['Date', 'Description', 'Amount', 'Balance']]
        current_balance = random.uniform(5000, 15000)
        
        for _ in range(num_transactions):
            trans_date = self.fake.date_between(start_date=start_date, end_date=end_date)
            
            if random.random() < 0.7:  # 70% expenses
                amount = -random.uniform(10, 500)
                description = random.choice([
                    f"Purchase at {self.fake.company()}",
                    f"Payment to {self.fake.name()}",
                    f"Grocery - {self.fake.company()}",
                    f"Restaurant - {self.fake.company()}",
                    f"Gas Station - {self.fake.company()}",
                    f"Online Purchase - Amazon",
                    "ATM Withdrawal",
                    f"Utility Bill - Electric Co",
                ])
            else:  # 30% income
                amount = random.uniform(100, 3000)
                description = random.choice([
                    "Salary Deposit",
                    "Direct Deposit",
                    f"Transfer from {self.fake.name()}",
                    "Interest Credit",
                ])
            
            current_balance += amount
            transactions.append([
                trans_date.strftime('%Y-%m-%d'),
                description,
                f"${amount:,.2f}",
                f"${current_balance:,.2f}"
            ])
        
        # Create table
        table = Table(transactions, colWidths=[1.2*inch, 3*inch, 1.2*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        # Summary
        total_deposits = sum(float(t[2].replace('$', '').replace(',', '')) 
                           for t in transactions[1:] 
                           if float(t[2].replace('$', '').replace(',', '')) > 0)
        total_withdrawals = abs(sum(float(t[2].replace('$', '').replace(',', '')) 
                                   for t in transactions[1:] 
                                   if float(t[2].replace('$', '').replace(',', '')) < 0))
        
        story.append(Paragraph(f"<b>Total Deposits:</b> ${total_deposits:,.2f}", info_style))
        story.append(Paragraph(f"<b>Total Withdrawals:</b> ${total_withdrawals:,.2f}", info_style))
        story.append(Paragraph(f"<b>Ending Balance:</b> ${current_balance:,.2f}", info_style))
        
        doc.build(story)
    
    def generate_invoice(self, index):
        """Generate a synthetic invoice with tables."""
        filename = OUTPUT_DIR / f"invoice_{index:03d}.pdf"
        doc = SimpleDocTemplate(str(filename), pagesize=letter)
        story = []
        
        # Header
        title_style = ParagraphStyle(
            'InvoiceTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#2ca02c'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        story.append(Paragraph("INVOICE", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Invoice details
        invoice_number = f"INV-{random.randint(10000, 99999)}"
        invoice_date = self.fake.date_between(start_date='-60d', end_date='today')
        due_date = invoice_date + timedelta(days=30)
        
        company_name = self.fake.company()
        client_name = self.fake.company()
        
        # Header info
        data = [
            ['From:', 'To:'],
            [company_name, client_name],
            [self.fake.address().replace('\n', ', '), self.fake.address().replace('\n', ', ')],
            ['', ''],
            [f'Invoice #: {invoice_number}', f'Date: {invoice_date}'],
            ['', f'Due Date: {due_date}'],
        ]
        
        header_table = Table(data, colWidths=[3*inch, 3*inch])
        header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Line items
        items = [['Description', 'Quantity', 'Unit Price', 'Amount']]
        num_items = random.randint(3, 10)
        subtotal = 0
        
        for _ in range(num_items):
            description = self.fake.catch_phrase()
            quantity = random.randint(1, 20)
            unit_price = random.uniform(50, 500)
            amount = quantity * unit_price
            subtotal += amount
            
            items.append([
                description,
                str(quantity),
                f"${unit_price:.2f}",
                f"${amount:.2f}"
            ])
        
        # Totals
        tax_rate = 0.08
        tax = subtotal * tax_rate
        total = subtotal + tax
        
        items.append(['', '', 'Subtotal:', f"${subtotal:.2f}"])
        items.append(['', '', f'Tax ({tax_rate*100}%):', f"${tax:.2f}"])
        items.append(['', '', 'TOTAL:', f"${total:.2f}"])
        
        items_table = Table(items, colWidths=[3*inch, 1*inch, 1.2*inch, 1.2*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ca02c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -4), colors.beige),
            ('GRID', (0, 0), (-1, -4), 1, colors.black),
            ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
        ]))
        
        story.append(items_table)
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("<b>Payment Terms:</b> Net 30 days", self.styles['Normal']))
        
        doc.build(story)
    
    def generate_financial_report(self, index):
        """Generate a financial report with charts."""
        filename = OUTPUT_DIR / f"financial_report_{index:03d}.pdf"
        doc = SimpleDocTemplate(str(filename), pagesize=letter)
        story = []
        
        # Header
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#d62728'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        quarter = random.choice(['Q1', 'Q2', 'Q3', 'Q4'])
        year = random.randint(2022, 2024)
        
        story.append(Paragraph(f"FINANCIAL REPORT - {quarter} {year}", title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Generate chart
        categories = ['Revenue', 'Expenses', 'Profit', 'Assets', 'Liabilities']
        values = [random.uniform(50000, 200000) for _ in categories]
        
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(categories, values, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
        ax.set_ylabel('Amount ($)')
        ax.set_title(f'Financial Overview - {quarter} {year}')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save to buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150)
        img_buffer.seek(0)
        plt.close()
        
        # Add to PDF
        img = Image(img_buffer, width=5*inch, height=3.5*inch)
        story.append(img)
        story.append(Spacer(1, 0.3*inch))
        
        # Summary
        story.append(Paragraph("<b>Executive Summary</b>", self.styles['Heading2']))
        story.append(Paragraph(self.fake.paragraph(nb_sentences=5), self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Metrics table
        metrics = [
            ['Metric', 'Value'],
            ['Total Revenue', f"${values[0]:,.2f}"],
            ['Total Expenses', f"${values[1]:,.2f}"],
            ['Net Profit', f"${values[2]:,.2f}"],
            ['Total Assets', f"${values[3]:,.2f}"],
            ['Total Liabilities', f"${values[4]:,.2f}"],
        ]
        
        metrics_table = Table(metrics, colWidths=[3*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ]))
        
        story.append(metrics_table)
        doc.build(story)

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate synthetic financial documents for FinWise-AI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/generate_synthetic_data.py --num 100
  python scripts/generate_synthetic_data.py --num 200
        """
    )
    parser.add_argument('--num', type=int, default=100, 
                       help='Number of documents to generate (default: 100)')
    args = parser.parse_args()
    
    generator = SyntheticDataGenerator(num_documents=args.num)
    generator.generate_all()
    
    print("📊 Document Distribution:")
    print("  • 60% Bank Statements (text-heavy PDFs)")
    print("  • 30% Invoices (with tables)")
    print("  • 10% Financial Reports (with embedded charts)")
    print(f"\n💡 Next Steps:")
    print(f"  1. Start backend:  python main.py")
    print(f"  2. Start frontend: streamlit run frontend/streamlit_app.py")
    print(f"  3. Upload documents via the UI or API")
    print(f"\n🎯 Ready to test FinWise-AI with realistic data!\n")

if __name__ == "__main__":
    main()