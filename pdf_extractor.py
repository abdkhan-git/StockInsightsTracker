import requests
import json
import os

def extract_pdf_content(pdf_url, api_key):
    """
    Extracts content from a PDF using the OpenRouter API.

    Args:
        pdf_url (str): The URL of the PDF file.
        api_key (str): The API key for OpenRouter.

    Returns:
        str: The extracted content from the PDF, or an error message if extraction fails.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Please extract all the stock trades in this PDF and put them in a table. Use MarkDown formatting. Do not add additional comments or notes. Do not add markdown begin/end tags. Just the table.\n"
                        "Format: Owner | Asset | Type | Transaction Date | Notification Date | Amount"
                    )
                },
                {
                    "type": "file",
                    "file": {
                        "filename": "ptr.pdf",
                        "file_data": pdf_url
                    }
                }
            ]
        }
    ]

    plugins = [
        {
            "id": "file-parser",
            "pdf": {
                "engine": "pdf-text"  # Use free, fast text parser
            }
        }
    ]

    payload = {
        "model": os.getenv("AI_MODEL", "mistralai/mistral-small-3.2-24b-instruct:free"),
        "messages": messages,
        "plugins": plugins
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to fetch PDF or API request: {e}"
    except (KeyError, ValueError) as e:
        return f"Error: Failed to parse API response: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"


if __name__ == '__main__':
    # Example usage:
    pdf_url = "https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/2025/20030630.pdf"  # Replace with a valid PDF URL
    api_key = "sk-or-v1-"  # Replace with your actual API key
    extracted_content = extract_pdf_content(pdf_url, api_key)
    print(extracted_content)
