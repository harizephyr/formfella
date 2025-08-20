from openai import OpenAI
import os
from dotenv import load_dotenv
import base64
from core.config.settings import settings
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# def get_llm_response(input):
#     response = client.responses.create(
#         model="gpt-4o",
#         input=input
#     )
#     return response.output_text

# # print(get_llm_response("Write a short bedtime story about a unicorn."))


def get_llm_response(image_path, prompt):
    # Read the image file as binary
    with open(image_path, 'rb') as image_file:
        # Encode the binary image data to base64
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",   # or gpt-4o
        messages=[
            {"role": "system", "content": "You are a form processor. based on this image, ask question about it? example: text is email, then ask what this your email"},
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
            ]}
        ]
    )

    return response.choices[0].message.content