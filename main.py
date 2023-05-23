import requests
import os

url = os.environ.get('YOUTRACK_URL')
key = os.environ.get('YOUTRACK_KEY')

headers = {
    'Authorization': f'Bearer {key}',
    'Accept': 'application/json',
    'Cache-Control': 'no-cache',
    'Content-Type': 'application/json'
}


def call_api_for_issue(issue_id):

    full_url = url + f'issues/{issue_id}'

    response = requests.get(full_url,
                            headers=headers)

    if response.status_code == 200:
        retrieved_data = response.json()
        # Process data
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")


if __name__ == '__main__':
    issue = 'NC-8'
    call_api_for_issue(issue)
