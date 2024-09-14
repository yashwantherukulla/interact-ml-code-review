from pydantic import BaseModel, Field
from typing import List, Optional

class CodeReviewCategory(BaseModel):
    score: int = Field(..., ge=1, le=10, description="Score from 1 to 10")

class CodeReviewModel(BaseModel):
    # Code Quality
    readability: CodeReviewCategory
    maintainability: CodeReviewCategory
    consistency: CodeReviewCategory
    commenting: CodeReviewCategory

    # Functionality
    correctness: CodeReviewCategory
    completeness: CodeReviewCategory
    error_handling: CodeReviewCategory

    # Performance
    efficiency: CodeReviewCategory
    scalability: CodeReviewCategory

    # Security
    security: CodeReviewCategory

    # Testing
    test_coverage: CodeReviewCategory

    # Innovation (for hackathon context)
    innovation: CodeReviewCategory
    creativity: CodeReviewCategory

    # Overall Assessment
    complexity_score: CodeReviewCategory

    # Hackathon-specific
    project_impact: CodeReviewCategory
    technical_complexity: CodeReviewCategory
    practicality: CodeReviewCategory