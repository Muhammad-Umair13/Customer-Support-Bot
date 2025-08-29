import os
from agents import AsyncOpenAI, OpenAIChatCompletionsModel, set_trace_processors
# from agents.tracing.processors import ConsoleSpanExporter, BatchTraceProcessor
from agents.run import RunConfig
from dotenv import load_dotenv

load_dotenv()


# || Add To See Logs ||
# exporter = ConsoleSpanExporter()
# processor = BatchTraceProcessor(exporter)
# set_trace_processors([processor])



Gemini_api_key = os.getenv("GEMINI_API_KEY")

if not Gemini_api_key:
    raise ValueError("Gemini_api_key is not found!")

client = AsyncOpenAI(
    api_key=Gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=client
)

config = RunConfig(
    model=model,
    model_provider=client,
    tracing_disabled=True
)