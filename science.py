
# WARNING: This file (`science.py`) is meant for research purposes ONLY, don't deploy it.

import re
import random
import datetime
from transformers import pipeline

prompt_fragments = [
	"<Guest> What is 123 + 456?\n<AI> 123 + 456 is [MATH(123 + 456) -> 579] 579.\n"
	"<Guest> What is 123 * 456?\n<AI> 123 * 456 is [MATH(123 * 456) -> 56088] 56088.\n"
	"<Guest> What is 123 ^ 456?\n<AI> 123 ^ 456 is [MATH(123 ^ 456) -> 435] 435.\n"
	"<Guest> What are you?\n<AI> I am a chatbot.\n",
	"<Guest> How many people are on earth?\n<AI> The Earth has [SEARCH(earth population) -> 7.888 billion (2021)] 7.888 billion inhabitants as of 2021.\n"
	"<Guest> What day is it?\n<AI> Today's date is [DATE() -> Feb 20th, 2023] February 20th, 2023.\n",
]

llm = pipeline('text-generation', model='EleutherAI/gpt-neo-125M', device=0)

def do_plugin(name, arg):
	if name == "MATH":
		return str(eval(arg)) # lol surely nothing can go wrong

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

hits = {}
miss = {}
result = {}
for i in range(1000):
	print("\nTrial %d:" % i)
	for op in ["+", "*", "-", "^", "&", "|"]:
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

		answer = None
		if "]" in response:
			answer = response[response.index("]")+1:].strip()
			answer = re.sub("[^0-9]", "", answer)
			if answer == "": answer = 0
			answer = int(answer)

		if op not in hits: hits[op] = 0
		if op not in miss: miss[op] = 0
		if answer == c:
			hits[op] += 1
		else:
			miss[op] += 1
			print("Miss: '%s' => '%s'" % (query, response))

		result[op] = "Accuracy (%s): %.02f (%d / %d)" % (op, 100.0 * hits[op] / (hits[op] + miss[op]), hits[op], hits[op] + miss[op])
	for j in result:
		print(result[j])
