from openai import OpenAI

def send_to_llm(message, prompt):
    # Use synchronous OpenAI client
    client = OpenAI()

    # Call OpenAI API and wait for response (blocking)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": message}
        ],
        temperature=1,
        top_p=0.01,
        stream=False  # Blocking request, not streaming
    )

    # Extract response text
    return response.choices[0].message.content if response.choices else "No response received."