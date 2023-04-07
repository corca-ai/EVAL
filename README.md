# EVAL

> **EVAL(Elastic Versatile Agent with Langchain) will execute all your requests. Like the eval method!**
>
> You don't have to think about how. If you tell them the results you want, they'll search, code, run, and test the Internet themselves, and they'll return the final results.

https://user-images.githubusercontent.com/19206046/229892113-481437b7-a332-4e0c-bfb3-d2c97c9035be.mp4

EVAL Making a full-fledged web application with multiple files

https://user-images.githubusercontent.com/51526347/230061897-b3479405-8ebd-45ab-a432-6506730242b9.mov

EVAL Making a UI for itself

#### [EVAL-BOT](https://github.com/eval-bot)

EVAL's self-managed github account. EVAL does everything except for signup and bio setting.

### Examples

[Here](examples/) is an example.

### EVAL's FEATURE

1. **Multimodal Conversation**
   - It **understands** and **generates** data formats for text, image, dataframe, audio (TODO), video (TODO).
2. **Services**
   - It can serve **services (blocking processes)** such as web apps.
3. **Evolving**
   - It can **create it's own tools** by writing, modifying, executing and testing code.

### BUILT-IN TOOLS

1. Terminal
   - SyscallTracer
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
4. Image Understanding, Generation, Editing
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

1. Environment variables
2. Run with docker-compose
3. Send request to EVAL

### 1. Environment Variables

You need to write some environment variables in the `.env` file. Refer [.env.example](.env.example) if you don't know how to format it.

**Mandatory**

Manatory envs are required in order to serve EVAL.

- `OPENAI_API_KEY` - OpenAI api key

**Optional**

Each optional env has default value, so you don't need to set unless you want to change it.

- `EVAL_PORT` - port (default: 8000)
- `SERVER` - server address (default: http://localhost:8000)
- `LOG_LEVEL` - INFO | DEBUG (default: INFO)
- `BOT_NAME` - give it a name! (default: Orca)
- `MODEL_NAME` - model name for GPT (default: gpt-4)

**For More Tools**

Some tools requires environment variables. Set envs depend on which tools you want to use.

- Google search tool
  - `SERPAPI_API_KEY`
- Bing search tool
  - `BING_SEARCH_URL`
  - `BING_SUBSCRIPTION_KEY`

### 2. Run with docker-compose

- There are 2 services in docker-compose.yml
  - `eval` - without GPU, much lighter
    ```bash
    docker-compose up --build eval
    ```
  - `eval.gpu` - with GPU, for multi-modal conversation
    ```bash
    docker-compose up --build eval.gpu
    ```
- The one with GPU is much heavier and unstable for now because of the massive dependencies. We recommend you to use the one without GPU if you don't need multi-modal conversation.

### 3. Send request to EVAL

- `POST /command`

  - `key` - session id
  - `files` - urls of file inputs
  - `query` - prompt

- You can send request to EVAL with `curl` or `httpie`.

  ```bash
  curl -X POST -H "Content-Type: application/json" -d '{"key": "sessionid", "files": ["https://example.com/image.png"], "query": "Hi there!"}' http://localhost:8000/command
  ```

  ```bash
  http POST http://localhost:8000/command key=sessionid files:='["https://example.com/image.png"]' query="Hi there!"
  ```

- We are planning to make a GUI for EVAL so you can use it without terminal.

## TODO

- [ ] GUI
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
