import os
import random
import torch
import uuid
import numpy as np

from langchain.output_parsers.base import BaseOutputParser


IMAGE_PROMPT = """
{i}th image: provide a figure named {filename}. The description is: {description}.
"""


DATAFRAME_PROMPT = """
{i}th dataframe: provide a dataframe named {filename}. The description is: {description}.
"""


IMAGE_SUFFIX = """
Please understand and answer the image based on this information. The image understanding is complete, so don't try to understand the image again.
"""

AWESOMEGPT_PREFIX = """Awesome GPT is designed to be able to assist with a wide range of text and visual related tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. Awesome GPT is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.

Awesome GPT is able to process and understand large amounts of text and images. As a language model, Awesome GPT can not directly read images, but it has a list of tools to finish different visual tasks. 

Each image will have a file name formed as "image/xxx.png"
Each dataframe will have a file name formed as "dataframe/xxx.csv"

Awesome GPT can invoke different tools to indirectly understand pictures. When talking about images, Awesome GPT is very strict to the file name and will never fabricate nonexistent files. When using tools to generate new image files, Awesome GPT is also known that the image may not be the same as the user's demand, and will use other visual question answering tools or description tools to observe the real image. Awesome GPT is able to use tools in a sequence, and is loyal to the tool observation outputs rather than faking the image content and image file name. It will remember to provide the file name from the last tool observation, if a new image is generated.

Human may provide new figures to Awesome GPT with a description. The description helps Awesome GPT to understand this image, but Awesome GPT should use tools to finish following tasks, rather than directly imagine from the description.

Overall, Awesome GPT is a powerful visual dialogue assistant tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics."""

AWESOMEGPT_SUFFIX = """TOOLS
------
Awesome GPT can ask the user to use tools to look up information that may be helpful in answering the users original question. 
You are very strict to the filename correctness and will never fake a file name if it does not exist.
You will remember to provide the image file name loyally if it's provided in the last tool observation.
The tools the human can use are:

{{tools}}

{format_instructions}

USER'S INPUT
--------------------
Here is the user's input (remember to respond with a markdown code snippet of a json blob with a single action, and NOTHING else):

{{{{input}}}}"""

ERROR_PROMPT = "An error has occurred for the following text: \n{promptedText} Please explain this error.\n {e}"


os.makedirs("image", exist_ok=True)
os.makedirs("dataframe", exist_ok=True)


def seed_everything(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    return seed


def prompts(name, description):
    def decorator(func):
        func.name = name
        func.description = description
        return func

    return decorator


def cut_dialogue_history(history_memory, keep_last_n_words=500):
    tokens = history_memory.split()
    n_tokens = len(tokens)
    print(f"hitory_memory:{history_memory}, n_tokens: {n_tokens}")
    if n_tokens < keep_last_n_words:
        return history_memory
    else:
        paragraphs = history_memory.split("\n")
        last_n_tokens = n_tokens
        while last_n_tokens >= keep_last_n_words:
            last_n_tokens = last_n_tokens - len(paragraphs[0].split(" "))
            paragraphs = paragraphs[1:]
        return "\n" + "\n".join(paragraphs)


def get_new_image_name(org_img_name, func_name="update"):
    head_tail = os.path.split(org_img_name)
    head = head_tail[0]
    tail = head_tail[1]
    name_split = tail.split(".")[0].split("_")
    this_new_uuid = str(uuid.uuid4())[0:4]
    if len(name_split) == 1:
        most_org_file_name = name_split[0]
        recent_prev_file_name = name_split[0]
        new_file_name = "{}_{}_{}_{}.png".format(
            this_new_uuid, func_name, recent_prev_file_name, most_org_file_name
        )
    else:
        assert len(name_split) == 4
        most_org_file_name = name_split[3]
        recent_prev_file_name = name_split[0]
        new_file_name = "{}_{}_{}_{}.png".format(
            this_new_uuid, func_name, recent_prev_file_name, most_org_file_name
        )
    return os.path.join(head, new_file_name)


def get_new_dataframe_name(org_img_name, func_name="update"):
    head_tail = os.path.split(org_img_name)
    head = head_tail[0]
    tail = head_tail[1]
    name_split = tail.split(".")[0].split("_")
    this_new_uuid = str(uuid.uuid4())[0:4]
    if len(name_split) == 1:
        most_org_file_name = name_split[0]
        recent_prev_file_name = name_split[0]
        new_file_name = "{}_{}_{}_{}.csv".format(
            this_new_uuid, func_name, recent_prev_file_name, most_org_file_name
        )
    else:
        assert len(name_split) == 4
        most_org_file_name = name_split[3]
        recent_prev_file_name = name_split[0]
        new_file_name = "{}_{}_{}_{}.csv".format(
            this_new_uuid, func_name, recent_prev_file_name, most_org_file_name
        )
    return os.path.join(head, new_file_name)
