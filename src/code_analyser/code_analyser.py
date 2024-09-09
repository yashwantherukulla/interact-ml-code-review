from groq import Groq
import instructor

from code_file_eval_model import CodeReviewModel

def get_code(file_path:str):
    with open(file_path, 'r') as f:
        code = f.read()
    return code


sys_prompt = """
You are an expert code reviewer evaluating a project for a hackathon.\n
Your task is to analyze the given code and provide a comprehensive review.\n
Focus on code quality, functionality, performance, innovation, and hackathon-specific aspects.\n
Be objective, thorough, and constructive in your feedback.\n
Provide your review in the following JSON format.\n\n
Guidelines:\n
1. Scores should be integers from 1 to 10, where 1 is poor and 10 is excellent.\n
2. The overall_score should be between 0 and 100.\n
3. Provide concise, relevant remarks for each category explaining the score.\n
4. When giving remarks, refer to the point of weakness or strength if any.\n
4. For lists (strengths, weaknesses, improvement_suggestions), provide at least three items.\n
5. Base your review solely on the code provided, making reasonable inferences about its context and purpose.\n
6. Consider the hackathon context in your assessment, particularly for innovation, project impact, and technical complexity.\n
7. In the final_remarks, summarize the key points of your review.\n
8. In the recommendation, suggest whether the project should be considered for awards or further development.\n\n
Analyze the code thoroughly and provide a balanced, insightful review that will be valuable for the judges to evaluate the team better.\n
NOTE: THIS IS MEANT TO VIEWED BY THE JUDGES OF THE HACKATHON, MAKE IT SUCH THAT, IT ASSISTS THEM IN THEIR EVALUATION.\n
"""



client = Groq(api_key="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")
client = instructor.from_groq(client, mode=instructor.Mode.TOOLS)

output = client.chat.completions.create(
    model="llama-3.1-70b-versatile",#"mixtral-8x7b-32768",
    messages=[
        {
            "role": "system",
            "content": sys_prompt
        },
        {
            "role": "user",
            "content": get_code("src/code_analyser/example_code.py"),
        }
    ],
    response_model=CodeReviewModel,
)

print(output.model_dump_json(indent=2))