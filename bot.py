import requests

def search_stackoverflow(query):
    url = "https://api.stackexchange.com/2.3/search"
    params = {
        "order": "desc",
        "sort": "relevance",
        "intitle": query,
        "site": "stackoverflow"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        if data.get("items"):
            top_question = data["items"][0]
            return f"Question: {top_question['title']}\nLink: {top_question['link']}"
        else:
            return "No relevant questions found on Stack Overflow."
    except requests.exceptions.RequestException as e:
        return f"Failed to connect to Stack Overflow API: {e}"

def main():
    print("Welcome to my Coding Assistant Bot!")
    print("Type 'exit' to quit.")

    while True:
        user_input = input(">>> ")
        if user_input.lower() == 'exit':
            break

        if user_input.startswith("search "):
            query = user_input[len("search "):]
            result = search_stackoverflow(query)
            print(result)
        else:
            print("Command not recognized. Try 'search <your query>'.")

if __name__ == "__main__":
    main()

