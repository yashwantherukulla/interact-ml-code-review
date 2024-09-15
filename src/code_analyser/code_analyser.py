from groq import Groq
import instructor
import os
import json
import time
from .code_file_eval_model import CodeReviewModel
from collections import defaultdict
from ... import logger
import subprocess
from dotenv import load_dotenv

load_dotenv()


class CodeAnalyser:
    def __init__(self):
        self.logger = logger.setupLogger()

    def get_code(self, file_path: str):
        with open(file_path, "r") as f:
            code = f.read()
        return code

    def getOutput(self, filePath: str):
        sys_prompt = """
        You are an expert code reviewer evaluating a project for a hackathon.\n
        Your task is to analyze the given code and provide a comprehensive review.\n
        Focus on readability maintainability, consistency, commenting, correctness, completeness, error handling, efficiency, scalability, security, test coverage, innovation, creativity, complexity score, project impact,technical complexity, and practicality.\n
        Be objective, thorough, and constructive in your feedback.\n
        Provide your review in the following JSON format.\n\n
        Guidelines:\n
        1. Scores should be integers from 1 to 10, where 1 is poor and 10 is excellent.\n
        2. The overall_score should be between 0 and 100.\n
        3. Base your review solely on the code provided, making reasonable inferences about its context and purpose.\n
        4. Consider the hackathon context in your assessment, particularly for innovation, project impact, and technical complexity.\n
        Analyze the code thoroughly and provide a balanced, insightful review that will be valuable for the judges to evaluate the team better.\n
        NOTE: THIS IS MEANT TO VIEWED BY THE JUDGES OF THE HACKATHON, MAKE IT SUCH THAT, IT ASSISTS THEM IN THEIR EVALUATION.\n
        """

        client = Groq(api_key=os.getenv("API_KEY"))
        client = instructor.from_groq(client, mode=instructor.Mode.TOOLS)

        output = client.chat.completions.create(
            model="llama-3.1-70b-versatile",  # "mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": sys_prompt},
                {
                    "role": "user",
                    "content": self.get_code(filePath),
                },
            ],
            response_model=CodeReviewModel,
        )
        return output

    def processAllRepos(self, root_folder):
        scores = []
        for repoName in os.listdir(root_folder):
            mapping = {}
            repoPath = os.path.join(root_folder, repoName)
            if os.path.isdir(repoPath):
                self.processRepo(repoPath, mapping)
                score_summary = self.finalScores(repoPath)

            scores.append(score_summary)

            with open(os.path.join(repoPath, "file_output_mapping.json"), "w") as f:
                json.dump(mapping, f, indent=2)

        return scores

    def processRepo(self, repoPath, mapping):
        outputFolder = os.path.join(repoPath, "output_data")
        os.makedirs(outputFolder, exist_ok=True)
        chunkFolderPath = os.path.join(repoPath, "chunk_data")
        for file in os.listdir(chunkFolderPath):
            filePath = os.path.join(chunkFolderPath, file)
            if os.path.isfile(filePath):
                self.processFile(filePath, outputFolder, mapping)
            time.sleep(0.75)

    def processFile(self, filePath, outputFolder, mapping):
        try:
            output = self.getOutput(filePath).model_dump_json(indent=2)

            relativePath = os.path.relpath(filePath, "cloned_repos")
            ouputFileName = relativePath.replace(os.path.sep, "_") + "_output.txt"
            outputFilePath = os.path.join(outputFolder, ouputFileName)

            with open(outputFilePath, "w", encoding="utf-8") as f:
                f.write(output)

            mapping[filePath] = outputFilePath
        except Exception as e:
            self.logger.info(f"Error processing file {filePath}: {str(e)}")

    def finalScores(self, repoPath):
        directory = os.path.join(repoPath, "output_data")
        score_aggregation = defaultdict(int)
        files = 0

        for filename in os.listdir(directory):
            if filename.endswith(".txt"):
                with open(os.path.join(directory, filename), "r") as file:
                    data = json.load(file)

                for key, value in data.items():
                    if isinstance(value, dict) and "score" in value:
                        score_aggregation[key] += value["score"]
            files += 1

        for category in score_aggregation:
            score_aggregation[category] = round(score_aggregation[category] / files, 1)

        score_aggregation["repo_link"] = self.getGithubUrl(repoPath)
        return score_aggregation

    def getGithubUrl(self, repoPath):
        try:
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                cwd=repoPath,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            self.logger.warning(f"Unable to get GitHub URL for repo: {repoPath}")
            return "Unknown Repository"
