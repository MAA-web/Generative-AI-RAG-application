# Prompt Templates for RAG System

This document describes the three prompt templates available in the RAG system for studying hallucination and faithfulness differences.

## Overview

The system supports three distinct prompt templates that can be selected via the API to compare their effectiveness in reducing hallucinations and improving faithfulness to the source documents.

## Template Selection

Templates are selected by passing the `prompt_template` parameter in the `/query` API endpoint:

```json
{
    "question": "What is the return policy?",
    "prompt_template": "strict"  // Options: "strict", "balanced", "permissive"
}
```

## Template Descriptions

### 1. Strict Template (`strict`)

**Purpose**: Maximum faithfulness with explicit anti-hallucination warnings

**Characteristics**:
- **Explicit anti-hallucination rules**: Multiple warnings against using external knowledge
- **Strict context-only policy**: Must only use information from provided context
- **Explicit uncertainty handling**: Must state when information is not available
- **No inference allowed**: Cannot infer or assume details not explicitly stated
- **Clear limitations**: Must acknowledge when context is unclear or incomplete

**Expected Behavior**:
- **Lowest hallucination risk**: Highest faithfulness to source documents
- **More "I don't know" responses**: Will refuse to answer if information isn't in context
- **Explicit citations required**: Must cite sources for all information
- **Conservative answers**: May provide less complete answers but more accurate

**Use Cases**:
- When accuracy is critical
- When you want to measure baseline faithfulness
- When studying maximum anti-hallucination techniques

**Example Response Style**:
> "Based on the policy documents, I don't have specific information about [topic]. Please contact Micro Center customer service for assistance."

### 2. Balanced Template (`balanced`) - Default

**Purpose**: Moderate approach balancing helpfulness and accuracy

**Characteristics**:
- **Context-first approach**: Prioritizes information from provided context
- **Clear instructions**: Instructs to use only context, but less aggressive than strict
- **Standard uncertainty handling**: Suggests contacting customer service when information is missing
- **Customer-friendly tone**: Balanced between accuracy and helpfulness
- **Citation requirements**: Includes citations but less strict about format

**Expected Behavior**:
- **Moderate hallucination risk**: Good balance between accuracy and completeness
- **Standard responses**: Typical RAG behavior
- **Some inference**: May make reasonable inferences from context
- **Helpful but cautious**: Tries to be helpful while staying grounded

**Use Cases**:
- Default production use
- General question answering
- When you want standard RAG behavior

**Example Response Style**:
> "According to Micro Center's return policy [Source: ReturnPolicy.txt], items can be returned within 30 days. If you have specific questions about your return, please contact customer service."

### 3. Permissive Template (`permissive`)

**Purpose**: Allows general knowledge supplementation while emphasizing context

**Characteristics**:
- **Context-priority**: Prioritizes context but allows general knowledge
- **Supplementation allowed**: Can use general retail knowledge if context is incomplete
- **Distinction required**: Must distinguish between document info and general knowledge
- **More complete answers**: May provide more comprehensive responses
- **Flexible citation**: Citations for context, but may include general guidance

**Expected Behavior**:
- **Higher hallucination risk**: May include information not in documents
- **More complete answers**: Likely to provide fuller responses
- **General knowledge usage**: May supplement with common retail knowledge
- **Less strict grounding**: May make more inferences

**Use Cases**:
- When completeness is prioritized over strict accuracy
- When studying how general knowledge affects responses
- When you want to see maximum information extraction

**Example Response Style**:
> "Based on the policy documents [Source: ReturnPolicy.txt], Micro Center allows returns within 30 days. Generally, electronics retailers also require items to be in original packaging, though I'd recommend confirming specific requirements with customer service."

## Comparison Matrix

| Aspect | Strict | Balanced | Permissive |
|--------|--------|----------|------------|
| **Faithfulness** | Highest | Medium | Lower |
| **Hallucination Risk** | Lowest | Medium | Higher |
| **Answer Completeness** | Lower | Medium | Higher |
| **"I don't know" Frequency** | Highest | Medium | Lowest |
| **General Knowledge Usage** | None | None | Allowed |
| **Citation Strictness** | Very High | Medium | Flexible |
| **Use Case** | Critical accuracy | Production default | Completeness priority |

## API Usage

### Request Format

```json
POST /query
{
    "question": "What is the return policy?",
    "top_k": 5,
    "use_web_search": false,
    "prompt_template": "strict"  // or "balanced" or "permissive"
}
```

### Response Format

The response includes the template used:

```json
{
    "question": "What is the return policy?",
    "answer": "...",
    "citations": [...],
    "prompt_template": "strict",
    "retrieved_chunks": [...]
}
```

## Evaluation and Analysis

To compare templates:

1. **Run same questions with different templates**: Use identical questions across all three templates
2. **Measure faithfulness**: Use the `/evaluate` endpoint to calculate faithfulness scores
3. **Analyze responses**: Compare answer completeness, citation accuracy, and hallucination rates
4. **Track metrics**: Monitor average similarity scores, faithfulness scores, and response quality

### Example Evaluation Workflow

```python
questions = ["What is the return policy?", "How long is the warranty?"]

for template in ["strict", "balanced", "permissive"]:
    for question in questions:
        response = requests.post("/query", json={
            "question": question,
            "prompt_template": template
        })
        # Analyze and compare responses
```

## Recommendations

- **For production**: Use `balanced` (default) for general use
- **For critical accuracy**: Use `strict` when accuracy is paramount
- **For completeness**: Use `permissive` when you want maximum information extraction
- **For research**: Test all three to understand hallucination patterns

## Future Enhancements

Potential improvements:
- Template-specific similarity thresholds
- Automatic template selection based on query type
- Hybrid templates combining approaches
- Template performance metrics tracking

