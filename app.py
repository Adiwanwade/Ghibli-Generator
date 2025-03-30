import torch
from diffusers import StableDiffusionPipeline
from PIL import Image, ImageEnhance
import numpy as np
import os
from flask import Flask, request, render_template, send_file

# Step 1: Load the Stable Diffusion model
model_id = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")

# Step 2: Define a function to generate an image with a Ghibli-style prompt
def generate_ghibli_image(prompt, output_path="ghibli_image.png"):
    # Add Ghibli-style keywords to the prompt
    ghibli_prompt = f"{prompt}, Studio Ghibli style, soft colors, detailed background, hand-drawn aesthetic, warm lighting"
    
    # Generate the image
    image = pipe(ghibli_prompt, num_inference_steps=50, guidance_scale=7.5).images[0]
    
    # Step 3: Post-process the image to enhance the Ghibli style
    image = post_process_ghibli_style(image)
    
    # Save the image
    image.save(output_path)
    return image

# Step 4: Post-process the image to make it more Ghibli-like
def post_process_ghibli_style(image):
    # Convert to PIL Image if it's not already
    if not isinstance(image, Image.Image):
        image = Image.fromarray(np.uint8(image))
    
    # Adjust color palette (soften colors)
    enhancer = ImageEnhance.Color(image)
    image = enhancer.enhance(0.8)  # Reduce color intensity
    
    # Adjust brightness and contrast for a warm, soft look
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.1)  # Slightly increase brightness
    
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(0.9)  # Slightly reduce contrast
    
    # Apply a slight blur to mimic hand-drawn softness
    image = image.filter(ImageEnhance.Sharpness(image).enhance(0.5))
    
    return image




app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        prompt = request.form["prompt"]
        output_path = os.path.join(UPLOAD_FOLDER, "ghibli_output.png")
        
        # Generate the image
        generate_ghibli_image(prompt, output_path)
        
        return render_template("index.html", image_url=output_path)
    
    return render_template("index.html", image_url=None)

@app.route("/download")
def download():
    return send_file(os.path.join(UPLOAD_FOLDER, "ghibli_output.png"), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)