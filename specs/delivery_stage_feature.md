# Feature: Delivery Stage

## Goal
Add a Delivery capability that sends the Writer's outbound message to configured delivery providers.
Telegram is the first delivery provider.
Delivery should run only after the configured pipeline stages complete successfully.

## Background
The Planner currently runs configured stages in order.
When the Writer is the final successful stage, the Writer output becomes the final outbound message.
The command-line entry point currently prints the final successful output to stdout.
The Delivery capability should use the Writer's outbound message as its input and send it to enabled delivery providers.
Delivery is not a content-producing stage.
Delivery is a side-effect step that occurs after successful message generation.

## Scope
Implement delivery handling for the existing pipeline.
Update or add behavior for:
- pipeline configuration delivery section
- Planner delivery coordination
- Telegram delivery provider
- delivery result reporting
- ledger delivery records
- tests for configured delivery behavior
- documentation describing the delivery flow

## Requirements

### Delivery Configuration
Pipeline configuration may define a top-level delivery section.
The delivery section defines one or more delivery providers.
Each delivery provider has a provider name and an enabled flag.
Only enabled delivery providers participate in a pipeline run.
Telegram is the only required delivery provider for this feature.
A minimal delivery configuration may look like:

    delivery:
      - provider: telegram
        enabled: true

### Delivery Timing
Delivery must run only after all configured stages complete successfully.
Delivery must receive the final outbound message produced by the Writer.
Delivery must not run if any configured pipeline stage fails validation or raises an error.
Delivery must not run before the Writer produces a valid outbound message.

### Delivery Responsibility
Delivery providers are responsible for transporting an outbound message.
Delivery providers must not generate, edit, rank, filter, or summarize content.
Delivery providers must not change the Writer output.

### Telegram Delivery Provider
The Telegram delivery provider sends the outbound message to the configured Telegram destination.
Telegram delivery must use existing Telegram configuration values from the project environment configuration.
Telegram delivery must report success or failure.
Telegram delivery must not perform Writer formatting.
Telegram delivery must not perform Curator filtering.

### Planner Behavior
The Planner remains responsible for coordinating pipeline execution.
The Planner runs configured stages first.
If all stages succeed, the Planner passes the final outbound message to enabled delivery providers.
The Planner records delivery results separately from stage results.
The final Writer outbound message should remain available as the successful run output.

### Command-Line Behavior
Successful command-line execution should still print the final outbound message to stdout.
Delivery success should not replace the outbound message as stdout output.
On stage failure, stdout should remain empty and the failure reason should be printed to stderr.
On delivery failure, the failure should be reported clearly without implying that Writer generation failed.

### Ledger Behavior
The ledger should continue recording stage results under the stages section.
Delivery results should be recorded separately from stage results.
Delivery should not be represented as a normal pipeline stage.
A successful delivery record should identify the provider and report that delivery succeeded.
A failed delivery record should identify the provider and report the failure reason.
The Writer output should remain recorded as the Writer stage output.

### Delivery Failure Behavior
Delivery failures should be reported independently from message generation.
A delivery failure should not rewrite the Writer stage result as failed.
If a delivery provider fails, the run result should make the delivery failure observable.
If multiple delivery providers are configured in the future, one provider's failure should be attributable to that provider.

### Tests
Tests should cover observable delivery behavior.
Tests should verify that delivery runs after Writer success.
Tests should verify that delivery does not run when a pipeline stage fails.
Tests should verify that the final outbound message remains the run output.
Tests should verify that delivery results are recorded separately from stage results.
Tests should verify that disabled delivery providers do not run.
Tests should not require live Telegram calls.

## Non-Goals
- Supporting delivery providers other than Telegram
- Supporting multiple active delivery providers beyond the configuration shape
- Adding retry behavior
- Adding delivery scheduling behavior
- Changing Writer output format
- Changing Curator behavior
- Changing Researcher behavior
- Making Delivery a normal configured pipeline stage
- Replacing stdout output with delivery status
- Requiring live Telegram calls during unit tests

## Acceptance Criteria
A reviewer can observe that:
- The pipeline can configure Telegram delivery separately from stages.
- Delivery runs only after successful Writer output generation.
- Delivery receives the Writer outbound message.
- Delivery does not modify the outbound message.
- Delivery results are recorded separately from stage results in the ledger.
- The final Writer outbound message remains the successful run output.
- Stage failures prevent delivery from running.
- Disabled delivery providers do not run.
- Telegram-specific behavior is isolated to Telegram delivery.
- Existing pipeline stage behavior remains unchanged.
- Tests pass without live Telegram calls.

## Rationale
The Writer is responsible for generating an outbound message.
Delivery is responsible for transporting the outbound message.
Separating Delivery from normal pipeline stages keeps content generation independent from message transport.
Recording delivery results separately from stage results makes it clear whether a failure occurred during message generation or message delivery.

## Completion
When implementation is complete, append a build log entry to eval_log.md following the format in AGENTS.md
