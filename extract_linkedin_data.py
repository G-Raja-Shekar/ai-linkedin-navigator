import json


def extract_linkedin_profile(data):
    """
    Extract specific fields from a LinkedIn profile object.
    
    Args:
        data: A dictionary representing a LinkedIn profile
        
    Returns:
        A dictionary with extracted fields
    """
    extracted = {
        'firstName': data.get('firstName', ''),
        'lastName': data.get('lastName', ''),
        'fullName': f"{data.get('firstName', '')} {data.get('lastName', '')}".strip(),
        'degree': data.get('degree', ''),
        'companyName': '',
        'title': '',
        'industry': '',
        'location': ''
    }
    
    # Extract data from currentPositions if available
    current_positions = data.get('currentPositions', [])
    if current_positions and len(current_positions) > 0:
        first_position = current_positions[0]
        
        # Extract company name and title
        extracted['companyName'] = first_position.get('companyName', '')
        extracted['title'] = first_position.get('title', '')
        
        # Extract industry and location from companyUrnResolutionResult
        company_urn = first_position.get('companyUrnResolutionResult', {})
        extracted['industry'] = company_urn.get('industry', '')
        extracted['location'] = company_urn.get('location', '')
    
    return extracted


def process_linkedin_profiles(profiles_array):
    """
    Process an array of LinkedIn profile objects and extract required fields.
    
    Args:
        profiles_array: A list of LinkedIn profile dictionaries
        
    Returns:
        A list of dictionaries with extracted fields
    """
    extracted_profiles = []
    
    for profile in profiles_array:
        extracted_data = extract_linkedin_profile(profile)
        extracted_profiles.append(extracted_data)
    
    return extracted_profiles


def save_to_json(data, filename='extracted_profiles.json'):
    """Save the extracted data to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Data saved to {filename}")


def save_to_csv(data, filename='extracted_profiles.csv'):
    """Save the extracted data to a CSV file."""
    import csv
    
    if not data:
        print("No data to save")
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        # Get fieldnames from the first dictionary
        fieldnames = data[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(data)
    
    print(f"Data saved to {filename}")


# Example usage
if __name__ == "__main__":
    import re
    import subprocess
    
    # Read the linkedin.js file
    with open('linkedin.js', 'r', encoding='utf-8') as f:
        js_content = f.read()
    
    # Use Node.js to convert JS to JSON
    # Create a temporary script to extract the data
    temp_script = """
    const data = require('./linkedin.js');
    console.log(JSON.stringify(data));
    """
    
    # Try alternative approach: extract and convert using regex
    match = re.search(r'const data = (\[.*\])', js_content, re.DOTALL)
    if match:
        js_array = match.group(1)
        
        # Write to a temporary file and use Node.js to parse it
        with open('temp_data.js', 'w', encoding='utf-8') as f:
            f.write(f"module.exports = {js_array};")
        
        try:
            # Use Node.js to convert to JSON
            result = subprocess.run(
                ['node', '-e', 'console.log(JSON.stringify(require("./temp_data.js")))'],
                capture_output=True,
                text=True,
                check=True
            )
            linkedin_profiles = json.loads(result.stdout)
            print(f"Loaded {len(linkedin_profiles)} profiles from linkedin.js")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Node.js not available. Using alternative parsing method...")
            # Fallback: try to fix common JS to JSON issues
            import demjson3
            try:
                linkedin_profiles = demjson3.decode(js_array)
                print(f"Loaded {len(linkedin_profiles)} profiles using demjson3")
            except:
                print("Please install demjson3: pip install demjson3")
                linkedin_profiles = []
        finally:
            # Clean up temp file
            import os
            if os.path.exists('temp_data.js'):
                os.remove('temp_data.js')
    else:
        print("Could not extract data array from linkedin.js")
        linkedin_profiles = []
    
    if linkedin_profiles:
        # Process the profiles
        extracted_data = process_linkedin_profiles(linkedin_profiles)
        
        # Display summary
        print(f"\nProcessed {len(extracted_data)} profiles")
        print(f"\nFirst profile sample:")
        if extracted_data:
            print(json.dumps(extracted_data[0], indent=2))
        
        # Save to files
        save_to_json(extracted_data)
        save_to_csv(extracted_data)
