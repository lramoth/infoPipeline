# Eval: Structured Model Response Tolerance

Purpose  
Validate the observable behavior described in `specs/model_response_tolerance_feature.md`.

Do not grade implementation details such as:
- class names
- method names
- helper modules
- parsing algorithms
- validation-result shapes
- internal data structures.

Grade only observable behavior.  
Do not infer requirements that are not stated in the specification.

## Evaluation Environment

Unless explicitly required by the spec:
- Do not perform live Gemini, Ollama, Telegram, or other external API calls.
- Do not perform additional web searches.
- Do not retry model requests.
- Do not modify external systems.
- Use mocks, fixtures, or controlled test inputs.

## Scenario 1: Direct Researcher Structured Response
Given the Researcher receives a model response containing direct valid structured research data,
When the Researcher processes the response,
Then:
- the Researcher succeeds
- the returned output contains the structured research items
- existing Researcher validation still passes

## Scenario 2: Markdown-Wrapped Researcher Structured Response
Given the Researcher receives a model response containing valid structured research data inside Markdown code-fence formatting,
When the Researcher processes the response,
Then:
- the Researcher succeeds
- the returned output contains the extracted structured research items
- existing Researcher validation still passes

## Scenario 3: Explanatory Researcher Structured Response
Given the Researcher receives a model response containing valid structured research data surrounded by non-structured explanatory text,
When the Researcher processes the response,
Then:
- the Researcher succeeds
- the returned output contains the extracted structured research items
- existing Researcher validation still passes

## Scenario 4: Direct Curator Structured Response
Given the Curator receives a model response containing direct valid structured curated data,
When the Curator processes the response,
Then:
- the Curator succeeds
- the returned output contains the structured curated items
- existing Curator validation still passes

## Scenario 5: Markdown-Wrapped Curator Structured Response
Given the Curator receives a model response containing valid structured curated data inside Markdown code-fence formatting,
When the Curator processes the response,
Then:
- the Curator succeeds
- the returned output contains the extracted structured curated items
- existing Curator validation still passes

## Scenario 6: Explanatory Curator Structured Response
Given the Curator receives a model response containing valid structured curated data surrounded by non-structured explanatory text,
When the Curator processes the response,
Then:
- the Curator succeeds
- the returned output contains the extracted structured curated items
- existing Curator validation still passes

## Scenario 7: No Valid Structured Data
Given a structured-output stage receives a model response containing only human-readable explanation and no valid structured payload,
When the stage processes the response,
Then:
- the stage fails
- a readable failure reason is reported

## Scenario 8: Malformed Structured Data
Given a structured-output stage receives a model response containing incomplete or malformed structured data,
When the stage processes the response,
Then:
- the stage fails
- a readable failure reason is reported

## Scenario 9: Extracted Data Fails Existing Validation
Given a structured-output stage receives a model response containing extractable structured data,
When the extracted data violates that stage’s existing validation rules,
Then:
- the stage fails validation
- the failure reflects the existing stage validation requirement
- later pipeline stages are not run when evaluated through the Planner

## Scenario 10: Existing Planner Behavior
Given the Planner runs a pipeline where Researcher or Curator receives wrapped but valid structured model output,
When the wrapped structured output passes existing stage validation,
Then:
- the Planner records the stage as successful
- the Planner continues to the next stage
- Planner ordering and failure handling remain otherwise unchanged

## Grading instructions
For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.
Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
