from pydantic import BaseModel, Field
from typing import List, Optional

class CodeReviewCategory(BaseModel):
    score: int = Field(..., ge=1, le=10, description="Score from 1 to 10")
    remarks: Optional[str] = Field(None, description="Remarks explaining the score")

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
    overall_score: int = Field(..., ge=0, le=100, description="Overall score out of 100")
    strengths: List[str] = Field(..., min_items=1, description="List of project strengths")
    weaknesses: List[str] = Field(..., min_items=1, description="List of project weaknesses")
    improvement_suggestions: List[str] = Field(..., min_items=1, description="Suggestions for improvement")
    complexity_score: CodeReviewCategory

    # Hackathon-specific
    project_impact: CodeReviewCategory
    technical_complexity: CodeReviewCategory
    practicality: CodeReviewCategory

    # Final Evaluation
    final_remarks: str = Field(..., description="Final remarks summarizing the review")