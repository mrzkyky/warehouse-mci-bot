#!/usr/bin/env python3
"""Test import to check for syntax errors"""
try:
    import bot
    print("SUCCESS: Bot module imported successfully - No syntax errors!")
except Exception as e:
    print(f"ERROR importing bot: {e}")
    import traceback
    traceback.print_exc()
