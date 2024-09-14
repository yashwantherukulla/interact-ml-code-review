import code_review_controller

if __name__ == "__main__":
    example_body = {
        'repo_links': ["https://github.com/Mohit-Talgotra/regit.git", "https://github.com/kiwi0fruit/ipynb-py-convert.git"]
    }
    print(code_review_controller.codeReview(example_body))