import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

# List 10 fine-tuning jobs
openai.FineTuningJob.list(limit=10)

# Retrieve the state of a fine-tune
openai.FineTuningJob.retrieve("ftjob-abc123")

# Cancel a job
openai.FineTuningJob.cancel("ftjob-abc123")

# List up to 10 events from a fine-tuning job
openai.FineTuningJob.list_events(id="ftjob-abc123", limit=10)

# Delete a fine-tuned model (must be an owner of the org the model was created in)
openai.Model.delete("ft:gpt-3.5-turbo:acemeco:suffix:abc123")