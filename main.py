from agents import Agent,Runner, function_tool,RunContextWrapper,GuardrailFunctionOutput,input_guardrail, TResponseInputItem, InputGuardrailTripwireTriggered,ModelSettings
from config.config import config, model
from pydantic import BaseModel

ORDERS = {
    "111": "Processing – will be shipped in 2 days",
    "222": "Shipped – tracking number: TRK987654",
    "333": "Delivered – on 25 Aug 2025",
}

# Tool Calling for Order Status
@function_tool
def get_order_status(order_id):
    for order_status in ORDERS:
        if order_id == order_status:
            return f"The Order Status of [{order_id}] is:  {ORDERS[order_id]}"
    return error_function()

def error_function():
    return f"Order_id is not correct, Please provide correct order_id"


# Guardrail for Non-Political Content
class User_Input(BaseModel):
    is_correct : bool
    reason : str

@input_guardrail
async def validate_user_input(ctx:RunContextWrapper,agent:Agent,input: str | list[TResponseInputItem])-> GuardrailFunctionOutput:
    Input_Checker = Agent(
        name="Input Checker",
        instructions="""
        You are a strict classifier. 
        Only return JSON in this format:
        { "is_correct": true/false, "reason": "<short reason>" }

        Rule:
        - If input contains offensive words (stupid, hate, idiot, etc.) → is_correct=false and if mentions politics, political parties, or politicians → is_correct=false
        - Otherwise → is_correct=true
        """,
       model=model,
       output_type=User_Input
    )
    result = await Runner.run(Input_Checker,input,run_config=config)
    res: User_Input = result.final_output

    return GuardrailFunctionOutput(
        output_info=res,
        tripwire_triggered=not res.is_correct
    )

Human_Agent = Agent(
    name="Human Agent",
    instructions="""You are a human agent.
    If user ask to complex queries or negative sentiment, Please answer politily and positive
    Answer clean and concise.
    """,
    model=model
)


Customer_Agent = Agent(
    name="Customer Support Agent",
    instructions ="""
    You are a friendly E-commerce customer support agent. 
    - Answer customer FAQs politely. 
    - Provide product details, order status, return/refund policy, and shipping info. 
    - If you don’t know, ask customer for more details.
    - If user ask complex queries or negative sentiment handoff to Human Agent
    """,
    handoffs=[Human_Agent], # Handoff to Human Agent if found Negative Input
    model=model,
    tools=[get_order_status],
    input_guardrails=[validate_user_input],
    model_settings=ModelSettings(
        tool_choice='auto',  # Enable Auto Tool Selection
        
        # metadata={"customer_id": "CUST-001", "session_id": "abc123"}

    )
)

def main():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🤖 Welcome to the Customer Support Agent")
    print("💡 Type 'exit' anytime to quit.")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(" ")
    
    while True:
        try:
            prompt = input("🟢 Your Question: ")
            if prompt.lower() in ["exit"]:
                print("👋 Exiting... Have a great day!")
                break
            result = Runner.run_sync(Customer_Agent,prompt,run_config=config)
            print("💬 Answer:", result.final_output)
        except InputGuardrailTripwireTriggered as e:
            print("🚨 Tripwire triggered: Please provide correct Input")
main()