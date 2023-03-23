# EVAL

> **EVAL(Elastic Versatile Agent with Langchain) will execute all your requests. Like the eval method!**

You don't have to think about how. If you tell them the results you want, they'll search, code, run, and test the Internet themselves, and they'll return the final results.

### EVAL's FEATURE

1. It can **understand** and **generate** data formats for text, image, dataframe, audio (TODO), video (TODO).
2. It can **create tools** that it can use by writing and modifying code.
3. It can **evolve** itself by executing and testing its code.

### BUILT-IN TOOLS

1. Terminal
2. Code Editor
   - READ: Read and understand file.
   - WRITE: Write code to create a new tool.
   - PATCH: Correct the error throught the code patch if an error occurs.
   - DELETE: Delete code in file for a new start.
3. Search
   - Google, Bing, Wikipedia
   - Custom DB Search (Currently using Corca's Wine Data in https://www.workershop.kr/en)
     - Use GPT index to quickly find the information you need in a document and use that information to answer
   - Requests.get (Get information from anywhere you want)
4. Python REPL
5. Image Understanding, Generation, Editing
   - Image Understanding
     - Image Understanding: blip-image-captioning
     - Visual Question&Answering: blip-vqa
   - Image Generation: Stable Diffusion 1.5
   - Image Editing
     - Replace or remove an object: Stable Diffusion Inpainting
     - Change Image's style: InstructPix2Pix

Thanks to [LangChain](https://github.com/hwchase17/langchain), [Visual ChatGPT](https://github.com/microsoft/visual-chatgpt), [llama index](https://github.com/jerryjliu/llama_index).

### CUSTOM TOOLS

We also don't know what tools EVAL will create. Every day, It will create the right tools to execute your request.

---

## Usage

1. environments settings
2. `docker-compose up -d`

### Environment

You need to write some environment variables in the `.env` file. Refer [.env.example](.env.example) if you don't know how to format it.

**Mandatory**

Manatory envs are required in order to serve EVAL.

- `OPENAI_API_KEY` - OpenAI api key

**Optional**

Each optional env has default value, so you don't need to set unless you want to change it.

- `PORT` - port (default: 8000)
- `SERVER` - server address (default: http://localhost:8000)
- `LOG_LEVEL` - INFO | DEBUG (default: INFO)
- `BOT_NAME` - give it a name! (default: Orda)

**For More Tools**

Some tools requires environment variables. Set envs depend on which tools you want to use.

- Google search tool
  - `SERPAPI_API_KEY`
- Bing search tool
  - `BING_SEARCH_URL`
  - `BING_SUBSCRIPTION_KEY`

## TODO

- [ ] memory saving
- [ ] session manage
- [ ] convert to alpaca
- [ ] prompt upgrade
- [ ] give a tool to create tools
- [ ] etc.

## Reference

Thanks to the following repositories.

- https://github.com/hwchase17/langchain
- https://github.com/microsoft/visual-chatgpt
- https://github.com/jerryjliu/llama_index
