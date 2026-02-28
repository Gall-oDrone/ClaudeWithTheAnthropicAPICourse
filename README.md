# Claude with the Anthropic API Course Notebooks

This repository contains Jupyter notebooks that accompany the [Claude with the Anthropic API course](https://anthropic.skilljar.com/claude-with-the-anthropic-api) from Anthropic Academy.

## 📚 Course Overview

This comprehensive course teaches developers how to integrate Claude AI into applications using the Anthropic API. The curriculum covers:

- **Fundamental API operations** - Authentication, request configuration, and basic interactions
- **Advanced prompting techniques** - System prompts, temperature control, structured outputs
- **Tool integration** - Custom tools, batch operations, web search capabilities
- **Retrieval Augmented Generation (RAG)** - Text chunking, embeddings, search, and contextual retrieval
- **Extended features** - Image analysis, PDF processing, citations, and prompt caching
- **Model Context Protocol (MCP)** - Standardized tool and resource integration
- **Anthropic Apps** - Claude Code and Computer Use for automation
- **Agent-based systems** - Parallelization, chaining, and routing workflows

## 🎯 What You'll Learn

- Set up and authenticate with the Anthropic API
- Implement single and multi-turn conversations
- Configure system prompts and control model behavior
- Design prompt evaluation workflows
- Apply advanced prompt engineering techniques
- Integrate Claude's tool use capabilities
- Build RAG systems with text chunking and embeddings
- Utilize Claude's multimodal capabilities
- Implement prompt caching strategies
- Develop MCP servers and clients
- Deploy Anthropic Apps
- Architect agent-based systems

## 📋 Prerequisites

- Proficiency in Python programming
- Basic knowledge of handling JSON data
- Access to the [Anthropic API](https://console.anthropic.com/)

## 🚀 Getting Started

1. **Clone this repository:**
   ```bash
   git clone https://github.com/yourusername/claude-anthropic-api-course.git
   cd claude-anthropic-api-course
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API key:**
   - Get your API key from [Anthropic Console](https://console.anthropic.com/)
   - Create a `.env` file in the root directory
   - Add your API key: `ANTHROPIC_API_KEY=your_api_key_here`

4. **Start Jupyter:**
   ```bash
   jupyter notebook
   ```

## 📁 Notebook Structure

- `001_requests.ipynb` - Basic API requests and authentication
- *(More notebooks will be added as the course progresses)*

## 🆕 New Features: Format Grading System

The repository now includes a comprehensive **Format Grading System** that implements the format grading criteria outlined in the Anthropic API course curriculum. This system provides:

### Format Validation Capabilities
- **JSON**: Syntax validation, schema validation, required/forbidden field checking
- **XML**: Structure validation, required section checking, tag balancing
- **Markdown**: Header validation, content structure, code block requirements
- **CSV**: Column validation, data consistency, required field checking
- **YAML**: Format validation, field requirements, structure checking

### Key Features
- **Automatic Format Detection**: Intelligently detects expected output format from prompts
- **Schema Validation**: JSON schema validation for complex data structures
- **Content Validation**: Ensures required elements are present and forbidden elements are absent
- **Integration**: Seamlessly integrates with existing code and model grading systems
- **Batch Processing**: Supports batch evaluation with format-specific criteria
- **Comprehensive Reporting**: Detailed feedback and scoring for format compliance

### Usage Examples
```python
from utils.graders import FormatGrader, FormatGradingCriteria

# Set up format criteria
criteria = FormatGradingCriteria(
    required_format="json",
    required_fields=["name", "age", "email"],
    forbidden_fields=["password"]
)

# Create grader and validate
grader = FormatGrader(criteria)
result = grader.grade(json_output, "json")
```

See `examples/format_grading_example.py` for comprehensive usage examples.

## 🆕 Prompt Eval Integrations (from Notebook Workflows)

Integrations inspired by the prompt-engineering notebook (`notebooks/prompt_engineering_tecniques/002_prompting_completed.ipynb`) are available in the project:

### Template renderer (`utils/shared_utils.py`)
- **`TemplateRenderer.render(template_string, variables)`** – Substitute `{key}` placeholders; use `{{` and `}}` for literal braces. Useful for building prompts from multiple inputs.

### Rubric grading with mandatory criteria (`utils/graders.py`, `prompts/grading_prompts.py`)
- **`ModelGrader.grade_with_rubric(...)`** – Grade using an explicit criteria list and optional **mandatory criteria** (any violation → score ≤ 3).
- **`Grader.grade_comprehensive(..., solution_criteria=..., mandatory_criteria=...)`** – When `solution_criteria` is provided, model grading uses rubric mode with optional mandatory requirements.
- Prompt constant: `RUBRIC_GRADING_PROMPT` in `prompts/grading_prompts.py`.

### HTML evaluation report (`utils/report.py`)
- **`generate_evaluation_report(eval_summary, output_path=None, title=..., pass_threshold=7.0)`** – Builds an HTML report from evaluator results: summary stats (total tests, average score, pass rate) and a table (scenario, prompt/inputs, criteria, output, score, reasoning). Supports both simple and parameterized test cases.

### Parameterized test cases (`utils/evaluator.py`)
- Test cases can use **`prompt_template`** and **`prompt_inputs`** (dict); the evaluator resolves the prompt with `TemplateRenderer`. Optional **`scenario`** for display; **`solution_criteria`** and **`mandatory_criteria`** are passed to the grader for rubric grading.

### Concurrency and progress (`utils/evaluator.py`)
- **`run_eval(..., max_workers=1, html_report_path=None, progress_milestone_percent=20)`** – Optional parallel runs (`max_workers > 1`), HTML report generation to a file, and progress logging at configurable milestones.

### Running tests
```bash
# Run integration tests (template renderer, report, evaluator options; some tests skip without anthropic)
python3 -m pytest tests/test_template_renderer.py tests/test_report.py tests/test_integrations.py -v

# Run shared-utils tests (includes TemplateRenderer)
PYTHONPATH=. python3 tests/test_shared_utils.py
```

## 🔧 Course Modules

### 1. Accessing Claude with the API
- Getting an API key
- Making requests
- Multi-turn conversations
- System prompts
- Temperature control
- Response streaming
- Structured data

### 2. Prompt Evaluation
- Evaluation workflows
- Test dataset generation
- Model-based grading
- Code-based grading
- **Format-based grading** (NEW!)
  - JSON/XML/Markdown/CSV/YAML validation
  - Schema validation
  - Required/forbidden field checking
  - Structure and content validation

### 3. Prompt Engineering Techniques
- Clear and direct communication
- Specific instructions
- XML tag structuring
- Example-based learning

### 4. Tool Use with Claude
- Tool functions and schemas
- Message block handling
- Multi-turn conversations with tools
- Batch operations
- Web search integration

### 5. Retrieval Augmented Generation (RAG)
- Text chunking strategies
- Text embeddings
- BM25 lexical search
- Multi-index pipelines
- Contextual retrieval

### 6. Advanced Features
- Extended thinking mode
- Image and PDF support
- Citations
- Prompt caching
- Code execution and Files API

### 7. Model Context Protocol (MCP)
- MCP clients and servers
- Tool and resource definitions
- Server inspection
- Prompt management

### 8. Anthropic Apps
- Claude Code setup and usage
- Computer Use for UI automation
- MCP server enhancements
- Automated debugging

### 9. Agents and Workflows
- Parallelization workflows
- Chaining workflows
- Routing workflows
- Environment inspection

## 🛠️ Development

This repository is designed to be used alongside the video course. Each notebook corresponds to specific lessons and exercises from the course curriculum.

## 📝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements or corrections.

## 📄 License

This project is for educational purposes. Please refer to Anthropic's terms of service for API usage.

## 🔗 Resources

- [Course Link](https://anthropic.skilljar.com/claude-with-the-anthropic-api)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Anthropic Console](https://console.anthropic.com/)
- [Anthropic Academy](https://academy.anthropic.com/)

## 🙏 Acknowledgments

- [Anthropic](https://www.anthropic.com/) for providing the comprehensive course
- The course instructors and content creators
- The open-source community for various tools and libraries used in the examples

---

**Note:** This repository is designed to complement the official course materials. Please ensure you have proper access to the course content through Anthropic Academy.
