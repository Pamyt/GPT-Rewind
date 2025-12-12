"""
Test script to verify the DeepSeek API endpoints
"""

import json
import requests
import time
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:5000"
TEST_DATA_PATH = "data/example.json"

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def test_server_connection():
    """Test if server is running"""
    print_header("Testing Server Connection")
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("✓ Server is running")
            return True
        else:
            print(f"✗ Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server")
        print(f"  Make sure the server is running at {BASE_URL}")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_file_upload():
    """Test file upload endpoint"""
    print_header("Testing File Upload")
    
    if not os.path.exists(TEST_DATA_PATH):
        print(f"✗ Test data file not found: {TEST_DATA_PATH}")
        return None
    
    try:
        with open(TEST_DATA_PATH, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/api/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("✓ File uploaded successfully")
            print(f"  Filepath: {data.get('filepath')}")
            print(f"  Filename: {data.get('filename')}")
            return data.get('filepath')
        else:
            print(f"✗ Upload failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error during upload: {str(e)}")
        return None

def test_data_analysis(filepath):
    """Test data analysis endpoint"""
    print_header("Testing Data Analysis")
    
    if not filepath:
        print("✗ No filepath provided")
        return False
    
    try:
        print("Analyzing data (this may take a moment)...")
        response = requests.post(
            f"{BASE_URL}/api/analyze",
            json={"filepath": filepath},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Data analysis successful")
            
            # Print summary of results
            print("\nAnalysis Results Summary:")
            
            if 'session_count' in data:
                print(f"  • Session count: {data['session_count'].get('session_count', 'N/A')}")
            
            if 'most_used_models' in data:
                print(f"  • Most used models: {len(data['most_used_models'])} model(s)")
            
            if 'total_characters' in data:
                total = sum(int(item.get('counts', 0)) for item in data.get('total_characters', []))
                print(f"  • Total characters: {total}")
            
            if 'refuse_counts' in data:
                print(f"  • Refuse counts: {data['refuse_counts']}")
            
            if 'emoji_counts' in data:
                print(f"  • Emoji counts: {len(data['emoji_counts'])} unique emoji(s)")
            
            if 'chat_days' in data:
                print(f"  • Chat days: {len(data['chat_days'])} day(s)")
            
            if 'most_used_language' in data:
                print(f"  • Languages detected: {len(data['most_used_language'])} language(s)")
            
            if 'polite_extent' in data:
                print(f"  • Polite words: {len(data['polite_extent'])} type(s)")
            
            return True
        else:
            print(f"✗ Analysis failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print("✗ Analysis timed out (data may be too large)")
        return False
    except Exception as e:
        print(f"✗ Error during analysis: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "DeepSeek API Test Suite" + " "*25 + "║")
    print("╚" + "="*58 + "╝")
    
    # Test 1: Server connection
    if not test_server_connection():
        print("\n✗ Tests aborted: Server is not running")
        return
    
    # Test 2: File upload
    filepath = test_file_upload()
    if not filepath:
        print("\n✗ Tests aborted: File upload failed")
        return
    
    # Test 3: Data analysis
    if test_data_analysis(filepath):
        print_header("All Tests Passed!")
        print("✓ Server is running correctly")
        print("✓ File upload is working")
        print("✓ Data analysis API is working")
        print("\nYou can now use the web interface at http://localhost:5000")
    else:
        print_header("Tests Failed!")
        print("✗ Some tests failed")
        print("\nPlease check the error messages above")

if __name__ == "__main__":
    print("Note: Make sure the server is running before running this test")
    print("Start the server with: ./start_frontend.sh (or start_frontend.bat on Windows)")
    
    input("\nPress Enter to start tests...")
    main()
