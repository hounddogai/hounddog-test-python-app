import asyncio
import os
from typing import Optional, Dict, Any
import traceback
from dotenv import load_dotenv

from nicegui import ui, app
import openai
import anthropic
import google.genai as genai

# Load environment variables from .env file
load_dotenv(override=True)


# Model configurations - will be populated dynamically
OPENAI_MODELS = []
ANTHROPIC_MODELS = []
GOOGLE_MODELS = []

# Track if models have been loaded
MODELS_LOADED = False

# Global variables for UI components
prompt_input = None
openai_model_select = None
anthropic_model_select = None
google_model_select = None
submit_button = None
result_tabs = None
openai_result = None
anthropic_result = None
google_result = None
loading_spinner = None

async def fetch_openai_models(api_key: str) -> list:
    """Fetch available OpenAI models"""
    try:
        client = openai.AsyncOpenAI(api_key=api_key)
        response = await client.models.list()
        # Filter for chat models and sort by name
        models = [model.id for model in response.data if 'gpt' in model.id.lower()]
        models.sort()
        return models
    except Exception as e:
        print(f"Error fetching OpenAI models: {e}")
        raise e


async def fetch_anthropic_models(api_key: str) -> list:
    """Fetch available Anthropic models"""
    try:
        # Anthropic doesn't have a models list endpoint, so we use known models
        # but we can test connectivity
        client = anthropic.AsyncAnthropic(api_key=api_key)
        # Test with a minimal request to verify the key works
        await client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1,
            messages=[{"role": "user", "content": "test"}]
        )
        # Return known models if the key works
        return [
            "claude-opus-4-20250514",
            "claude-sonnet-4-20250514",
            "claude-3-7-sonnet-20250219",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022"
        ]
    except Exception as e:
        print(f"Error testing Anthropic API: {e}")
        raise e


async def fetch_google_models(api_key: str) -> list:
    """Fetch available Google models"""
    try:
        client = genai.Client(api_key=api_key)
        response = await client.aio.models.list()
        # Filter for generative models
        models = []
        async for model in response:
            if hasattr(model, 'name') and 'gemini' in model.name.lower():
                # Extract model name from full path (e.g., "models/gemini-1.5-pro" -> "gemini-1.5-pro")
                model_name = model.name.split('/')[-1] if '/' in model.name else model.name
                models.append(model_name)
        models.sort()
        if not models:
            raise Exception("No Gemini models found")
        return models
    except Exception as e:
        print(f"Error fetching Google models: {e}")
        raise e


async def load_all_models():
    """Load models from all available APIs"""
    global OPENAI_MODELS, ANTHROPIC_MODELS, GOOGLE_MODELS, MODELS_LOADED

    api_status = check_api_keys()
    tasks = []

    # Clear existing models
    OPENAI_MODELS = []
    ANTHROPIC_MODELS = []
    GOOGLE_MODELS = []

    # Only fetch models for APIs with valid keys
    if api_status['openai']:
        tasks.append(('openai', fetch_openai_models(os.getenv("OPENAI_API_KEY"))))

    if api_status['anthropic']:
        tasks.append(('anthropic', fetch_anthropic_models(os.getenv("ANTHROPIC_API_KEY"))))

    if api_status['google']:
        tasks.append(('google', fetch_google_models(os.getenv("GEMINI_API_KEY"))))

    if not tasks:
        ui.notify("No API keys configured. Please set up your API keys first.", type="warning")
        MODELS_LOADED = False
        return

    # Execute all model fetching tasks
    print("Loading models from APIs...")
    results = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)

    success_count = 0
    for i, (provider, _) in enumerate(tasks):
        if isinstance(results[i], Exception):
            print(f"Failed to load {provider} models: {results[i]}")
            ui.notify(f"Failed to load {provider.title()} models: {str(results[i])}", type="negative")
        else:
            success_count += 1
            if provider == 'openai':
                OPENAI_MODELS = results[i]
                print(f"Loaded {len(OPENAI_MODELS)} OpenAI models")
            elif provider == 'anthropic':
                ANTHROPIC_MODELS = results[i]
                print(f"Loaded {len(ANTHROPIC_MODELS)} Anthropic models")
            elif provider == 'google':
                GOOGLE_MODELS = results[i]
                print(f"Loaded {len(GOOGLE_MODELS)} Google models")

    if success_count > 0:
        MODELS_LOADED = True
        ui.notify(f"Successfully loaded models from {success_count} provider(s)!", type="positive")
    else:
        MODELS_LOADED = False
        ui.notify("Failed to load models from any provider. Please check your API keys.", type="negative")


