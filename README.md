# text-to-sql

# 🧠 Transformers Final Project: Natural Language to SQL/Cypher

This project explores two approaches for converting natural language questions into structured queries (SQL/Cypher) using large language models (LLMs). Inspired by real-world applications like Uber's **QueryGPT**, we evaluate both **few-shot prompting** and **fine-tuning** techniques on the **BirdSQL** dataset.

---

## 🔍 Motivation

Inspired by Uber’s [QueryGPT](https://www.uber.com/blog/query-gpt/), our project explores the effectiveness of prompting strategies and fine-tuning for translating natural language into structured queries.

Uber showed that:
- **LLMs can bridge the gap** between business users and data via natural language
- Even **smaller LLMs**, with proper prompting, can match the performance of larger models
- **Execution accuracy** and **semantic correctness** are key metrics when evaluating generated queries

Our goal is to reproduce and extend this idea using open-source tools and publicly available benchmarks.

> 🧠 We used the [BirdSQL](http://bird-bench.github.io/) dataset — a modern benchmark designed to test LLM capabilities in translating natural language to SQL. It contains diverse schemas and complex questions, ideal for robust evaluation.

---

## 🎯 Project Objective

Convert questions like  
> _"How many students are enrolled in the Math department?"_  
into structured queries like  
> `SELECT COUNT(*) FROM students WHERE department = 'Math';`

We evaluate how well LLMs perform this task using two methods:
1. Fine-tuning the model
2. Few-shot prompting with examples

---

## 🧪 Approaches Compared

### 1. Fine-Tuning an LLM  
Train a pre-trained transformer model (e.g., T5, GPT) on a labeled dataset (like BirdSQL) with natural language questions and matching SQL queries.

- ✅ High accuracy potential  
- ⚠️ Requires significant GPU time and data

### 2. Few-shot Learning (Prompt Engineering)  
Provide a few examples in the prompt (in-context learning) and let the LLM generalize.

- ✅ Fast, no training required  
- ⚠️ Prompt quality heavily influences performance

---

## 🧩 Project Pipeline

### Step 0: Data Preparation  

**Function 1 – Extract Schema**  
- Load SQLite database  
- Extract all table names and `CREATE TABLE` statements  
- Output: Dictionary mapping table names → schema

**Function 2 – Format Schema for Prompting**  
- Generate a readable schema block for prompting:  
  _“Here are the tables in the database:”_ followed by table structures  
- Add model instructions

**Function 3 – Prepare Training/Dev Examples**  
- Load dataset (e.g., `train.json`)  
- For each example:  
  - Add schema context  
  - Add question, hint (if any), and expected SQL query  
- Return as a pandas DataFrame

---

### Step 1: Prompt-Based Inference

#### 🔹 Zero-shot Prompting
- For each dev example:
  - Use schema + question only (no examples)
  - Pass to the LLM
  - Store result in `zero_shot` column

#### 🔹 Few-shot Prompting
- Sample 2 examples from training set
- Format each example as:  
  `Q: <question>\nA: <SQL>`  
- Combine with schema + current question  
- Pass to LLM
- Store result in `few_shot` column

→ Save all dev set predictions (zero-shot and few-shot) to CSV

---

### Step 2: Fine-Tuning with Schema

- Input: `[schema + question]`  
- Output: `SQL query`  
- Train on BirdSQL training set, evaluate on dev set  
- If a generated query causes an error:
  - Prompt the LLM again with `[schema + original query + error message]`
  - Ask it to correct the SQL

---

### Step 3: Evaluation Metrics

#### ✅ Execution Accuracy  
- % of queries that run successfully (no syntax/runtime errors)

#### 🎯 Output Accuracy  
- % of generated queries that exactly match the gold SQL query  
- If output is 100% accurate, execution is guaranteed correct

---

## 📊 Example Prompt (Few-shot)
