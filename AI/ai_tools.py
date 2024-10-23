import os

import vertexai
from dotenv import load_dotenv
from vertexai.generative_models import SafetySetting
from vertexai.preview.prompts import Prompt

load_dotenv()


def generate_comment_reply(comment: str, post: str):
    vertexai.init(project=os.getenv("GCLOUD_PROJECT_ID"))
    prompt = Prompt(
        prompt_data="Reply to this comment: {comment}\n\nPost: {post}",
        model_name="gemini-1.5-flash-002",
        generation_config=generation_config,
        safety_settings=safety_settings,
    )

    response = prompt.generate_content(
        contents=prompt.assemble_contents(comment=comment, post=post),
        stream=False
    )
    print(response.text)
    return response.text


generation_config = {
    "max_output_tokens": 256,
    "temperature": 0.7,
    "top_p": 0.9,
}

safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
]