# Check API key availability
def check_api_keys():
    """Check which API keys are available"""
    return {
        'openai': bool(os.getenv("OPENAI_API_KEY")),
        'anthropic': bool(os.getenv("ANTHROPIC_API_KEY")),
        'google': bool(os.getenv("GEMINI_API_KEY"))
    }


async def test_api_key(provider: str, api_key: str) -> Dict[str, Any]:
    """Test an API key by making a simple request"""
    try:
        if provider == "openai":
            client = openai.AsyncOpenAI(api_key=api_key)
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return {"success": True, "provider": provider}

        elif provider == "anthropic":
            client = anthropic.AsyncAnthropic(api_key=api_key)
            response = await client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=5,
                messages=[{"role": "user", "content": "Hello"}]
            )
            return {"success": True, "provider": provider}

        elif provider == "google":
            client = genai.Client(api_key=api_key)
            response = await client.aio.models.generate_content(
                model="gemini-1.5-flash",
                contents="Hello"
            )
            return {"success": True, "provider": provider}

        else:
            return {"success": False, "provider": provider, "error": "Unknown provider"}

    except Exception as e:
        return {"success": False, "provider": provider, "error": str(e)}


async def test_all_apis():
    """Test all available API keys"""
    api_status = check_api_keys()

    # Get API keys
    openai_key = os.getenv("OPENAI_API_KEY") if api_status['openai'] else None
    anthropic_key = os.getenv("ANTHROPIC_API_KEY") if api_status['anthropic'] else None
    google_key = os.getenv("GEMINI_API_KEY") if api_status['google'] else None

    # Test available APIs
    tasks = []
    if openai_key:
        tasks.append(test_api_key("openai", openai_key))
    if anthropic_key:
        tasks.append(test_api_key("anthropic", anthropic_key))
    if google_key:
        tasks.append(test_api_key("google", google_key))

    if not tasks:
        ui.notify("No API keys configured to test", type="warning")
        return

    ui.notify("Testing API keys...", type="info")

    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)

        success_count = 0
        for result in results:
            if isinstance(result, Exception):
                ui.notify(f"Test failed with exception: {str(result)}", type="negative")
            elif result["success"]:
                success_count += 1
                ui.notify(f"{result['provider'].title()} API key is working ✓", type="positive")
            else:
                ui.notify(f"{result['provider'].title()} API key failed: {result.get('error', 'Unknown error')}", type="negative")

        if success_count == len(tasks):
            ui.notify("All API keys are working! 🎉", type="positive")
        elif success_count > 0:
            ui.notify(f"{success_count}/{len(tasks)} API keys are working", type="warning")
        else:
            ui.notify("All API key tests failed", type="negative")

    except Exception as e:
        ui.notify(f"Error testing API keys: {str(e)}", type="negative")


async def call_openai_api(prompt: str, model: str, api_key: str) -> Dict[str, Any]:
    """Call OpenAI API and return response"""
    try:
        client = openai.AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        return {
            "success": True,
            "content": response.choices[0].message.content,
            "model": model
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "model": model
        }


