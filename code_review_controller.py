import json
import subprocess
from src.__main__ import codeReviewer

def codeReview(body):
    if body == None:
        return {
            "message": "Repository links are required", "error": "Bad Request"
        }

    link_args = json.dumps(body['repo_links'])

    try:
        codeReviewer(link_args)
        return {
            "message": f"Repository analysis completed successfully.", "error": None
        }
    except Exception as e:
        return {
            "message": f"Error executing script", "error": str(e)
        }