#  AI Story Visualizer  

Turn your stories into **beautiful visual scenes** with AI!  
This project uses **Google Gemini** to analyze stories and generate scene prompts, and **ClipDrop API** to create high-quality illustrations in different art styles (Disney, Pixar, Studio Ghibli, Comic Book).  

---

## 📽️ Demo Video  
👉 [🎥 Watch the demo](ai_story_.mp4)  

---

## 🌟 Features  
- 📝 Enter any story and convert it into multiple illustrated scenes  
- 🎭 Choose from different **art styles** (Disney Animation, Pixar 3D, Studio Ghibli, Comic Book)  
- 📖 View your story scenes in a gallery layout  
- 📥 Download generated images  
- 🎨 Character and environment consistency handled by Google Gemini  
- 🎉 Smooth Streamlit UI with a clean, modern design  

---

## ⚙️ Installation  

### 1️⃣ Clone the repo  
```bash
git clone https://github.com/durga221/ai-story-visualizer.git
cd ai-story-visualizer
Create a virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate   # On Windows
source venv/bin/activate  # On Mac/Linux

3️⃣ Install dependencies
pip install -r requirements.txt

🔑 API Keys

This app requires two API keys:

Google AI Studio API Key (for Gemini model) → Get Key Here

ClipDrop API Key (for image generation) → Get Key Here

👉 Open app.py and replace the placeholders:

GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"
CLIPDROP_API_KEY = "YOUR_CLIPDROP_API_KEY"

🚀 Usage

Run the Streamlit app:

streamlit run app.py


Then open the local server link shown in your terminal (usually http://localhost:8501).
