
# WARNING: This file (`science.py`) is meant for research purposes ONLY, don't deploy it.

import re
import json
import random
import datetime
from transformers import pipeline

llm = pipeline('text-generation', model='EleutherAI/gpt-neo-2.7B', device=0)

prompt_fragments_control = [
	"<Guest> What are you?\n<AI> I'm a science project.\n",
	"<Guest> How many people are on earth?\n<AI> The Earth has [SEARCH(earth population) -> 7.888 billion (2021)] 7.888 billion inhabitants as of 2021.\n",
	"<Guest> What day is it?\n<AI> Today's date is [DATE() -> Feb 20th, 2023] February 20th, 2023.\n",
]
prompt_fragments_experiment = [
	"<Guest> What is 123 + 456?\n<AI> 123 + 456 is [MATH(123 + 456) -> 579] 579.\n",
	"<Guest> What is 123 * 456?\n<AI> 123 * 456 is [MATH(123 * 456) -> 56088] 56088.\n",
	"<Guest> What is 123 ^ 456?\n<AI> 123 ^ 456 is [MATH(123 ^ 456) -> 435] 435.\n",
	"<Guest> What is 123 & 456?\n<AI> 123 & 456 is [MATH(123 & 456) -> 72] 72.\n",
	"<Guest> What is 123 - 456?\n<AI> 123 - 456 is [MATH(123 - 456) -> -333] -333.\n",
]

def do_plugin(name, arg):
	if name == "MATH":
		try:
			bad = str(eval(arg)) # lol surely nothing can go wrong
		except:
			bad = None
		return bad

	if name == "SEARCH":
		if (arg == "earth population") or (arg == "world population"):
			return "7.888 billion (2021)"
		if (arg == "best pony"):
			return "Starlight Glimmer"

	if name == "DATE":
		return datetime.datetime.now().strftime("%b %-d, %Y")

	return None

def parse_plugin(text):
	if "[" not in text: return None
	if "(" not in text: return None
	if ")" not in text: return None
	lb = text.index("[")
	lp = text.index("(")
	rp = text.index(")")
	if (lb > lp) or (lp > rp): return None
	name = text[lb+1:lp].strip()
	arg = text[lp+1:rp].strip()
	res = do_plugin(name, arg)
	if res is None: return None
	if res != "":
		res = " -> " + res
	return text[:lb] + "[%s(%s)%s]" % (name, arg, res)

passed = {}
failed = {}
result = [{} for i in range(len(prompt_fragments_experiment)+1)]
ops = ["+", "*", "-", "^", "&", "|"]

for i in range(1000):
	print("\nTrial %d:" % i)
	for N in range(len(result)):
		prompt_fragments = prompt_fragments_experiment[:N] + prompt_fragments_control
		for op in ops:
			a = random.randint(0, 100)
			b = random.randint(0, 100)

			if op == "+": c = a + b
			if op == "-": c = a - b
			if op == "*": c = a * b
			if op == "^": c = a ^ b
			if op == "&": c = a & b
			if op == "|": c = a | b
			
			query = "What is %d %s %d?" % (a, op, b)
			random.shuffle(prompt_fragments)
			prompt = "".join(prompt_fragments)
			context = prompt + "<Guest> %s\n<AI>" % (query)

			response = ""
			while True:
				output = llm(context, max_new_tokens=16, pad_token_id=50256, num_return_sequences=1)[0]["generated_text"]
				output = output[len(context):]
				if "\n" in output: output = output[:output.index("\n")]
				plugin_output = parse_plugin(output)
				if plugin_output is None:
					response += output
					break
				response += plugin_output
				context += plugin_output

			answer = response.strip().replace(".", " ").replace("=", " ").replace("->", " ").replace("]", " ").replace("  ", " ").replace("  ", " ").strip().split(" ")[-1]
			try:
				answer = int(answer)
			except:
				answer = 0

			tag = "N=%d OP=%s" % (N, op)
			if tag not in passed: passed[tag] = 0
			if tag not in failed: failed[tag] = 0
			if answer == c:
				passed[tag] += 1
			else:
				failed[tag] += 1
			print("%s: '%s' => '%s'" % ("PASS" if (answer == c) else "FAIL", query, response))
			result[N][op] = 100.0 * passed[tag] / (passed[tag] + failed[tag])

	lines = ["| %s |"%op for op in ops]
	for j in range(len(ops)):
		for k in range(len(result)):
			lines[j] += " %.01f%% |" % result[k][ops[j]]
	print("\n".join(lines))
