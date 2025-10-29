# 🤖 AI Features - GitHub Models Integration

## Overview

Aurora CloudBank leverages GitHub Models to provide intelligent, AI-powered development workflows. Our AI features are built using production-ready prompts that integrate seamlessly with the repository's development process.

---

## 🎯 AI Pull Request Summarizer

### Feature Description

The **AI Pull Request Summarizer** is a high-value AI feature that automatically generates comprehensive, actionable summaries of pull requests by analyzing code changes, commit messages, and PR metadata.

### Key Benefits

- **Time Savings**: Reduces reviewer time by providing instant, structured PR summaries
- **Consistency**: Ensures all PRs have standardized, professional summaries
- **Improved Code Review**: Highlights key changes, impacts, and areas requiring attention
- **Better Documentation**: Creates permanent, searchable records of what each PR accomplishes

### Technical Implementation

**Model**: OpenAI GPT-4.1  
**Prompt File**: [`ai_pr_summarizer.prompt.yml`](https://github.com/AUo959/aurora-cloudbank-symbolic/blob/main/ai_pr_summarizer.prompt.yml)  
**Temperature**: 0.3 (optimized for consistent, deterministic outputs)

### How It Works

The AI PR Summarizer analyzes multiple dimensions of a pull request:

1. **PR Title & Description** - Understanding the stated intent
2. **Commit Messages** - Tracking the development narrative
3. **Files Changed** - Identifying affected components
4. **Code Diffs** - Analyzing actual technical modifications
5. **Impact Assessment** - Evaluating effects on architecture, performance, and functionality

### Output Format

The AI generates structured summaries with the following sections:

#### **Summary**
A concise 1-2 sentence overview of the PR's purpose and accomplishments.

#### **Key Changes**
3-5 bullet points highlighting the main technical modifications.

#### **Impact**
Description of how the changes affect the codebase (performance, architecture, functionality).

#### **Review Focus**
Specific areas and considerations that reviewers should pay close attention to.

#### **Testing**
Testing requirements and considerations for validating the changes.

---

## 📋 Using the AI PR Summarizer

### Option 1: GitHub Models Playground

1. Navigate to the [Models](https://github.com/AUo959/aurora-cloudbank-symbolic/models) section
2. Open the `ai_pr_summarizer.prompt.yml` prompt
3. Fill in the required variables:
   - `{{pr_title}}` - The pull request title
   - `{{pr_description}}` - The PR description text
   - `{{commit_messages}}` - List of commit messages
   - `{{files_changed}}` - List of modified files
   - `{{diff_content}}` - Summary of the code changes
4. Click "Run" to generate the summary
5. Copy the generated summary and add it to your PR description

### Option 2: API Integration

You can integrate the AI PR Summarizer into your CI/CD pipeline using the GitHub Models API:

```python
import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

# Initialize client
endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1"
token = os.environ["GITHUB_TOKEN"]

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token)
)

# Load prompt from the repository
system_prompt = """You are an expert code reviewer and technical writer..."""
user_prompt = f"""Analyze this Pull Request and provide a comprehensive summary:

**PR Title**: {pr_title}
**PR Description**: {pr_description}
**Commit Messages**: {commit_messages}
**Files Changed**: {files_changed}
**Diff Summary**: {diff_content}
"""

# Generate summary
response = client.complete(
    messages=[
        SystemMessage(system_prompt),
        UserMessage(user_prompt)
    ],
    temperature=0.3,
    model=model
)

ai_summary = response.choices[0].message.content
print(ai_summary)
```

### Option 3: GitHub Actions Workflow

Create a workflow file `.github/workflows/ai_pr_summary.yml`:

```yaml
name: AI PR Summary Generator

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  generate-summary:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Generate AI Summary
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # Extract PR details
          # Call GitHub Models API with ai_pr_summarizer prompt
          # Post summary as PR comment
          echo "AI Summary generation workflow"
```

---

## 🔧 Best Practices

### For PR Authors

1. **Provide Context**: Write clear PR titles and descriptions to help the AI understand intent
2. **Meaningful Commits**: Use descriptive commit messages that explain the "why" behind changes
3. **Review AI Output**: Always review and refine AI-generated summaries before finalizing
4. **Update as Needed**: Regenerate summaries when significant changes are made to the PR

### For Reviewers

1. **Use as Starting Point**: Treat AI summaries as helpful context, not replacement for thorough review
2. **Verify Claims**: Cross-check AI assessments against actual code changes
3. **Provide Feedback**: If AI summaries are inaccurate, note what was missed for future improvements

### For Repository Maintainers

1. **Standardize Usage**: Encourage consistent use of AI summaries across all PRs
2. **Monitor Quality**: Regularly review AI-generated summaries for accuracy and usefulness
3. **Iterate on Prompts**: Update the prompt based on team feedback and evolving needs
4. **Track Metrics**: Measure time savings and review quality improvements

---

## 🚀 Future AI Features

The AI PR Summarizer is the first of many AI-powered features planned for Aurora CloudBank:

- **AI Code Review Assistant**: Automated code quality analysis and suggestions
- **AI Documentation Generator**: Automatic generation of API documentation
- **AI Test Case Suggester**: Intelligent test case recommendations based on code changes
- **AI Dependency Analyzer**: Impact analysis for dependency updates
- **AI Security Scanner**: Proactive security vulnerability detection

---

## 📚 Additional Resources

- [GitHub Models Documentation](https://docs.github.com/github-models/about-github-models)
- [OpenAI GPT-4.1 Model Card](https://github.com/marketplace/models/catalog)
- [Prompt Engineering Best Practices](https://docs.github.com/github-models/use-github-models/storing-prompts-in-github-repositories)
- [Azure AI Inference SDK](https://learn.microsoft.com/azure/ai-studio/)

---

## 💡 Contributing

Have ideas for improving the AI PR Summarizer or suggestions for new AI features? We welcome contributions!

1. Review the [Contributing Guidelines](CONTRIBUTING.md)
2. Open an issue to discuss your proposed changes
3. Submit a PR with prompt improvements or new features
4. Share your usage experiences and feedback

---

**Built with ❤️ using GitHub Models**
