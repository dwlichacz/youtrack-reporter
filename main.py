import os
import re

import requests

url = os.environ.get('YOUTRACK_URL')
api_key = os.environ.get('YOUTRACK_KEY')

headers = {
    'Authorization': f'Bearer {api_key}',
    'Accept': 'application/json',
    'Cache-Control': 'no-cache',
    'Content-Type': 'application/json'
}


def parse_description(input_string):
    no_bold_string = input_string.replace('*', '')

    patterns = {
        "Challenge": r"Challenge:\s*(.*)",
        "Asset": r"Asset:\s*(.*)",
        "Title": r"Title:\s*(.*)",
        "Description": r"Description:\s*((?:.|\n(?!\n))+)",
        "Start Date": r"Start Date:\s*(.*)",
        "End Date": r"End Date:\s*(.*)",
    }

    extracted_values = {}

    for key, pattern in patterns.items():
        match = re.search(pattern, no_bold_string)
        if match:
            value = match.group(1).strip()
            extracted_values[key] = value

    return extracted_values['Challenge'], extracted_values['Asset'], extracted_values['Title'], \
        extracted_values['Description'], extracted_values['Start Date'], extracted_values['End Date']


def parse_comments(comment_list):
    matching_comments = [comment['text'] for comment in comment_list if "final query" in comment['text'].lower()]

    if len(matching_comments) == 1:
        # Find the content between "```sql" and "```"
        query = ""
        start = False
        for line in matching_comments[0].splitlines():
            if line.strip() == "```sql":
                start = True
            elif line.strip() == "```":
                break
            elif start:
                query += line + "\n"

        # Return the extracted query
        return query.strip()
    else:
        return None


def call_api_for_issue(issue_id):
    full_url = url + f'issues/{issue_id}'

    params = {
        'fields': 'summary,description'
    }

    response = requests.get(full_url,
                            params=params,
                            headers=headers)

    if response.status_code == 200:
        retrieved_data = response.json()
        title = retrieved_data['summary']
        description = retrieved_data['description']
        challenge, asset, inbox_title, inbox_description, start_date, end_date = parse_description(description)
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")


def call_api_for_comments(issue_id):
    full_url = url + f'issues/{issue_id}/comments'

    params = {
        'fields': 'text'
    }

    response = requests.get(full_url,
                            params=params,
                            headers=headers)

    if response.status_code == 200:
        comments = response.json()
        query = parse_comments(comments)
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")


if __name__ == '__main__':
    issue = 'NC-17'
    call_api_for_issue(issue)
    call_api_for_comments(issue)