async def call_anthropic_api(prompt: str, model: str, api_key: str) -> Dict[str, Any]:
    """Call Anthropic API and return response"""
    try:
        client = anthropic.AsyncAnthropic(api_key=api_key)
        response = await client.messages.create(
            model=model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        return {
            "success": True,
            "content": response.content[0].text,
            "model": model
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "model": model
        }


async def call_google_api(prompt: str, model: str, api_key: str) -> Dict[str, Any]:
    """Call Google Gemini API and return response"""
    try:
        client = genai.Client(api_key=api_key)
        response = await client.aio.models.generate_content(
            model=model,
            contents=prompt
        )
        return {
            "success": True,
            "content": response.text,
            "model": model
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "model": model
        }


def format_result(result: Dict[str, Any]) -> str:
    """Format API result for display"""
    if result["success"]:
        return f"**Model:** {result['model']}\n\n{result['content']}"
    else:
        return f"**Model:** {result['model']}\n\n**Error:** {result['error']}"


async def submit_prompt():
    """Handle form submission and call all APIs"""
    global loading_spinner, openai_result, anthropic_result, google_result

    # Get form values
    prompt = prompt_input.value.strip()
    openai_model = openai_model_select.value
    anthropic_model = anthropic_model_select.value
    google_model = google_model_select.value
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    google_key = os.getenv("GEMINI_API_KEY")

    # Validation
    if not prompt:
        ui.notify("Please enter a prompt", type="warning")
        return

    if not MODELS_LOADED:
        ui.notify("Please fetch models first using the 'Refresh Models' button", type="warning")
        return

    if not openai_key:
        ui.notify("OpenAI API key not found in environment variables", type="warning")
        return

    if not anthropic_key:
        ui.notify("Anthropic API key not found in environment variables", type="warning")
        return

    if not google_key:
        ui.notify("Gemini API key not found in environment variables", type="warning")
        return

    # Check if models are selected (and not placeholder text)
    if (not openai_model or openai_model == "Click 'Refresh Models' to load options") and OPENAI_MODELS:
        ui.notify("Please select an OpenAI model", type="warning")
        return

    if (not anthropic_model or anthropic_model == "Click 'Refresh Models' to load options") and ANTHROPIC_MODELS:
        ui.notify("Please select an Anthropic model", type="warning")
        return

    if (not google_model or google_model == "Click 'Refresh Models' to load options") and GOOGLE_MODELS:
        ui.notify("Please select a Google model", type="warning")
        return

    # Show loading state
    submit_button.disable()
    if loading_spinner:
        loading_spinner.set_visibility(True)

    # Clear previous results and show loading
    openai_result.clear()
    anthropic_result.clear()
    google_result.clear()

    with openai_result:
        ui.spinner(size="lg").classes("mb-2")
        ui.label("Calling OpenAI...")

    with anthropic_result:
        ui.spinner(size="lg").classes("mb-2")
        ui.label("Calling Anthropic...")

    with google_result:
        ui.spinner(size="lg").classes("mb-2")
        ui.label("Calling Google...")

    # Force UI update
    await asyncio.sleep(0.1)

    try:
        print(f"Starting API calls for prompt: {prompt[:50]}...")

        # Call all APIs concurrently
        tasks = [
            call_openai_api(prompt, openai_model, openai_key),
            call_anthropic_api(prompt, anthropic_model, anthropic_key),
            call_google_api(prompt, google_model, google_key)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        print(f"API calls completed. Results: {len(results)}")

        # Update results
        openai_result.clear()
        anthropic_result.clear()
        google_result.clear()

        # OpenAI result
        with openai_result:
            if isinstance(results[0], Exception):
                ui.markdown(f"**Model:** {openai_model}\n\n**Error:** {str(results[0])}")
                print(f"OpenAI error: {results[0]}")
            else:
                ui.markdown(format_result(results[0]))
                print("OpenAI result updated")

        # Anthropic result
        with anthropic_result:
            if isinstance(results[1], Exception):
                ui.markdown(f"**Model:** {anthropic_model}\n\n**Error:** {str(results[1])}")
                print(f"Anthropic error: {results[1]}")
            else:
                ui.markdown(format_result(results[1]))
                print("Anthropic result updated")

        # Google result
        with google_result:
            if isinstance(results[2], Exception):
                ui.markdown(f"**Model:** {google_model}\n\n**Error:** {str(results[2])}")
                print(f"Google error: {results[2]}")
            else:
                ui.markdown(format_result(results[2]))
                print("Google result updated")

        ui.notify("All responses received!", type="positive")

    except Exception as e:
        ui.notify(f"Error: {str(e)}", type="negative")
        print(f"Error in submit_prompt: {traceback.format_exc()}")

    finally:
        # Hide loading state
        submit_button.enable()
        if loading_spinner:
            loading_spinner.set_visibility(False)


def main():
    """Set up the UI"""
    global prompt_input, openai_model_select, anthropic_model_select, google_model_select
    global submit_button, result_tabs, openai_result, anthropic_result, google_result, loading_spinner

    # Set up the page
    ui.page_title("LLM Comparison Tool")

    # Header
    with ui.column().classes("w-full max-w-6xl mx-auto p-4"):
        ui.html("<h1 class='text-3xl font-bold text-center mb-2'>LLM Comparison Tool</h1>")
        ui.html("<p class='text-center text-gray-600 mb-6'>Compare responses from OpenAI GPT, Anthropic Claude, and Google Gemini</p>")

        # API Keys Status section
        with ui.card().classes("w-full p-4 mb-4"):
            with ui.expansion("API Keys", icon="key").classes("w-full"):
                ui.html("<p class='text-sm text-gray-600 mb-4'>API keys are read from environment variables (.env file)</p>")

                # Check API key status
                api_status = check_api_keys()

                with ui.row().classes("w-full gap-4 mb-4"):
                    with ui.column().classes("flex-1"):
                        with ui.row().classes("items-center gap-2"):
                            ui.image("public/logos/openai.png").classes("w-6 h-6")
                            if api_status['openai']:
                                ui.icon("check_circle", color="green").classes("text-lg")
                                ui.label("OPENAI_API_KEY").classes("text-green-600 font-medium")
                            else:
                                ui.icon("cancel", color="red").classes("text-lg")
                                ui.label("OPENAI_API_KEY").classes("text-red-600 font-medium")

                    with ui.column().classes("flex-1"):
                        with ui.row().classes("items-center gap-2"):
                            ui.image("public/logos/anthropic.png").classes("w-6 h-6")
                            if api_status['anthropic']:
                                ui.icon("check_circle", color="green").classes("text-lg")
                                ui.label("ANTHROPIC_API_KEY").classes("text-green-600 font-medium")
                            else:
                                ui.icon("cancel", color="red").classes("text-lg")
                                ui.label("ANTHROPIC_API_KEY").classes("text-red-600 font-medium")

                    with ui.column().classes("flex-1"):
                        with ui.row().classes("items-center gap-2"):
                            ui.image("public/logos/google-gemini.png").classes("w-6 h-6")
                            if api_status['google']:
                                ui.icon("check_circle", color="green").classes("text-lg")
                                ui.label("GEMINI_API_KEY").classes("text-green-600 font-medium")
                            else:
                                ui.icon("cancel", color="red").classes("text-lg")
                                ui.label("GEMINI_API_KEY").classes("text-red-600 font-medium")

                # Test button
                with ui.row().classes("w-full justify-right"):
                    ui.button(
                        "Test API Keys",
                        on_click=test_all_apis,
                        icon="network_check"
                    ).classes("bg-green-500 text-white px-4 py-2")

        # Model Selection section
        with ui.card().classes("w-full p-4 mb-4"):
            with ui.expansion("Model Selection", icon="tune").classes("w-full"):
                with ui.row().classes("w-full justify-between items-center mb-4"):
                    ui.html("<p class='text-sm text-gray-600'>Choose which models to use for comparison</p>")
                    ui.button(
                        "Refresh Models",
                        on_click=refresh_models,
                        icon="refresh"
                    ).classes("bg-blue-500 text-white px-3 py-1 text-sm")

                with ui.row().classes("w-full gap-4"):
                    with ui.column().classes("flex-1"):
                        with ui.row().classes("items-center gap-2 mb-2"):
                            ui.image("public/logos/openai.png").classes("w-5 h-5")
                            ui.label("OpenAI Model").classes("font-medium")
                        openai_model_select = ui.select(
                            options=["Click 'Refresh Models' to load options"],
                            value="Click 'Refresh Models' to load options"
                        ).classes("w-full")

                    with ui.column().classes("flex-1"):
                        with ui.row().classes("items-center gap-2 mb-2"):
                            ui.image("public/logos/anthropic.png").classes("w-5 h-5")
                            ui.label("Anthropic Model").classes("font-medium")
                        anthropic_model_select = ui.select(
                            options=["Click 'Refresh Models' to load options"],
                            value="Click 'Refresh Models' to load options"
                        ).classes("w-full")

                    with ui.column().classes("flex-1"):
                        with ui.row().classes("items-center gap-2 mb-2"):
                            ui.image("public/logos/google-gemini.png").classes("w-5 h-5")
                            ui.label("Google Model").classes("font-medium")
                        google_model_select = ui.select(
                            options=["Click 'Refresh Models' to load options"],
                            value="Click 'Refresh Models' to load options"
                        ).classes("w-full")

        # Input section
        with ui.card().classes("w-full p-4 mb-4"):
            ui.html("<h2 class='text-xl font-semibold mb-4'>Prompt</h2>")

            # Prompt input
            prompt_input = ui.textarea(
                label="Enter your prompt",
                placeholder="Ask a question or provide instructions...",
                value=""
            ).classes("w-full mb-4").props("rows=4")

            # Submit section
            with ui.row().classes("w-full justify-center items-center gap-4"):
                submit_button = ui.button(
                    "Compare Responses",
                    on_click=submit_prompt,
                    icon="send"
                ).classes("bg-blue-500 text-white px-6 py-2")

                loading_spinner = ui.spinner(size="md").set_visibility(False)

        # Results section
        with ui.card().classes("w-full p-4"):
            ui.html("<h2 class='text-xl font-semibold mb-4'>Results</h2>")

            with ui.tabs().classes("w-full") as tabs:
                openai_tab = ui.tab("OpenAI")
                anthropic_tab = ui.tab("Anthropic")
                google_tab = ui.tab("Gemini")

            with ui.tab_panels(tabs, value=openai_tab).classes("w-full"):
                with ui.tab_panel(openai_tab):
                    openai_result = ui.column().classes("w-full p-4 min-h-32")

                with ui.tab_panel(anthropic_tab):
                    anthropic_result = ui.column().classes("w-full p-4 min-h-32")

                with ui.tab_panel(google_tab):
                    google_result = ui.column().classes("w-full p-4 min-h-32")


async def refresh_models():
    """Refresh model lists from APIs"""
    await load_all_models()

    # Update the dropdowns
    if openai_model_select:
        openai_model_select.options = OPENAI_MODELS
        openai_model_select.value = OPENAI_MODELS[0] if OPENAI_MODELS else None
    if anthropic_model_select:
        anthropic_model_select.options = ANTHROPIC_MODELS
        anthropic_model_select.value = ANTHROPIC_MODELS[0] if ANTHROPIC_MODELS else None
    if google_model_select:
        google_model_select.options = GOOGLE_MODELS
        google_model_select.value = GOOGLE_MODELS[0] if GOOGLE_MODELS else None


if __name__ in {"__main__", "__mp_main__"}:
    main()
    ui.run(title="LLM Comparison Tool", port=8080, show=True)
