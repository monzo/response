import requests


def delete_original_message(response_url):
    requests.post(response_url, json={"delete_original": "true"})


def replace_original_message(response_url, text):
    requests.post(response_url, json={"replace_original": "true", "text": text})
