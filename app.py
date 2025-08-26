import streamlit as st
import google.generativeai as genai
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import time

# --- 🔑 IMPORTANT: Hardcode Your API Keys Here ---
# Replace "YOUR_GOOGLE_API_KEY" with your actual Google AI Studio API key.
# Replace "YOUR_CLIPDROP_API_KEY" with your actual Clipdrop API key.
GOOGLE_API_KEY = "GOOGLE_API_KEY"
CLIPDROP_API_KEY = "CLIPDROP_API_KEY"

# --- Style and Configuration ---
ART_STYLES = {
    "Disney Animation": {
        "name": "Disney Animation",
        "prompt_addition": "Disney-style animation, vibrant colors, expressive characters, magical atmosphere, detailed backgrounds, professional Disney art style",
        "description": "Classic Disney animated movie style",
    },
    "Pixar 3D": {
        "name": "Pixar 3D",
        "prompt_addition": "Pixar-style 3D animation, cute characters, warm lighting, detailed textures, cinematic quality, professional 3D rendering",
        "description": "Modern Pixar 3D animation style",
    },
    "Studio Ghibli": {
        "name": "Studio Ghibli",
        "prompt_addition": "Studio Ghibli style, hand-drawn animation, soft watercolor backgrounds, whimsical characters, nature-focused, dreamy atmosphere",
        "description": "Beautiful hand-drawn Studio Ghibli style",
    },
    "Comic Book": {
        "name": "Comic Book",
        "prompt_addition": "Comic book illustration style, bold outlines, dynamic poses, vibrant colors, action-packed scenes, graphic novel art",
        "description": "Dynamic comic book style",
    },
}

# --- Helper Functions ---

def inject_custom_css():
    """Inject custom CSS for professional styling."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

    /* --- EDITED FOR PURE WHITE THEME & LAYOUT --- */
    body {
        background-color: #FFFFFF !important;
    }
    .main {
        background: #FFFFFF;
        font-family: 'Poppins', sans-serif;
        color: #000000; /* Set main text to black */
    }
    .stApp {
        background: #FFFFFF;
    }
    hr {
        display: none !important; /* This hides the horizontal line */
    }
    .main-header, .story-card {
        background: #f0f2f6; /* Light grey for card elements */
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 2rem;
    }
    .story-card {
        padding: 2rem;
        margin: 1rem 0;
    }
    /* --- END EDITED SECTION --- */

    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stButton > button {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }
    #MainMenu, footer, header {
        visibility: hidden;
    }
    </style>
    """, unsafe_allow_html=True)


def get_character_consistency_prompt(story, selected_style):
    """Generate character consistency guidelines using Gemini."""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        template = f"Create a brief, single-paragraph visual guide for a story in a '{selected_style}' style. Story: {story}"
        response = model.generate_content(template)
        return response.text
    except Exception as e:
        st.warning("Gemini analysis failed. Using a fallback guide.")
        return f"A basic guide for characters in a {selected_style} style."

def get_refined_image_prompts(story, consistency_guide, selected_style, num_scenes):
    """Generate refined image prompts using Gemini."""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        style_info = ART_STYLES[selected_style]["prompt_addition"]
        template = f"""
        Generate {num_scenes} image prompts for the story below, following the visual guide.
        Story: {story}
        Visual Guide: {consistency_guide}
        Art Style: {style_info}
        Instructions: Return ONLY a Python list of lists. Each inner list must contain a single string: the detailed, concise prompt (under 80 words).
        Example: [["Prompt 1..."], ["Prompt 2..."]]
        """
        response = model.generate_content(template)
        response_text = response.text.strip().replace("`", "").replace("python", "")
        prompts = eval(response_text)
        return prompts
    except Exception as e:
        st.error(f"Gemini prompt generation failed: {e}")
        return None

def generate_image(prompt, retries=3, delay=5):
    """
    Generate an image using the Clipdrop API with a retry mechanism.
    """
    for attempt in range(retries):
        try:
            response = requests.post(
                'https://clipdrop-api.co/text-to-image/v1',
                headers={'x-api-key': CLIPDROP_API_KEY},
                files={'prompt': (None, prompt[0], 'text/plain')},
                timeout=60
            )
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content))
            return image
        except requests.exceptions.HTTPError as err:
            st.warning(f"HTTP error occurred: {err.response.status_code}. Retrying ({attempt + 1}/{retries})...")
            time.sleep(delay)
        except requests.exceptions.RequestException as e:
            st.warning(f"Request failed: {e}. Retrying ({attempt + 1}/{retries})...")
            time.sleep(delay)
    st.error("Image generation failed after multiple retries.")
    return create_placeholder_image(prompt[0])


