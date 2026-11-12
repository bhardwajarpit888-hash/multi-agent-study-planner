import os
import json
from typing import Optional, Any
from dotenv import load_dotenv

load_dotenv()


class SmartMockLLM:
    """
    Intelligent deterministic fallback LLM.
    Ensures that testing, classmate simulations, and local execution
    work flawlessly even without an external API key or during network downtime.
    """

    def __init__(self, model_name: str = "mock-agent"):
        self.model_name = model_name

    def invoke(self, prompt: Any) -> Any:
        prompt_str = str(prompt)

        class MockResponse:
            def __init__(self, content: str):
                self.content = content

        # Check prompt intent
        if "Extract the syllabus into JSON" in prompt_str or "Syllabus Extraction Agent" in prompt_str:
            return MockResponse(
                json.dumps({
                    "course_code": "CS-301",
                    "course_name": "Applied Machine Learning & Neural Networks",
                    "description": "Foundations of Supervised, Unsupervised, and Deep Learning with real-world applications.",
                    "total_weeks": 4,
                    "modules": [
                        {
                            "id": "M1",
                            "title": "Module 1: Foundations of Machine Learning",
                            "description": "Linear regression, logistic regression, gradient descent, and loss functions.",
                            "order": 1,
                            "topics": [
                                {
                                    "id": "T1",
                                    "module_id": "M1",
                                    "title": "Linear Regression & Ordinary Least Squares",
                                    "description": "Cost function, closed-form normal equation vs gradient descent.",
                                    "estimated_hours": 2.0,
                                    "difficulty": 2,
                                    "prerequisites": [],
                                    "priority": "core"
                                },
                                {
                                    "id": "T2",
                                    "module_id": "M1",
                                    "title": "Gradient Descent Optimization & Learning Rates",
                                    "description": "Batch, stochastic, and mini-batch GD with convergence criteria.",
                                    "estimated_hours": 2.5,
                                    "difficulty": 3,
                                    "prerequisites": ["T1"],
                                    "priority": "core"
                                },
                                {
                                    "id": "T3",
                                    "module_id": "M1",
                                    "title": "Logistic Regression & Cross-Entropy Loss",
                                    "description": "Sigmoid function, decision boundaries, multi-class classification.",
                                    "estimated_hours": 2.0,
                                    "difficulty": 2,
                                    "prerequisites": ["T1"],
                                    "priority": "core"
                                }
                            ]
                        },
                        {
                            "id": "M2",
                            "title": "Module 2: Model Evaluation & Regularization",
                            "description": "Bias-variance tradeoff, L1/L2 regularization, ROC-AUC, cross-validation.",
                            "order": 2,
                            "topics": [
                                {
                                    "id": "T4",
                                    "module_id": "M2",
                                    "title": "Bias-Variance Tradeoff & Overfitting",
                                    "description": "High bias vs high variance diagnosis and learning curves.",
                                    "estimated_hours": 2.0,
                                    "difficulty": 3,
                                    "prerequisites": ["T2"],
                                    "priority": "core"
                                },
                                {
                                    "id": "T5",
                                    "module_id": "M2",
                                    "title": "L1 (Lasso) and L2 (Ridge) Regularization",
                                    "description": "Penalized regression, sparsity, and weight decay mechanics.",
                                    "estimated_hours": 2.5,
                                    "difficulty": 3,
                                    "prerequisites": ["T4"],
                                    "priority": "core"
                                },
                                {
                                    "id": "T6",
                                    "module_id": "M2",
                                    "title": "Validation Strategies: K-Fold Cross Validation & ROC/PR Curves",
                                    "description": "Stratified K-fold, confusion matrix, precision, recall, F1, and AUC.",
                                    "estimated_hours": 2.0,
                                    "difficulty": 2,
                                    "prerequisites": ["T3", "T4"],
                                    "priority": "core"
                                }
                            ]
                        },
                        {
                            "id": "M3",
                            "title": "Module 3: Tree Models & Ensembles",
                            "description": "Decision trees, Random Forests, and Gradient Boosting machines.",
                            "order": 3,
                            "topics": [
                                {
                                    "id": "T7",
                                    "module_id": "M3",
                                    "title": "Decision Trees: Gini Impurity & Information Gain",
                                    "description": "Tree splitting criteria, pruning, CART algorithm.",
                                    "estimated_hours": 2.0,
                                    "difficulty": 2,
                                    "prerequisites": [],
                                    "priority": "core"
                                },
                                {
                                    "id": "T8",
                                    "module_id": "M3",
                                    "title": "Random Forests & Bagging Ensembles",
                                    "description": "Bootstrap aggregating, out-of-bag error, feature importance.",
                                    "estimated_hours": 2.5,
                                    "difficulty": 3,
                                    "prerequisites": ["T7"],
                                    "priority": "core"
                                },
                                {
                                    "id": "T9",
                                    "module_id": "M3",
                                    "title": "Gradient Boosted Trees (XGBoost & LightGBM)",
                                    "description": "Sequential residual fitting, shrinkage, boosting theory.",
                                    "estimated_hours": 3.0,
                                    "difficulty": 4,
                                    "prerequisites": ["T8"],
                                    "priority": "core"
                                }
                            ]
                        },
                        {
                            "id": "M4",
                            "title": "Module 4: Deep Learning & Neural Network Fundamentals",
                            "description": "Perceptrons, backpropagation, PyTorch basics, and CNN intuition.",
                            "order": 4,
                            "topics": [
                                {
                                    "id": "T10",
                                    "module_id": "M4",
                                    "title": "Multilayer Perceptrons & Activation Functions",
                                    "description": "ReLU, LeakyReLU, Softmax, universal approximation theorem.",
                                    "estimated_hours": 2.5,
                                    "difficulty": 3,
                                    "prerequisites": ["T2"],
                                    "priority": "core"
                                },
                                {
                                    "id": "T11",
                                    "module_id": "M4",
                                    "title": "Backpropagation Algorithm & Computational Graphs",
                                    "description": "Chain rule in matrix calculus, vanishing/exploding gradients.",
                                    "estimated_hours": 3.5,
                                    "difficulty": 5,
                                    "prerequisites": ["T10"],
                                    "priority": "core"
                                },
                                {
                                    "id": "T12",
                                    "module_id": "M4",
                                    "title": "Introduction to Convolutional Neural Networks (CNNs)",
                                    "description": "Kernel convolutions, stride, pooling, and feature hierarchies.",
                                    "estimated_hours": 3.0,
                                    "difficulty": 4,
                                    "prerequisites": ["T11"],
                                    "priority": "core"
                                }
                            ]
                        }
                    ]
                })
            )

        if "Adaptive Replanner Agent" in prompt_str or "replan the schedule" in prompt_str:
            return MockResponse(
                json.dumps({
                    "strategy_used": "Buffer Absorption & Weekend Catch-up",
                    "explanation": "Missed topics were seamlessly absorbed into the upcoming Saturday buffer slot and distributed to lower-density days, maintaining your daily limit without overburdening your schedule.",
                    "notes": "No planned rest days were compromised."
                })
            )

        if "Student Advisor" in prompt_str:
            return MockResponse(
                "Great effort! It's completely normal to fall behind on challenging topics like Gradient Descent. "
                "I've dynamically redistributed the missed material into your upcoming buffer blocks. "
                "Focus on understanding the core intuitions today—you're still comfortably on track to finish the course on time!"
            )

        return MockResponse("Acknowledged. Processing study plan state update.")


