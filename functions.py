from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import json
from json import JSONDecodeError
import requests
from io import BytesIO

def summarize_text(user_input):

    llm = ChatOpenAI(model="gpt-4o", temperature=1)
    # Create a prompt template
    template = """
    You are an expert summarizer. Summarize the following text in 1-2 sentences:
    Text: {user_input}
    """
    prompt = PromptTemplate(
        input_variables=["text"], 
        template=template)
    
    chain = prompt | llm

    summary = chain.invoke({"user_input": user_input}).content

    return summary

def draft_email(user_input):

    llm = ChatOpenAI(model="gpt-4o", temperature=1)

    # Create a prompt template
    prompt_template = """
    You are a helpful assistant tasked with drafting a concise and professional
    email reply based on the provided email: {user_input}.
    Your objective is to create an accurate and polished response efficiently.
    Ensure the tone remains professional and conclude the email with the signature, 'MengC.
    """

    # Create the prompt from the prompt template
    prompt = PromptTemplate(
        input_variables=["user_input"],
        template = prompt_template,
    )

    chain = prompt | llm

    response = chain.invoke({"user_input": user_input}).content

    return response

# This one illustrates formatting the response
def sentiment(user_input):
    # temperature=0 and top_p=1 to eliminate randomness
    llm = ChatOpenAI(model="gpt-4o", temperature=0, top_p=1)

    # Create a prompt template
    prompt_template = """
    You are a helpful assistant tasked with analyzing the sentiment of the following text: {user_input}.
    Your objective is to state the sentiment in plain words and then give a rating from 1 to 10, with 1 
    being totally bad to 10 being totally good. Additionally, you will give an assessment on the urgency
    of the text in question in the same fashion, with 10 being ASAP and 1 being whenever. Output only the 
    following JSON object. Do not wrap it in code fences or add any extra text:
    {{
    "sentiment": {{
        "label": "<positive|negative|neutral>",
        "analysis": "<It is … because …>",
        "score": <integer 1–10>
    }},
    "urgency": {{
        "label": "<ASAP|soon|whenever>",
        "analysis": "<It is … because …>",
        "score": <integer 1–10>
    }}
    }}
    """

    # Create the prompt from the prompt template
    prompt = PromptTemplate(
        input_variables=["user_input"],
        template = prompt_template,
    )

    raw = (prompt | llm).invoke({"user_input": user_input}).content
    # Strip any extra whitespaces
    response = raw.strip()

    try:
        # Load the JSON-like string as dictionaries
        data = json.loads(raw)
        s, u = data["sentiment"], data["urgency"]
    # Handle JSON errors in case chatGPT makes a mistake
    except JSONDecodeError as e:
        print(f"JSON error: {e}")
        print(f"{repr(response)}")
        return "Sorry, there was an error. Please try again."
    
    try:
        # Reformat it back into a string
        response = (
            f"Sentiment: *{s['label']}*\n"
            f"Analysis: *{s['analysis']}*\n"
            f"Score: *{s['score']}*\n"
            f"----------\n"
            f"Urgency: *{u['label']}*\n"
            f"Analysis: *{u['analysis']}*\n"
            f"Score: *{u['score']}*"
            )
    # Handle key errors in case chatGPT makes a mistake
    except KeyError as e:
        print(f"Key error: {e}")
        print(f"{repr(response)}")
        return "Sorry, there was an error. Please try again."
    
    return response

# I know this one is very silly
def therapy(user_input):

    llm = ChatOpenAI(model="gpt-4o", temperature=1)

    # Create a prompt template
    prompt_template = """
    You are a sketchy corporate therapist tasked with getting the user back to work.  The user sent 
    you this message: {user_input}.  Your objective is to increase their productivity, but don't tell 
    them that! Remember, the company comes first, their happiness comes second.  Consider adding subtle 
    clues that your intentions are not pure.  Don't prompt for a response, simply give them a solution.
    """

    # Create the prompt from the prompt template
    prompt = PromptTemplate(
        input_variables=["user_input"],
        template = prompt_template,
    )

    chain = prompt | llm

    response = chain.invoke({"user_input": user_input}).content

    return response

def generate_image(user_input, client):
    """
    Generate an image via OpenAI’s Images API (v1.x SDK),
    download the first result, and return it as a PNG BytesIO.
    """
    # Ask DALL·E
    resp = client.images.generate(
        model="dall-e-3",
        prompt=user_input,
        n=1,
        size="1024x1024",
        response_format="url"  # returns URLs
    )
    url = resp.data[0].url  # the generated image URL

    # Download the PNG bytes
    img_bytes = requests.get(url).content

    # Wrap in BytesIO and return
    buf = BytesIO(img_bytes)
    buf.name = "generated.png"
    buf.seek(0)
    return buf