def create_placeholder_image(text):
    """Create a placeholder image when generation fails."""
    img = Image.new('RGB', (1024, 576), color='#FF6B6B')
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        font = ImageFont.load_default()
    draw.text((50, 50), "Image Generation Failed", fill="white", font=font)
    draw.text((50, 120), "Could not connect to the model.", fill="white", font=font)
    return img

def get_image_download_link(img, filename, text):
    """Generate a link to download the image."""
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:image/png;base64,{img_str}" download="{filename}" style="color: #4ECDC4; text-decoration: none;">{text}</a>'
    return href

# --- UI Functions ---

def create_story_viewer():
    """Display all generated images in a responsive grid."""
    if not st.session_state.get('generated_images'):
        st.info("📚 Your visual story will appear here once created.")
        return

    st.markdown("### 📖 Your Visual Story")
    st.markdown("---")

    for i in range(0, len(st.session_state.generated_images), 2):
        cols = st.columns(2)
        for col_idx, col in enumerate(cols):
            img_idx = i + col_idx
            if img_idx < len(st.session_state.generated_images):
                image = st.session_state.generated_images[img_idx]
                prompt = st.session_state.prompts[img_idx]
                col.image(image, caption=f"Scene {img_idx+1}", use_container_width=True)
                with col.expander("📋 Scene Details"):
                    st.write(f"**Prompt:** {prompt[0]}")
                col.markdown(get_image_download_link(image, f"scene_{img_idx+1}.png", "📥 Download Scene"), unsafe_allow_html=True)

def main():
    st.set_page_config(layout="wide", page_title="AI Story Visualizer", page_icon="✨")
    inject_custom_css()

    # --- API Key Check ---
    if GOOGLE_API_KEY == "YOUR_GOOGLE_API_KEY" or CLIPDROP_API_KEY == "YOUR_CLIPDROP_API_KEY":
        st.error("🚨 Please hardcode your Google and Clipdrop API keys in the script before running.")
        return

    try:
        genai.configure(api_key=GOOGLE_API_KEY)
    except Exception as e:
        st.error(f"❌ Invalid Google API Key: {e}")
        return

    st.markdown('<div class="main-header"><h1 class="main-title">AI Story Visualizer </h1></div>', unsafe_allow_html=True)

    if 'generated_images' not in st.session_state:
        st.session_state.generated_images = []
        st.session_state.prompts = []

    tab1, tab2 = st.tabs(["🎨 Create Story", "📖 View Story"])

    with tab1:
        st.markdown('<div class="story-card">', unsafe_allow_html=True)
        story = st.text_area("### 📝 Your Story", height=200, placeholder="A lone astronaut discovers a glowing forest on a distant moon...")

        col1, col2 = st.columns(2)
        selected_style = col1.selectbox("### 🎨 Art Style", options=list(ART_STYLES.keys()), format_func=lambda x: f"{ART_STYLES[x]['name']} - {ART_STYLES[x]['description']}")
        num_scenes = col2.slider("### 📊 Number of Scenes", min_value=2, max_value=8, value=4)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("✨ Create Visual Story"):
            if not story or len(story.split()) < 10:
                st.warning("Please enter a story of at least 10 words.")
            else:
                with st.spinner("🚀 Beginning creative process..."):
                    st.session_state.generated_images, st.session_state.prompts = [], []

                    status = st.empty()
                    status.info("🎭 Analyzing characters and setting...")
                    guide = get_character_consistency_prompt(story, selected_style)

                    status.info("📝 Crafting detailed scene prompts...")
                    prompts = get_refined_image_prompts(story, guide, selected_style, num_scenes)

                    if prompts:
                        st.session_state.prompts = prompts
                        progress_bar = st.progress(0)
                        for idx, prompt in enumerate(prompts):
                            status.info(f"🎨 Generating scene {idx + 1}/{len(prompts)}...")
                            image = generate_image(prompt)
                            if image:
                                st.session_state.generated_images.append(image)
                            progress_bar.progress((idx + 1) / len(prompts))

                        if st.session_state.generated_images:
                            status.success(f"🎉 Successfully generated {len(st.session_state.generated_images)} scenes!")
                            st.balloons()
                        else:
                            status.error("❌ No images were generated. Please check the errors above.")

        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.generated_images:
            st.markdown("---")
            st.markdown("### ✨ Generated Scenes Gallery")
            cols = st.columns(len(st.session_state.generated_images))
            for idx, col in enumerate(cols):
                col.image(st.session_state.generated_images[idx], caption=f"Scene {idx+1}", use_container_width=True)

    with tab2:
        create_story_viewer()

if __name__ == "__main__":
    main()
