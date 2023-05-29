import os
import re

import requests

url = os.environ.get('YOUTRACK_URL')
api_key = os.environ.get('YOUTRACK_KEY')
template_file = os.environ.get('YOUTRACK_TEMPLATE')

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
        "Gift ID": r"Gift ID:\s*(.*)",
        "Title": r"Title:\s*(.*)",
        "Description": r"Description:\s*((?:.|\n(?!\n))+)",
        "Start Time": r"Start Time:\s*(.*)",
        "End Time": r"End Time:\s*(.*)",
    }

    extracted_values = {}

    for key, pattern in patterns.items():
        match = re.search(pattern, no_bold_string)
        if match:
            value = match.group(1).strip()
            extracted_values[key] = value

    # Account for case when there is no Gift ID
    extracted_values.setdefault("Gift ID", None)

    return extracted_values['Challenge'], extracted_values['Asset'], extracted_values['Gift ID'], \
        extracted_values['Title'], extracted_values['Description'], extracted_values['Start Time'], \
        extracted_values['End Time']


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

        challenge, asset, gift_id, inbox_title, inbox_description, start_time, end_time = parse_description(description)

        return title, challenge, asset, gift_id, inbox_title, inbox_description, start_time, end_time
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
        return query
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")


def fill_in_template(issue_id):
    with open(template_file, 'r') as file:
        template_string = file.read()

    title, challenge, asset, gift_id, inbox_title, \
        inbox_description, start_time, end_time = call_api_for_issue(issue_id)
    query = call_api_for_comments(issue_id)

    if not gift_id:
        output = 'uid, prize'
        promo_type = 'coin'
        gift_id = 'null'
        amount = 'prize'
    else:
        output = 'uid'
        promo_type = 'card'
        amount = 'null'

    segment = 'placeholder_segment'

    completed_template = template_string.format(title=title, challenge=challenge, output=output, start_time=start_time,
                                                end_time=end_time, query=query, segment=segment, promo_type=promo_type,
                                                gift_id=gift_id, amount=amount, inbox_title=inbox_title,
                                                inbox_description=inbox_description, view=asset)

    return completed_template, title


def parse_file_title(input_string):
    # Remove non-alphanumeric characters (excluding spaces)
    alphanumeric_string = re.sub(r'[^a-zA-Z0-9\s]', '', input_string)

    # Replace consecutive spaces with a single underscore
    underscored_string = re.sub(r'\s+', '_', alphanumeric_string)

    lowercase_string = underscored_string.lower()

    return lowercase_string


def write_final_file(issue_id):
    file_text, title = fill_in_template(issue_id)
    filename = parse_file_title(title)

    with open(filename + '.md', "w") as file:
        file.write(file_text)


if __name__ == '__main__':
    issue = 'NC-17'
    write_final_file(issue)
