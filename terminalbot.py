import requests
import json
import os
import io
import re
import base64
import random
from pathlib import Path
from PIL import Image, PngImagePlugin
import urllib.request

ENDPOINT = "http://127.0.0.1:5000"
SD_URL = "http://127.0.0.1:7860"
viu_url = "https://github.com/atanunq/viu/releases/download/v1.4.0/viu"

#Get Viu Check if the file exists
if not os.path.isfile("viu"):
    # Download the file
    urllib.request.urlretrieve(viu_url, "viu")
    # Give execute permission
    os.chmod("viu", 0o755)
else:
    # Check if the file has execute permission
    if not os.access("viu", os.X_OK):
        # Give execute permission
        os.chmod("viu", 0o755)


def split_text(text):
    parts = re.split(r'\n[a-zA-Z]', text)
    return parts

username =  "User"
botname = "Assistant"

def get_prompt(conversation_history, username, text): # For KoboldAI Generation

    return {
        "prompt": conversation_history + f"{username}: {text}\n{botname}:",
        "use_story": False,
        "use_memory": True,
        "use_authors_note": False,
        "use_world_info": False,
        "max_context_length": 2048,
        "max_length": 120,
        "rep_pen": 1.0,
        "rep_pen_range": 2048,
        "rep_pen_slope": 0.7,
        "temperature": 0.8,
        "tfs": 0.97,
        "top_a": 0.8,
        "top_k": 0,
        "top_p": 0.5,
        "typical": 0.19,
        "sampler_order": [5, 4, 3, 1, 2, 0, 6],
        "singleline": False, #usually True
        #"sampler_seed": 69420,   #set the seed
        #"sampler_full_determinism": True,     #set it so the seed determines generation content
        "frmttriminc": False,
        "frmtrmblln": False
    }

print("Starting ")
num_lines_to_keep = 20
os.system(f"clear")
global conversation_history
with open(f'conv_history_{botname}_terminal.txt', 'a+') as file:
    file.seek(0)
    # Read the contents of the file
    chathistory = file.read()
    print(chathistory)
conversation_history = f"{chathistory}"


def draw(user_message): # For Stable Diffusion
    payload = {
        "prompt": (f"{user_message}"),
        "steps": 30,
        "batch_size": 1,
        "n_iter": 1,
        "cfg scale": 8,
        "width": 512, # Feel free to change these if your GPU is not limited
        "height": 512, # Feel free to change these if your GPU is not limited
       # "enable_hr': false,
       # "denoising_strength": 0,
       # "firstphase_width": 0,
       # "firstphase_height": 0,
       # "styles": [
       #     "string"
       # ],
        "seed": -1,
        "subseed": -1,
        "subseed_strength": 0,
        "seed_resize_from_h": -1,
        "seed_resize_from_w": -1,
        "restore_faces": True,
        "tiling": False,
        "negative prompt": "Out of frame, out of focus, morphed",
        "s_churn": 0,
        "s_tmax": 0,
        "s_tmin": 0,
        "s_noise": 1,
        "sampler_index": "Euler a"
}

    r = requests.post(url=f'{SD_URL}/sdapi/v1/txt2img', json=payload).json()
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    chars1 = "1234564890"
    gen1 = random.choice(chars)
    gen2 = random.choice(chars)
    gen3 = random.choice(chars1)
    gen4 = random.choice(chars)
    gen5 = random.choice(chars)
    gen6 = random.choice(chars)
    gen7 = random.choice(chars1)
    gen8 = random.choice(chars)
    gen9 = random.choice(chars)
    gen10 = random.choice(chars1)
    word = f"terminal-bot{gen1}{gen2}{gen3}{gen4}{gen5}{gen6}{gen7}{gen8}{gen9}{gen10}"

    for i in r['images']:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))
        png_payload = {"image": "data:image/png;base64," + i}
        response2 = requests.post(url=f'{SD_URL}/sdapi/v1/png-info',
                                  json=png_payload)

        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        image.save(f'{word}.png', pnginfo=pnginfo)
        os.system(f"./viu {word}.png --width 48"),
        os.remove(f"{word}.png")
        
# Define the function to handle incoming messages
def handle_message(user_message):
    global conversation_history
    # Generate a prompt using the conversation history and user message
    prompt = get_prompt(conversation_history, username, user_message)
    # Send the prompt to KoboldAI and get the response
    response = requests.post(f"{ENDPOINT}/api/v1/generate", json=prompt)
    # Parse the response and get the generated text
    if response.status_code == 200:
        results = response.json()['results']
        text = results[0]['text']
        response_text = split_text(text)[0]
        # Update the conversation history with the user message and bot response
        response_text = response_text.replace("  ", " ")        
        conversation_history += f"{username}: {user_message}\n{botname}: {response_text}\n"
        # Append conversation to text file
        with open(f'conv_history_{botname}_terminal.txt', "a") as f:
            f.write(f"{username}: {user_message}\n{botname}: {response_text}\n")
        # Send the response back to the user
        response_text = response_text.replace("\n", "")
        print(f"{botname}: {response_text}")

# Start the conversation
while True:
    # Get user input from the console
    user_message = input(f"{username}: ")
    # Handle the user's input and get the bot's response
    if user_message.startswith('/draw '): 
        message = user_message[6:]  # Extract the message part of the command
        draw(message)  # Pass the message to the draw() function
    else:
        handle_message(user_message)


