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

## Few-shot results with GPT-Neo 125M:
With `[MATH(expression) -> result]` syntax, 125 trials:
| Operator | N=0 (control) | N=1 | N=2 | N=3 | N=4 | N=5 |
| - | - | - | - | - | - | - |
| + | 0.00% | 92.1% | 97.6% | 93.7% | 94.4% | 95.2% |
| * | 0.00% | 2.4% | 93.7% | 92.9% | 93.7% | 92.9% |
| - | 0.00% | 21.4% | 39.7% | 46.0% | 50.0% | 54.0% |
| ^ | 0.00% | 15.1% | 38.1% | 96.8% | 91.3% | 88.1% |
| & | 0.00% | 0.0% | 3.2% | 11.1% | 73.0% | 65.1% |
| \| (held out) | 0.0% | 15.1% | 48.4% | 77.8% | 92.1% | 90.5% |

With `[MATH(expression)=result]` syntax, 125 trials:
| Operator | N=0 (control) | N=1 | N=2 | N=3 | N=4 | N=5 |
| - | - | - | - | - | - | - |
| + | 0.0% | 86.4% | 98.4% | 96.0% | 97.6% | 94.4% |
| * | 0.0% | 9.6% | 93.6% | 85.6% | 87.2% | 90.4% |
| - | 0.0% | 20.0% | 27.2% | 41.6% | 47.2% | 53.6% |
| ^ | 0.0% | 15.2% | 33.6% | 93.6% | 93.6% | 89.6% |
| & | 0.0% | 0.0% | 1.6% | 9.6% | 62.4% | 54.4% |
| \| (held out) | 0.0% | 12.8% | 26.4% | 78.4% | 90.4% | 83.2% |
