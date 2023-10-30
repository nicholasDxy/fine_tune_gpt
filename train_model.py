import os
import openai
import jsonlines
import tiktoken 
import datetime
# messages = []
# with open("train_data.jsonl", "r+", encoding="utf8") as f:
#     for item in jsonlines.Reader(f):
#         msg_list = item["messages"]
#         messages.append(msg_list)


openai.api_key = os.getenv("OPENAI_API_KEY")

# upload the training data.
# openai.File.create(
#   file=open("train_data.jsonl", "rb"),
#   purpose='fine-tune'
# )

#check the files uploaded
response = openai.File.list()

for file in response['data']:
    created_at = datetime.datetime.fromtimestamp(file['created_at']).strftime('%Y-%m-%d %H:%M:%S')
    print(f"File ID: {file['id']}, Filename: {file['filename']}, Created at: {created_at}")

print(openai.Model.list())
# train model
# openai.FineTuningJob.create(training_file="file-exNqzLQ2MD5bsnMO8W9ItR9a", model="gpt-3.5-turbo")
