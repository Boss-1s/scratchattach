import requests
from rich.pretty import pprint

def remove_pair_and_siblings(data, target_key, target_value):
    """
    Recursively removes any dictionary (and its sibling items)
    containing the target key-value pair.
    """
    if isinstance(data, dict):
        # If this dictionary contains the target pair, return None to delete it
        if data.get(target_key) == target_value:
            return None
        
        # Otherwise, process its contents recursively
        cleaned_dict = {}
        for key, value in data.items():
            cleaned_value = remove_pair_and_siblings(value, target_key, target_value)
            if cleaned_value is not None:
                cleaned_dict[key] = cleaned_value
        return cleaned_dict

    elif isinstance(data, list):
        # Process list items and filter out anything that returned None
        cleaned_list = []
        for item in data:
            cleaned_item = remove_pair_and_siblings(item, target_key, target_value)
            if cleaned_item is not None:
                cleaned_list.append(cleaned_item)
        return cleaned_list

    # Return primitive data types as-is
    return data


package_name = input("Enter the package name: ")
url = f"https://pypistats.org/api/packages/{package_name}/overall"

response = requests.get(url)
if response.status_code == 200:
    stats = response.json()
    stats = remove_pair_and_siblings(stats, "category", "with_mirrors")
    pprint(stats, expand_all=True, indent_guides=True)
else:
    print(f"Error fetching data: {response.status_code}")
