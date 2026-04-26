#!/usr/bin/env python3
"""Test API pipeline - health, upload, analyze endpoints"""

import requests
import os

API_BASE = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("\n=== Testing Health Check ===")
    try:
        response = requests.get(f"{API_BASE}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Health check PASSED")
            return True
        else:
            print("❌ Health check FAILED")
            return False
    except Exception as e:
        print(f"❌ Health check ERROR: {e}")
        return False

def test_upload():
    """Test upload endpoint"""
    print("\n=== Testing Upload Endpoint ===")
    
    # Create a test CSV file
    test_csv = "time,II\n0,0.5\n0.1,0.6\n0.2,0.7\n"
    test_file = "test_upload.csv"
    
    try:
        with open(test_file, 'w') as f:
            f.write(test_csv)
        
        with open(test_file, 'rb') as f:
            response = requests.post(f"{API_BASE}/api/ecg/upload", files={'file': f})
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Upload endpoint PASSED")
            return True
        else:
            print("❌ Upload endpoint FAILED")
            return False
    except Exception as e:
        print(f"❌ Upload endpoint ERROR: {e}")
        return False
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

def test_analyze():
    """Test analyze endpoint"""
    print("\n=== Testing Analyze Endpoint ===")
    
    # Create a test CSV file
    test_csv = "time,II\n0,0.5\n0.1,0.6\n0.2,0.7\n"
    test_file = "test_analyze.csv"
    
    try:
        with open(test_file, 'w') as f:
            f.write(test_csv)
        
        with open(test_file, 'rb') as f:
            response = requests.post(f"{API_BASE}/api/analysis/analyze", files={'file': f})
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Analyze endpoint PASSED")
            return True
        else:
            print("❌ Analyze endpoint FAILED")
            return False
    except Exception as e:
        print(f"❌ Analyze endpoint ERROR: {e}")
        return False
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

def main():
    """Run API pipeline tests"""
    print("="*60)
    print("API PIPELINE TEST")
    print("="*60)
    print(f"API Base: {API_BASE}")
    
    results = {
        "health": test_health(),
        "upload": test_upload(),
        "analyze": test_analyze()
    }
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.upper()}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED - API Contract Valid")
        return True
    else:
        print("❌ SOME TESTS FAILED - API Contract Invalid")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
