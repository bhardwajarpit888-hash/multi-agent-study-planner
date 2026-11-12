import os
import pymupdf


SAMPLE_SYLLABUS_TEXT = """COURSE SYLLABUS: CS-301 APPLIED MACHINE LEARNING & NEURAL NETWORKS
Semester: Spring 2026 | Duration: 4 Weeks (Intensive)
Department of Computer Science & Engineering

1. COURSE DESCRIPTION
This course provides a comprehensive introduction to modern machine learning, focusing on supervised learning,
model evaluation, tree-based ensembles, and deep neural network fundamentals. Students will implement key
algorithms, diagnose model behavior, and complete hands-on practical assignments.

2. TARGET LEARNING OUTCOMES
- Understand the mathematical underpinnings of linear & logistic models, cost optimization, and gradient descent.
- Diagnose overfitting vs underfitting using bias-variance decomposition and regularization (L1/L2).
- Build and tune tree ensembles (Random Forests, XGBoost).
- Implement neural networks from scratch using computational graphs and backpropagation.

3. DETAILED WEEKLY BREAKDOWN

MODULE 1: FOUNDATIONS OF SUPERVISED LEARNING (Week 1)
- Topic 1.1: Linear Regression & Ordinary Least Squares (Est. 2.0 hrs, Difficulty: 2/5, Core)
  Closed-form normal equations, loss landscapes, mean squared error (MSE).
- Topic 1.2: Gradient Descent Optimization & Learning Rates (Est. 2.5 hrs, Difficulty: 3/5, Core)
  Batch vs Stochastic vs Mini-batch gradient descent; learning rate schedules, convergence checking.
- Topic 1.3: Logistic Regression & Cross-Entropy Loss (Est. 2.0 hrs, Difficulty: 2/5, Core)
  Odds ratio, Sigmoid activation, log-loss derivation, multi-class softmax extension.

MODULE 2: GENERALIZATION, VALIDATION & REGULARIZATION (Week 2)
- Topic 2.1: Bias-Variance Decomposition & Overfitting (Est. 2.0 hrs, Difficulty: 3/5, Core)
  Training vs test error curves, diagnosing model capacity, high bias vs high variance.
- Topic 2.2: L1 (Lasso) and L2 (Ridge) Regularization (Est. 2.5 hrs, Difficulty: 3/5, Core)
  L1 geometric sparsity, L2 weight decay, hyperparameter tuning with lambda.
- Topic 2.3: Validation Protocols & Evaluation Metrics (Est. 2.0 hrs, Difficulty: 2/5, Core)
  Stratified K-fold cross-validation, confusion matrices, Precision, Recall, F1 score, ROC-AUC.

MODULE 3: TREE-BASED ALGORITHMS & ENSEMBLE METHODS (Week 3)
- Topic 3.1: Decision Trees & Splitting Criteria (Est. 2.0 hrs, Difficulty: 2/5, Core)
  Information gain, Gini impurity, entropy, tree pruning algorithms (pre/post-pruning).
- Topic 3.2: Bagging & Random Forests (Est. 2.5 hrs, Difficulty: 3/5, Core)
  Bootstrap sampling, out-of-bag (OOB) error estimation, feature subsampling, feature importances.
- Topic 3.3: Boosting & Gradient Boosted Decision Trees (Est. 3.0 hrs, Difficulty: 4/5, Core)
  AdaBoost intuition, sequential residual minimization, XGBoost objective & regularization.

MODULE 4: DEEP LEARNING & NEURAL NETWORKS (Week 4)
- Topic 4.1: Multilayer Perceptrons & Activation Functions (Est. 2.5 hrs, Difficulty: 3/5, Core)
  Feedforward architecture, non-linear activations (ReLU, GELU, Sigmoid), universal approximation.
- Topic 4.2: Backpropagation & Computational Graphs (Est. 3.5 hrs, Difficulty: 5/5, Core)
  Reverse-mode automatic differentiation, matrix Jacobian products, vanishing gradient problem.
- Topic 4.3: Convolutional Neural Networks (CNNs) & Computer Vision (Est. 3.0 hrs, Difficulty: 4/5, Core)
  2D convolution filters, stride, padding, max pooling, receptive field computation.

4. COURSE POLICIES & EXAM SCHEDULE
- Daily self-paced study recommended: 2.0 to 2.5 hours.
- Dedicated catch-up buffer slots recommended every weekend.
- Final Comprehensive Examination: End of Week 4 (Day 28).
"""


def generate_sample_syllabus_pdf(output_path: str) -> str:
    """
    Generates a professional sample syllabus PDF using PyMuPDF.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    doc = pymupdf.open()
    
    # Split text into pages
    lines = SAMPLE_SYLLABUS_TEXT.split("\n")
    page_text = ""
    line_count = 0
    
    for line in lines:
        page_text += line + "\n"
        line_count += 1
        if line_count >= 38:
            page = doc.new_page(width=595, height=842) # A4
            # Rect margin: (left, top, right, bottom)
            rect = pymupdf.Rect(50, 50, 545, 792)
            page.insert_textbox(rect, page_text, fontsize=10, fontname="helv")
            page_text = ""
            line_count = 0
            
    if page_text.strip():
        page = doc.new_page(width=595, height=842)
        rect = pymupdf.Rect(50, 50, 545, 792)
        page.insert_textbox(rect, page_text, fontsize=10, fontname="helv")
        
    doc.save(output_path)
    doc.close()
    
    # Also save raw text file
    txt_path = output_path.replace(".pdf", ".txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(SAMPLE_SYLLABUS_TEXT)
        
    return output_path


if __name__ == "__main__":
    pdf_out = os.path.join(os.path.dirname(__file__), "..", "..", "sample_data", "sample_ml_syllabus.pdf")
    generate_sample_syllabus_pdf(pdf_out)
    print(f"Generated sample PDF at: {pdf_out}")
