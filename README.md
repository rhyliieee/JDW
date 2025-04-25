# Job Description Writer (JDW)

A component of the [JobJigSaw](https://github.com/rhyliieee/JobJigSaw) suite, designed to generate professional and compelling job descriptions using AI.

## Features

- **AI-Powered Generation:** Leverages language models to transform raw job details into well-structured job descriptions.
- **Structured Input:** Accepts key job parameters (title, location, type, department, duties, qualifications, etc.).
- **Customizable Prompts:** Uses `prompts.yaml` for fine-tuning the generation process.
- **FastAPI Backend:** Provides a robust API endpoint for integration.
- **Streamlit UI:** Includes a simple web interface (`jobjigsawUI.py`) for direct interaction and testing.
- **Asynchronous Processing:** Utilizes FastAPI background tasks for non-blocking API operations (though the current implementation seems synchronous based on `jdw_endpoint.py`).
- **Caching System:** Employs `CacheManager` for potentially caching agents or compiled graphs.
- **Structured Output:** Uses Pydantic models (`data_models.py`) for reliable data handling.

## Prerequisites

- Python 3.8 or higher
- Required API keys (depending on the models used):
  - LLM API key (e.g., Groq, Mistral, OpenAI - configured within the agent creation logic)
  - Direc JDW API key (`JDW_AGENT_API_KEY`)

## Installation

1.  **Navigate to the JDW directory:**
    ```bash
    cd path/to/jobjigsaw/integration/JDW 
    ```
2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    ```
3.  **Activate Virtual Environment:**
    ```bash
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    # source venv/bin/activate
    ```
4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Create a `.env` file** in the `JDW` directory with your API keys:
    ```env
    # Add necessary LLM API keys here, e.g.:
    # GROQ_API_KEY=your_groq_api_key_here
    # MISTRAL_API_KEY=your_mistral_api_key_here
    # OPENAI_API_KEY=your_openai_api_key_here
    JDW_AGENT_API_KEY=your_jdw_api_key_here

    # Optional: Specify API URL if not running locally
    # JDW_API_URL=http://your_jdw_api_host:8090 
    ```

## Usage

1.  **Start the JDW API Server:**
    Open a terminal, activate the virtual environment, and run:
    ```bash
    # Ensure you are in the JDW directory
    uvicorn jdw_endpoint:app --reload --host 0.0.0.0 --port 8090 
    ```
    The JDW API endpoint will be available at `http://localhost:8090`.

2.  **Start the Streamlit UI (Optional):**
    Open another terminal, activate the virtual environment, and run:
    ```bash
    # Ensure you are in the JDW directory
    streamlit run jobjigsawUI.py
    ```
    The Streamlit application will be available at `http://localhost:8501` (or the URL provided in the terminal).

## API Endpoints

API documentation is available via Swagger UI and ReDoc when the server is running:
- JDW API Docs: `http://localhost:8090/docs` or `/redoc`

Key Endpoints:
- `POST /ai/jdw/v1/job_description_writer`: Starts the job description generation process. Requires an API key and a `JDWRequest` body. Returns a `StartResponse` with a `trace_id`.
- `GET /ai/jdw/v1/status/{trace_id}`: Checks the status and retrieves results for a given `trace_id`. Returns a `StatusResponse`.
- `GET /ai/jdw/v1/health`: Health check endpoint. Requires an API key.

## Project Structure

```
JDW/
├── agents.py             # LLM agent initialization for JDW
├── data_models.py        # Pydantic models for JDW data structures
├── graph.py              # LangGraph Application Workflow for JDW
├── jdw_endpoint.py       # FastAPI endpoint definitions for JDW
├── jobjigsawUI.py        # Streamlit UI for JDW
├── prompts.yaml          # System prompts for the JDW agent
├── requirements.txt      # Python dependencies for JDW
├── utils.py              # Utility functions (e.g., CacheManager)
├── .env                  # Environment variables (API keys)
└── README.md             # This file
```

## System Architecture

```mermaid
graph TD
    subgraph User Interface
        A[jobjigsawUI.py (Streamlit)]
    end

    subgraph Backend API
        B[jdw_endpoint.py (FastAPI @ 8090)]
    end

    subgraph Core Logic
        C[graph.py (JDW Workflow)]
        D[agents.py]
        E[utils.py]
        F[data_models.py]
        G[prompts.yaml]
    end

    subgraph External Services
        H[LLM APIs (Groq, Mistral, OpenAI, etc.)]
    end

    A -- JDW Requests --> B
    B -- Initiates --> C
    C -- Uses --> D
    C -- Uses --> F
    D -- Uses --> G
    D -- Calls --> H
    B -- Uses --> E # For CacheManager
    C -- Uses --> E # For CacheManager

```

## Data Flow

1.  User interacts with `jobjigsawUI.py` (Streamlit) or sends a request directly to the `jdw_endpoint.py` API.
2.  Input data (job title, duties, qualifications, etc.) is received by the API endpoint.
3.  The endpoint validates the request and API key.
4.  It potentially starts a background task (or runs synchronously) invoking the LangGraph workflow defined in `graph.py`.
5.  `graph.py` uses `agents.py` to initialize the JDW agent with prompts from `prompts.yaml`.
6.  The agent (`agents.py`) calls the configured LLM API (`H`) to generate the job description based on the input and prompts.
7.  The generated description is structured using `data_models.py`.
8.  The result is stored (if using background tasks and status checks) or returned directly to the caller (UI or API client).

## Contributing

Refer to the main `JobJigSaw` project guidelines.

## License

Refer to the main `JobJigSaw` project license.
