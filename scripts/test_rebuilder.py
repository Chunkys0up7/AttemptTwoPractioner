import os
import subprocess
import shutil
import time
from pathlib import Path

def run_test(test_file):
    """Run a single test file and return (success, output)"""
    try:
        result = subprocess.run(
            ['pytest', test_file, '-v', '--tb=short'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(test_file)
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def rebuild_test(test_file, original_content):
    """Delete and recreate a test file with fresh content"""
    print(f"\nRebuilding test: {test_file}")
    
    # Delete the original
    os.remove(test_file)
    
    # Create a fresh copy
    with open(test_file, 'w') as f:
        f.write(original_content)
    
    print("Test rebuilt successfully")

def main():
    # Get all test files
    test_files = list(Path('tests').rglob('test_*.py'))
    
    # Store original content of each test file
    test_contents = {}
    for test_file in test_files:
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                test_contents[str(test_file)] = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(test_file, 'r', encoding='latin1') as f:
                test_contents[str(test_file)] = f.read()
    
    # Track failures
    failed_tests = {}
    
    for test_file in test_files:
        test_path = str(test_file)
        print(f"\nRunning test: {test_path}")
        
        # Try running the test up to 3 times
        for attempt in range(3):
            success, output = run_test(test_path)
            print(f"Attempt {attempt + 1}:")
            print(output)
            
            if success:
                print(f"Test passed after {attempt + 1} attempts")
                break
            else:
                print(f"Test failed on attempt {attempt + 1}")
                
                # If this is the third attempt, rebuild the test
                if attempt == 2:
                    print("Final attempt failed - rebuilding test...")
                    rebuild_test(test_path, test_contents[test_path])
                    
                    # Run the rebuilt test once more
                    success, output = run_test(test_path)
                    print("Final attempt after rebuild:")
                    print(output)
                    
                    if not success:
                        print(f"Test still failing after rebuild: {test_path}")
                        failed_tests[test_path] = output
                        break
        
        # Small delay between tests to avoid overwhelming the system
        time.sleep(1)
    
    # Print summary of failed tests
    if failed_tests:
        print("\n=== TESTS THAT FAILED AFTER REBUILD ===")
        for test, output in failed_tests.items():
            print(f"\nFailed test: {test}")
            print("Failure output:")
            print(output)
    else:
        print("\nAll tests passed after rebuild if needed!")

if __name__ == "__main__":
    main()
