#!/usr/bin/env python3
"""Decompile Python 3.13 .pyc files using bytecode inspection"""

import sys
import marshal
import dis
from pathlib import Path

def decompile_pyc_simple(pyc_path):
    """Simple decompiler using dis module"""
    try:
        with open(pyc_path, 'rb') as f:
            # Skip Python 3.13 header (16 bytes)
            header = f.read(16)
            code = marshal.load(f)
        
        print(f"\n{'='*80}")
        print(f"Bytecode from: {pyc_path}")
        print('='*80)
        dis.dis(code)
        return code
    except Exception as e:
        print(f"Error decompiling {pyc_path}: {e}")
        return None

def extract_function_names(code):
    """Extract function and class names from code object"""
    names = set()
    consts = code.co_consts
    
    for const in consts:
        if hasattr(const, 'co_name'):
            names.add(const.co_name)
    
    names.add(code.co_name)
    return names

if __name__ == "__main__":
    services = [
        "nin_engine",
        "quantum_engine", 
        "preprocessing",
        "feature_extraction",
        "rule_engine",
        "explainability"
    ]
    
    for service in services:
        pyc_path = f"backend/app/services/__pycache__/{service}.cpython-313.pyc"
        if Path(pyc_path).exists():
            print(f"\n\n>>> Decompiling {service}...")
            try:
                code = decompile_pyc_simple(pyc_path)
                if code:
                    names = extract_function_names(code)
                    print(f"\nFunctions/Classes in {service}:")
                    for name in sorted(names):
                        if not name.startswith('_'):
                            print(f"  - {name}")
            except Exception as e:
                print(f"Failed: {e}")
        else:
            print(f"Not found: {pyc_path}")
