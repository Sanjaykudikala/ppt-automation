# AI Presentation Generator

> An intelligent Streamlit web application that generates professional, themed PowerPoint presentations using LangGraph and Groq.

## 🖼 Screenshot

*(Add screenshot here)*
![App Screenshot](images/screenshot.png)

## Live Demo

[Live Demo](https://ppt-automation-98sd.onrender.com)

## Features

- **End-to-End Generation:** Automatically creates complete PowerPoint presentations from a single topic.
- **Audience Targeting:** Customize the content complexity for Beginner, Intermediate, or Advanced audiences.
- **Configurable Length:** Choose between 5 to 20 slides per presentation.
- **Beautiful UI:** A modern, responsive interface built with Streamlit.
- **Export Ready:** Directly downloads the generated `.pptx` file.

## Tech Stack

- **Frontend:** Streamlit
- **AI/LLM:** Groq API
- **Agent Framework:** LangGraph & LangChain
- **PPT Generation:** python-pptx
- **Containerization:** Docker

## Architecture

1. **User Input:** Topic, number of slides, and audience level are submitted via the Streamlit UI.
2. **Orchestration:** LangGraph handles the agentic flow:
   - **Planner:** Outlines the presentation structure.
   - **Content Generation:** Expands the outline into detailed bullet points and speaker notes based on the audience level.
3. **Compilation:** `python-pptx` processes the AI's JSON output and constructs the physical `.pptx` file using a predefined schema.
4. **Delivery:** The final `.pptx` file is served directly to the browser for download.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/ppt-automation.git
   cd ppt-automation
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory and add your Groq API Key:
   ```env
   GROQ_API_KEY=your_groq_api_key
   ```

5. **Run the app:**
   ```bash
   streamlit run app.py
   ```

## Run with Docker

1. **Build the image:**
   ```bash
   docker build -t ai-presentation-generator .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8501:8501 --env GROQ_API_KEY=your_groq_api_key ai-presentation-generator
   ```
   *The app will be available at `http://localhost:8501`*

## Deployment

This project is optimized for deployment on **Render** using Docker.

1. Create a new **Web Service** on Render and connect your GitHub repository.
2. Choose **Docker** as the runtime environment.
3. Add `GROQ_API_KEY` under Environment Variables.
4. Deploy! Render will automatically use the provided `Dockerfile`.

## Project Structure

```text
ppt_automation/
├── app.py                 # Streamlit UI entry point
├── main.py                # CLI entry point
├── Dockerfile             # Docker configuration
├── requirements.txt       # Python dependencies
├── pptschema.json         # Schema for PPT generation
├── src/                   # Core application logic
│   ├── pipeline.py        # LangGraph workflow definition
│   ├── planner.py         # AI outline generation
│   ├── content_inserter.py# AI slide content generation
│   ├── ppt_maker.py       # Python-pptx generation logic
│   └── ...
└── output/                # Generated presentations (git ignored)
```

## Future Improvements

- [ ] Add image generation for slides using DALL-E or local models.
- [ ] Support custom PowerPoint templates (`.potx`).
- [ ] Implement caching to prevent unnecessary API calls for identical topics.
- [ ] Add granular control over slide layouts (e.g., two-column, image with text).

## License

[MIT License](https://choosealicense.com/licenses/mit/)