def get_llm(provider: Optional[str] = None, api_key: Optional[str] = None):
    """
    Factory to instantiate LLM client based on environment or user selection.
    Supports OpenAI, Groq, Anthropic, and SmartMockLLM fallback.
    """
    provider = provider or os.getenv("LLM_PROVIDER", "openai").lower()
    
    # 1. OpenAI
    if provider == "openai":
        openai_key = api_key or os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                from langchain_openai import ChatOpenAI
                model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
                return ChatOpenAI(
                    model=model,
                    openai_api_key=openai_key,
                    temperature=0.2,
                )
            except Exception as e:
                print(f"[Config] OpenAI initialization warning: {e}. Falling back to SmartMockLLM.")

    # 2. Groq (High-speed Llama 3)
    elif provider == "groq":
        groq_key = api_key or os.getenv("GROQ_API_KEY")
        if groq_key:
            try:
                from langchain_groq import ChatGroq
                model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
                return ChatGroq(
                    model=model,
                    groq_api_key=groq_key,
                    temperature=0.2,
                )
            except Exception as e:
                print(f"[Config] Groq initialization warning: {e}. Falling back to SmartMockLLM.")

    # 3. Anthropic Claude
    elif provider in ["anthropic", "claude"]:
        anthropic_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            try:
                from langchain_anthropic import ChatAnthropic
                model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
                return ChatAnthropic(
                    model=model,
                    anthropic_api_key=anthropic_key,
                    temperature=0.2,
                )
            except Exception as e:
                print(f"[Config] Anthropic initialization warning: {e}. Falling back to SmartMockLLM.")

    # Default Deterministic Fallback Engine
    return SmartMockLLM()
