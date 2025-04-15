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

#### Performance Metrics
Query Authoring Time: Manual SQL queries at Uber typically take around 10 minutes to write. With QueryGPT, this time is reduced to approximately 3 minutes, representing a significant productivity gain. ​

User Adoption and Satisfaction: In a limited release to Operations and Support teams, about 300 daily active users reported that 78% of the generated queries reduced the time they would have spent writing queries from scratch. 

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

## Project Pipeline

### Step 0: Data Preparation

**Schema Extraction**
- Load a SQLite database
- Extract table names and their `CREATE TABLE` statements
- Store them in a dictionary format: `{table_name: CREATE statement}`

**Prompt Formatting**
- Convert the schema dictionary into a readable text prompt
- Include instructions and context like “Here are the tables in the database” followed by each table's schema.

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

#### Part 1: Training a Fine-tuned Language Model Using LoRA
The training and validation datasets (train_set.csv and dev_set.csv) are loaded. Each row contains a conversation, which includes a database schema, a natural language question, a hint, and the corresponding SQL query.

The script initializes the LLaMA 3.2B Instruct model using the Unsloth framework, with an option to load the model in 4-bit precision to optimize memory usage.

The model is prepared for fine-tuning using LoRA (Low-Rank Adaptation), which injects trainable adapter layers into key transformer components. This allows efficient fine-tuning without updating the full model.

A chat template is applied to format the training data as conversational text, matching the structure expected by the model. This helps align the model's behavior with typical dialogue-style prompts.

The processed dataset is passed to the SFTTrainer, which fine-tunes the model using supervised learning. Training parameters such as learning rate, batch size, number of epochs, and precision settings (fp16 or bf16) are specified using TrainingArguments.

Once training is complete, the fine-tuned model is used to generate predictions on the dev set. Each prompt (schema, question, and hint) is tokenized and passed to the model to produce a SQL output, which is then decoded and saved to a new file, dev_set_finetuned.csv.

Finally, the trained model is saved in GGUF format, making it suitable for further use or deployment.

#### Part 2: Evaluation and Query Rectification
The fine-tuned predictions are loaded and processed to extract:

The gold (ground truth) SQL query,

The model's predicted query,

The original schema included in the prompt.

Each predicted SQL query is executed against the database using a function run_query, which returns the result or an error if the query fails.

If the query fails to execute (e.g., due to syntax or schema errors), a rectification process is triggered:

A prompt is generated using the schema, the failed query, and the error message.

This prompt is passed to the language model again, asking it to correct the query.

If the model returns the fixed query within a code block (e.g., sql ... ), it is parsed accordingly.

The corrected query is then executed to verify if the issue is resolved.

Execution results from both the original and rectified queries are collected.

Finally, evaluation metrics such as output accuracy and error types are computed using helper functions like get_error_distribution and get_output_accuracy. This provides insights into the effectiveness of fine-tuning and the model’s ability to generate valid SQL.


---

Here’s a clear and structured explanation for **Step 3: Evaluation Metrics**, broken down into simple points:

---

### Step 3: Evaluating Model Performance Using Execution and Output Accuracy

#### Overview

In this step, the performance of all approaches—**Zero-shot**, **Few-shot**, **Fine-tuned**, and **Fine-tuned with self coreection**—is evaluated using two key metrics:

- **Execution Accuracy**: Measures how many SQL queries execute without errors on the database. This tells us if the generated SQL is syntactically and semantically valid.
- **Output Accuracy**: Measures how many generated SQL queries match exactly with the ground truth (`gold_query`). This evaluates correctness beyond just successful execution.

> Note: If a query is **100% correct (output accuracy)**, it will **always execute successfully** (100% execution accuracy). However, a query might execute without errors and still be logically wrong.

---

#### Part 1: Evaluating Zero-shot and Few-shot Predictions

1. The file `dev_set_zero_few_shot.csv` is loaded, which contains predictions from zero-shot and few-shot prompting.
2. For each row:
   - The gold SQL query is extracted.
   - The zero-shot and few-shot predictions are run on the corresponding database using `run_query`.
   - Results (either output or error) are stored for comparison.
3. Errors from each approach are categorized (e.g., syntax errors, column name errors) using `get_error_distribution`.
4. **Execution Accuracy** is calculated as:

**Execution Accuracy = (Number of Queries That Ran Without Errors / Total Queries) × 100**
   
   - Zero-shot Execution Accuracy: **51.04%**
   - Few-shot Execution Accuracy: **1.96%**
6. **Output Accuracy** is measured using `get_output_accuracy` by comparing the predicted query to the gold query.
   - Zero-shot Output Accuracy: **18.06%**
   - Few-shot Output Accuracy: **0.26%**

---

#### Part 2: Evaluating Fine-tuned Model Predictions

1. Predictions from the fine-tuned model are loaded from `dev_set_finetuned.csv`.
2. Each predicted and gold SQL query is executed against the corresponding database.
3. Errors are categorized and counted.
4. **Execution Accuracy**:
   - Fine-tuned Execution Accuracy: **73.27%**
5. **Output Accuracy**:
   - Fine-tuned Output Accuracy: **30.12%**

---

## Results Visualization

This section showcases visual comparisons to better understand the performance of different approaches—zero-shot, few-shot, and fine-tuning.

### Zero-Shot vs Few-Shot Accuracy

The chart below compares how the model performs when provided with no examples (zero-shot) versus when given a few in-context examples (few-shot). It helps highlight the challenges of using few-shot learning in complex tasks like SQL generation.

![Zero vs Few Shot Accuracy](figures/zero_vs_few_shot_accur.png)

---

### Execution Accuracy Across Approaches

This figure compares the **execution accuracy**, i.e., the percentage of SQL queries that ran without errors, across all three methods: zero-shot, few-shot, and fine-tuned. Higher execution accuracy indicates more syntactically and semantically correct SQL queries.

![Execution Accuracy](figures/execution_accuracy_comparison.png)

---

### Output Accuracy Across Approaches

Here we compare the **output accuracy**, which measures how many generated queries exactly match the gold-standard queries from the dataset. This metric reflects the true correctness of the model's output.

![Output Accuracy](figures/output_accuracy_comparison.png)

---

### Error Distribution in Finetuned Model

This chart shows a breakdown of different types of SQL execution errors (e.g., syntax, table not found, column errors) encountered by the fine-tuned model. Understanding these error types helps identify areas for model or data improvement.

![Finetuned Errors](figures/finetuned_error_distribution.png)

---

Let me know if you want to add more charts, rename the files for consistency, or generate captions automatically based on the image filenames.

