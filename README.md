# AI Presentation Generator

This is a Streamlit-based web application that generates professional, themed PowerPoint presentations using AI (Groq + LangGraph).

## Features

- Generate complete PowerPoint presentations based on a topic.
- Customize the number of slides (5-20).
- Tailor content to different audience levels (Beginner, Intermediate, Advanced).

## Local Development

### Requirements

- Python 3.10+
- Groq API Key

### Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your environment variables by creating a `.env` file in the root directory:
   ```
   GROQ_API_KEY=your_api_key_here
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

## Deployment on Render (via Docker)

This repository includes a `Dockerfile` for deploying the application on platforms like Render.

1. Connect your GitHub repository to a new **Web Service** in Render.
2. Select **Docker** as the Runtime environment.
3. Add your `GROQ_API_KEY` in the Render Environment Variables section.
4. Render will automatically build the Docker image and deploy the Streamlit app.
