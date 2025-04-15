# Text-to-SQL

This project explores two approaches for converting natural language questions into structured queries (SQL) using large language models (LLMs). Inspired by real-world applications like Uber's QueryGPT, we want to see if prompting and fine-tuning techniques via smaller models such as Llama 3.2 on the BirdSQL dataset can acheieve comparable results.

---

## Motivation

Inspired by Uber’s [QueryGPT](https://www.uber.com/blog/query-gpt/), our project explores the effectiveness of prompting strategies and fine-tuning for translating natural language into structured queries.

Uber demonstrated that:
- LLMs can help bridge the gap between business users and structured databases
- Smaller LLMs, with effective prompting, can perform similarly to larger models
- Execution accuracy and semantic correctness are key metrics for evaluating query generation

Our goal is to replicate and extend these ideas using open-source tools and benchmarks. We use OLLAMA for our project. We used OLLAMA locally to use LLama 3.2 for this project.

We use the [BirdSQL](http://bird-bench.github.io/) dataset — a modern benchmark designed to test the ability of LLMs to generate SQL across a variety of schemas and complex questions.

---

## Project Objective

Convert questions such as:  
"How many students are enrolled in the Math department?"  

Into valid SQL queries such as:  
`SELECT COUNT(*) FROM students WHERE department = 'Math';`

We compare two methods for accomplishing this:
1. Fine-tuning an LLM on schema-aware data 
2. Prompting, both zero and few-shot, using schema and example queries

---

## Approaches Compared

### Fine-Tuning
We train a pre-trained transformer model (e.g., T5 or GPT) on a labeled dataset with schema, natural language questions, and SQL queries.

- Pros: High potential for accuracy and generalization
- Cons: Requires significant compute resources and time

### Few-shot Prompting
We provide a few labeled examples directly in the prompt and rely on the LLM's in-context learning capabilities.

- Pros: No training required, quick to test and iterate
- Cons: Highly dependent on prompt quality and structure

---

## Project Pipeline

### Step 0: Data Preparation

**Schema Extraction**
- Load a SQLite database
- Extract table names and their `CREATE TABLE` statements
- Store them in a dictionary format: `{table_name: CREATE statement}`

**Prompt Formatting**
- Convert the schema dictionary into a readable text prompt
- Include instructions like “Here are the tables in the database” followed by each table's schema

**Example Construction**
- Load a dataset such as `train.json`
- For each example:
  - Add schema context
  - Include the natural language question, optional hint, and correct SQL query
- Return as a pandas DataFrame

---

### Step 1: Prompt-Based Inference

**Zero-shot Prompting**
- Use schema + question only (no examples)
- Pass to LLM and store the output in a `zero_shot` column

**Few-shot Prompting**
- Randomly select two examples from the training set
- Format each as a question-answer pair
- Combine them with schema + current question
- Pass to LLM and store the output in a `few_shot` column

All predictions are saved to a CSV file for later analysis.

---

### Step 2: Fine-Tuning

- Input: schema + question
- Output: SQL query
- Train the model on the BirdSQL training set and evaluate on the dev set
- For queries that result in errors, prompt the LLM with the schema, the incorrect query, and the error message, and ask it to generate a corrected version

---

### Step 3: Evaluation Metrics

**Execution Accuracy**
- Percentage of generated queries that run without syntax or runtime errors

**Output Accuracy**
- Percentage of generated queries that exactly match the gold (expected) SQL queries

Note: If a generated query exactly matches the gold query, it is guaranteed to execute correctly.

---

## Example Few-shot Prompt

