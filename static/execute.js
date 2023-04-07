const setLoader = (isLoading) => {
  const button = document.getElementById("submit");
  const loader = document.getElementById("submit-loader");
  if (isLoading) {
    button.style.display = "none";
    loader.style.display = "block";
  } else {
    button.style.display = "block";
    loader.style.display = "none";
  }
};

const setAnswer = (answer, files) => {
  document.getElementById("answer").textContent = answer;
  const filesDiv = document.getElementById("response-files");
  filesDiv.innerHTML = "";
  files.forEach((file) => {
    const a = document.createElement("a");
    a.classList.add("icon-link");
    a.href = file;
    a.textContent = file.split("/").pop();
    a.setAttribute("download", "");
    filesDiv.appendChild(a);
  });
};

class EvalApi {
  constructor({ onComplete, onError, onSettle }) {
    this.executionId = null;
    this.pollInterval = null;
    this.onComplete = (answer, files) => {
      onComplete(answer, files);
      onSettle();
    };
    this.onError = (error) => {
      onError(error);
      onSettle();
    };
  }

  async uploadFiles(rawfiles) {
    const files = [];

    if (rawfiles.length > 0) {
      const formData = new FormData();
      for (let i = 0; i < rawfiles.length; i++) {
        formData.append("files", rawfiles[i]);
      }
      const respone = await fetch("/upload", {
        method: "POST",
        body: formData,
      });
      const { urls } = await respone.json();
      files.push(...urls);
    }

    return files;
  }

  async execute(prompt, session, files) {
    try {
      const response = await fetch("/api/execute/async", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt,
          session,
          files,
        }),
      });
      if (response.status !== 200) {
        throw new Error(await response.text());
      }
      const { id: executionId } = await response.json();
      this.executionId = executionId;
      this.pollInterval = setInterval(this.poll.bind(this), 1000);
    } catch (e) {
      clearInterval(this.pollInterval);
      this.onError(e);
    }
  }

  async poll() {
    try {
      const response = await fetch(`/api/execute/async/${this.executionId}`, {
        method: "GET",
      });
      if (response.status !== 200) {
        throw new Error(await response.text());
      }
      const { status, result } = await response.json();
      if (status === "FAILURE") {
        throw new Error("Execution failed");
      }
      if (status === "SUCCESS") {
        clearInterval(this.pollInterval);
        this.onComplete(result.answer, result.files);
      }
    } catch (e) {
      clearInterval(this.pollInterval);
      this.onError(e);
    }
  }
}

const submit = async () => {
  setAnswer("Thinking...", []);
  setLoader(true);

  const api = new EvalApi({
    onComplete: (answer, files) => setAnswer(answer, files),
    onError: (error) => setAnswer(`Error: ${error.message}`, []),
    onSettle: () => setLoader(false),
  });

  const prompt = document.getElementById("prompt").value;
  const session = document.getElementById("session").value;
  const files = await api.uploadFiles(document.getElementById("files").files);

  await api.execute(prompt, session, files);
};

const setRandomSessionId = () => {
  const sessionId = Math.random().toString(36).substring(2, 15);
  document.getElementById("session").value = sessionId;
};
