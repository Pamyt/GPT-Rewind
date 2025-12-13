"""
Test script to verify the DeepSeek API endpoints
"""
import os
import requests

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

        print(f"✗ Server returned status {response.status_code}")
        return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server")
        print(f"  Make sure the server is running at {BASE_URL}")
        return False
    except requests.exceptions.RequestException as request_error:
        print(f"✗ Request error: {str(request_error)}")
        return False

def test_file_upload():
    """Test file upload endpoint"""
    print_header("Testing File Upload")

    if not os.path.exists(TEST_DATA_PATH):
        print(f"✗ Test data file not found: {TEST_DATA_PATH}")
        return None

    try:
        with open(TEST_DATA_PATH, 'rb') as file_handle:
            files = {'file': file_handle}
            response = requests.post(f"{BASE_URL}/api/upload", files=files)

        if response.status_code == 200:
            data = response.json()
            print("✓ File uploaded successfully")
            print(f"  Filepath: {data.get('filepath')}")
            print(f"  Filename: {data.get('filename')}")
            return data.get('filepath')

        print(f"✗ Upload failed with status {response.status_code}")
        print(f"  Response: {response.text}")
        return None
    except (IOError, OSError) as file_error:
        print(f"✗ File error during upload: {str(file_error)}")
        return None
    except requests.exceptions.RequestException as request_error:
        print(f"✗ Request error during upload: {str(request_error)}")
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
            _print_analysis_summary(data)
            return True

        print(f"✗ Analysis failed with status {response.status_code}")
        print(f"  Response: {response.text}")
        return False
    except requests.exceptions.Timeout:
        print("✗ Analysis timed out (data may be too large)")
        return False
    except requests.exceptions.RequestException as request_error:
        print(f"✗ Request error during analysis: {str(request_error)}")
        return False

def _print_analysis_summary(data):
    """Print summary of analysis results to reduce branching in main function"""
    result_fields = [
        ('session_count', lambda x: x['session_count'].get('session_count', 'N/A'),\
            'Session count'),
        ('most_used_models', lambda x: len(x['most_used_models']), 'Most used models', 'model(s)'),
        ('total_characters', lambda x: sum(int(item.get('counts', 0)) \
            for item in x.get('total_characters', [])), 'Total characters'),
        ('refuse_counts', lambda x: x['refuse_counts'], 'Refuse counts'),
        ('emoji_counts', lambda x: len(x['emoji_counts']), 'Emoji counts', 'unique emoji(s)'),
        ('chat_days', lambda x: len(x['chat_days']), 'Chat days', 'day(s)'),
        ('most_used_language', lambda x: len(x['most_used_language']),\
            'Languages detected', 'language(s)'),
        ('polite_extent', lambda x: len(x['polite_extent']), 'Polite words', 'type(s)')
    ]

    for field_info in result_fields:
        field_name = field_info[0]
        if field_name in data:
            value = field_info[1](data)
            label = field_info[2]
            suffix = field_info[3] if len(field_info) > 3 else ''
            print(f"  • {label}: {value} {suffix}")

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
