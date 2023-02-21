# Custom plugins for every chat AI, *without training*.
This open standard makes it fast and easy to make custom APIs and skills that any chat AI can use without training, and is quick and convenient to integrate into any chatbot that uses LLMs. (large language models, like GPT-3)

This is possible by using few-shot learning, and only requires adding a fragment to the prompt on-the-fly!

Advanced use cases like prompt/prefix tuning are supported, and if the chatbot dev has fine-tuning available, it can be used to further improve tool use for all users, even if they use different plugins.

## For plugin developers:
You write a `manifest.json` with:
* A list of API endpoints, and how to call them.
* "Prompt fragments" showing where the APIs are useful.
* (optional) A regex to validate input arguments.

Current Proposal (**expect changes**):
```
{
    "plugin_api_version": 0,
	"name": "Example Plugin",
    "description": "A boilerplate for plugin developers to copy paste.",
    "past_messages": 0,
    "apis": [
    	"MATH": {url:"https://example.tld/api/math", arguments: true, examples: [
    		["What is 123 + 456?", "123 + 456 is [MATH(123 + 456) -> 579] 579."],
    		["What is 123 * 456?", "123 * 456 is [MATH(123 * 456) -> 56088] 56088."]
    	]},
        "DATE": {url:"https://example.tld/api/date", arguments: false, examples: [
    		["What day is it?", "Today's date is [DATE() -> Feb 20th, 2023] February 20th, 2023."]
    	]}
    ]
}
```

## For chatbot developers:
To use plugins you:
* Compile a set of plugins into a "prompt fragment" which you add to your prompt.
* Parse the responses to extract plugin calls, executes them, and injects the results back into the context.

See `science.py` for a minimum example.

## Test results with GPT-Neo 125M:
### Few-Shot (n=1, ops=['+'])
* Accuracy (+): 81.00 (81 / 100)
* Accuracy (*): 1.00 (1 / 100)
* Accuracy (-): 6.00 (6 / 100)
* Accuracy (^): 17.00 (17 / 100)
* Accuracy (&): 0.00 (0 / 100)
* Accuracy (|): 9.00 (9 / 100)

### Few-Shot (n=2, ops=['+', '*'])
* Accuracy (+): 89.00 (89 / 100)
* Accuracy (*): 68.00 (68 / 100)
* Accuracy (-): 15.00 (15 / 100)
* Accuracy (^): 17.00 (17 / 100)
* Accuracy (&): 0.00 (0 / 100)
* Accuracy (|): 14.00 (14 / 100)

### Few-Shot (n=3, ops=['+', '*', '^'])
(running tests still...)
