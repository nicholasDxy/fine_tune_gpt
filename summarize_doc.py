import os
import openai
import jsonlines
import tiktoken 
import datetime
import jsonlines
import time

openai.api_key = os.getenv("OPENAI_API_KEY")

doc_list = []

with open("data/doc_info.jsonl", "r+", encoding="utf8") as f:
    for item in jsonlines.Reader(f):
        doc_list.append(item)
        # print(item['title'])

# print(doc_list[0]['content'])


for item in doc_list:
  completion = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "As a helpful assistant, your job is to summarize a student's personal experience essay using simple language and a first-person perspective. You will be given the essay and must provide a concise and clear summary from the author's point of view. Your summary should use the word \"I\" to reflect the author's perspective."},
    {"role": "user", "content": item['content']}
  ])
  content = completion.choices[0].message['content']
  print(content)
  item['summary'] = content
  print('------------------')
  time.sleep(60)

with jsonlines.open('data/summary_info.jsonl',mode='a') as writer:
    for item in doc_list:
        writer.write(item)