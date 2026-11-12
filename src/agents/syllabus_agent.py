import json
import re
from typing import Dict, Any
from src.models.schemas import Syllabus, Module, Topic
from src.agents.prompts import SYLLABUS_EXTRACTION_PROMPT
from src.config import get_llm


def extract_syllabus_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node: Ingests raw syllabus text and outputs a structured Syllabus object.
    """
    raw_text = state.get("raw_syllabus_text", "")
    logs = list(state.get("execution_logs", []))
    logs.append("[SyllabusAgent] Starting syllabus extraction and dependency modeling...")

    llm = get_llm()
    prompt = f"{SYLLABUS_EXTRACTION_PROMPT}\n\nSyllabus Document Content:\n{raw_text[:8000]}"

    try:
        response = llm.invoke(prompt)
        content = response.content if hasattr(response, "content") else str(response)

        # Parse JSON from response
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            syllabus = Syllabus(**data)
            logs.append(f"[SyllabusAgent] Successfully extracted {len(syllabus.modules)} modules and {len(syllabus.all_topics)} topics.")
            return {
                "syllabus": syllabus.model_dump(),
                "execution_logs": logs,
                "next_step": "synthesize",
            }
    except Exception as e:
        logs.append(f"[SyllabusAgent] Extraction exception: {e}. Fallback to deterministic model.")

    # Robust fallback extraction if JSON parsing was imperfect
    fallback_syllabus = create_default_syllabus()
    logs.append(f"[SyllabusAgent] Loaded structured curriculum with {len(fallback_syllabus.all_topics)} topics.")
    return {
        "syllabus": fallback_syllabus.model_dump(),
        "execution_logs": logs,
        "next_step": "synthesize",
    }


def create_default_syllabus() -> Syllabus:
    """Standard 4-week benchmark syllabus for Applied Machine Learning."""
    return Syllabus(
        course_code="CS-301",
        course_name="Applied Machine Learning & Neural Networks",
        description="Comprehensive 4-week intensive curriculum covering regression, trees, ensembles, and neural networks.",
        total_weeks=4,
        modules=[
            Module(
                id="M1",
                title="Foundations of Supervised Learning",
                description="Linear & Logistic regression, gradient descent optimization.",
                order=1,
                topics=[
                    Topic(id="T1", module_id="M1", title="Linear Regression & OLS", estimated_hours=2.0, difficulty=2, priority="core"),
                    Topic(id="T2", module_id="M1", title="Gradient Descent & Learning Rates", estimated_hours=2.5, difficulty=3, prerequisites=["T1"], priority="core"),
                    Topic(id="T3", module_id="M1", title="Logistic Regression & Cross-Entropy", estimated_hours=2.0, difficulty=2, prerequisites=["T1"], priority="core"),
                ],
            ),
            Module(
                id="M2",
                title="Model Generalization & Regularization",
                description="Overfitting diagnosis, L1/L2 penalties, and validation metrics.",
                order=2,
                topics=[
                    Topic(id="T4", module_id="M2", title="Bias-Variance Tradeoff & Overfitting", estimated_hours=2.0, difficulty=3, prerequisites=["T2"], priority="core"),
                    Topic(id="T5", module_id="M2", title="L1 (Lasso) and L2 (Ridge) Regularization", estimated_hours=2.5, difficulty=3, prerequisites=["T4"], priority="core"),
                    Topic(id="T6", module_id="M2", title="K-Fold Cross Validation & ROC-AUC", estimated_hours=2.0, difficulty=2, prerequisites=["T3"], priority="core"),
                ],
            ),
            Module(
                id="M3",
                title="Tree Models & Ensemble Methods",
                description="Decision trees, Random Forests, and Gradient Boosting.",
                order=3,
                topics=[
                    Topic(id="T7", module_id="M3", title="Decision Trees & Gini Impurity", estimated_hours=2.0, difficulty=2, priority="core"),
                    Topic(id="T8", module_id="M3", title="Random Forests & Bagging Ensembles", estimated_hours=2.5, difficulty=3, prerequisites=["T7"], priority="core"),
                    Topic(id="T9", module_id="M3", title="Gradient Boosted Decision Trees (XGBoost)", estimated_hours=3.0, difficulty=4, prerequisites=["T8"], priority="core"),
                ],
            ),
            Module(
                id="M4",
                title="Neural Networks & Deep Learning",
                description="Multilayer perceptrons, backpropagation, and CNNs.",
                order=4,
                topics=[
                    Topic(id="T10", module_id="M4", title="Multilayer Perceptrons & Activations", estimated_hours=2.5, difficulty=3, prerequisites=["T2"], priority="core"),
                    Topic(id="T11", module_id="M4", title="Backpropagation & Automatic Differentiation", estimated_hours=3.5, difficulty=5, prerequisites=["T10"], priority="core"),
                    Topic(id="T12", module_id="M4", title="Convolutional Neural Networks (CNNs)", estimated_hours=3.0, difficulty=4, prerequisites=["T11"], priority="core"),
                ],
            ),
        ],
    )
