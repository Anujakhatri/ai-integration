# from openai import OpenAI
import google.genai as genai
from dotenv import load_dotenv
import os

#load env
load_dotenv(verbose=True)
#read api key
api_key = os.getenv("GEMINI_API_KEY")
#create  genai client

client = genai.Client(api_key=api_key)

while True:
    print("\n ---------GenAI Menu------------")
    print("1. Ask AI: ")
    print("2. Exit")

    choice = input("Enter your choice:1 or 2:")

    if choice == "1":
        # try genai by asking question
        question = input("Ask AI: ")
        # send request to genai
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=question
        )

        print("AI answer")
        print(response.text)

    elif choice == "2":
        print("Exiting...")
        break

    else:
        print("Please enter a valid choice")

