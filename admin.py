#!/usr/bin/env python3
"""
Admin CLI tools for warehouse management
"""

import sys
from datetime import datetime, timedelta
from models import init_db, get_session, Transaction, User, TransactionType
from report_generator import ReportGenerator
import argparse

def show_stats():
    """Show database statistics"""
    session = get_session()
    
    total_transactions = session.query(Transaction).count()
    
    by_type = session.query(
        Transaction.type, 
        session.query(func.count(Transaction.id))
    ).group_by(Transaction.type).all()
    
    today = datetime.now().date()
    today_count = session.query(Transaction).filter(
        func.date(Transaction.created_at) == today
    ).count()
    
    print(f"📊 Database Statistics")
    print(f"======================")
    print(f"Total Transactions: {total_transactions}")
    print(f"Today: {today_count}")
    print(f"\nBy Type:")
    for t, c in by_type:
        print(f"  {t.value}: {c}")
    
    session.close()

def list_recent(limit=10):
    """List recent transactions"""
    session = get_session()
    
    transactions = session.query(Transaction).order_by(
        Transaction.created_at.desc()
    ).limit(limit).all()
    
    print(f"📋 Recent {limit} Transactions")
    print(f"==============================")
    
    for t in transactions:
        print(f"\n#{t.id} [{t.type.value.upper()}] {t.created_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"  Item: {t.item_name}")
        print(f"  Qty: {t.quantity} {t.unit}")
        if t.brand:
            print(f"  Brand: {t.brand}")
        if t.serial_numbers:
            print(f"  SN: {t.serial_numbers}")
    
    session.close()

def generate_report(date_str=None, format='text'):
    """Generate report for date"""
    session = get_session()
    
    if date_str:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    else:
        date = datetime.now()
    
    gen = ReportGenerator(session)
    
    if format == 'text':
        report = gen.generate_text_report(date)
        print(report)
    elif format == 'excel':
        path = gen.generate_excel_report(date)
        print(f"✅ Excel saved to: {path}")
    elif format == 'so':
        report = gen.generate_so_report(date)
        print(report)
    
    session.close()

def delete_transaction(transaction_id):
    """Delete a transaction"""
    session = get_session()
    
    t = session.query(Transaction).get(transaction_id)
    if t:
        session.delete(t)
        session.commit()
        print(f"✅ Transaction #{transaction_id} deleted")
    else:
        print(f"❌ Transaction #{transaction_id} not found")
    
    session.close()

def export_all(output_file='export.csv'):
    """Export all data to CSV"""
    import csv
    
    session = get_session()
    transactions = session.query(Transaction).all()
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'ID', 'Date', 'Type', 'Category', 'Item Name', 'Brand',
            'Specs', 'Quantity', 'Unit', 'Serial Numbers', 'Purpose',
            'Destination', 'Source', 'Notes'
        ])
        
        for t in transactions:
            writer.writerow([
                t.id, t.created_at, t.type.value, 
                t.category.value if t.category else '',
                t.item_name, t.brand, t.specs,
                t.quantity, t.unit, t.serial_numbers,
                t.purpose, t.destination, t.source, t.notes
            ])
    
    print(f"✅ Exported {len(transactions)} records to {output_file}")
    session.close()

def main():
    parser = argparse.ArgumentParser(description='Warehouse Admin Tools')
    subparsers = parser.add_subparsers(dest='command')
    
    # Stats
    subparsers.add_parser('stats', help='Show database statistics')
    
    # List
    list_parser = subparsers.add_parser('list', help='List recent transactions')
    list_parser.add_argument('-n', '--limit', type=int, default=10)
    
    # Report
    report_parser = subparsers.add_parser('report', help='Generate report')
    report_parser.add_argument('-d', '--date', help='Date (YYYY-MM-DD)')
    report_parser.add_argument('-f', '--format', choices=['text', 'excel', 'so'], 
                               default='text')
    
    # Delete
    delete_parser = subparsers.add_parser('delete', help='Delete transaction')
    delete_parser.add_argument('id', type=int, help='Transaction ID')
    
    # Export
    export_parser = subparsers.add_parser('export', help='Export to CSV')
    export_parser.add_argument('-o', '--output', default='export.csv')
    
    args = parser.parse_args()
    
    # Init DB
    init_db()
    
    if args.command == 'stats':
        show_stats()
    elif args.command == 'list':
        list_recent(args.limit)
    elif args.command == 'report':
        generate_report(args.date, args.format)
    elif args.command == 'delete':
        delete_transaction(args.id)
    elif args.command == 'export':
        export_all(args.output)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
