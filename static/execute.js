const $ = (selector) => document.querySelector(selector);

const setLoader = (isLoading) => {
  const button = $("#submit");
  const loader = $("#submit-loader");
  if (isLoading) {
    button.style.display = "none";
    loader.style.display = "block";
  } else {
    button.style.display = "block";
    loader.style.display = "none";
  }
};

const setAnswer = (answer, files = []) => {
  if (answer) {
    $("#answer").textContent = answer;
  } else {
    $("#answer").innerHTML = createSpinner();
  }

  const filesDiv = $("#response-files");
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
  constructor({ onComplete, onError, onSettle, onLLMEnd, onToolEnd }) {
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
    this.onLLMEnd = (info) => {
      onLLMEnd(info);
    };
    this.onToolEnd = (info) => {
      onToolEnd(info);
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
      const { status, result, info } = await response.json();
      switch (status) {
        case "PENDING":
          break;
        case "FAILURE":
          throw new Error("Execution failed");
        case "LLM_END":
          this.onLLMEnd(info);
          break;
        case "TOOL_END":
          this.onToolEnd(info);
          break;
        case "SUCCESS":
          clearInterval(this.pollInterval);
          this.onComplete(result.answer, result.files);
          break;
      }
    } catch (e) {
      clearInterval(this.pollInterval);
      this.onError(e);
    }
  }
}

const submit = async () => {
  setAnswer("");
  setLoader(true);

  const actions = $("#actions");

  const api = new EvalApi({
    onComplete: (answer, files) => setAnswer(answer, files),
    onError: (error) => setAnswer(`Error: ${error.message}`, []),
    onSettle: () => setLoader(false),
    onLLMEnd: (info) => {
      const w = document.createElement("div");
      w.innerHTML = createActionCard(
        1,
        info.action,
        info.action_input,
        info.what_i_did,
        info.plan
      );
      actions.innerHTML = "";
      actions.appendChild(w);
    },
    onToolEnd: (info) => {
      const w = document.createElement("div");
      w.innerHTML = createActionCard(
        1,
        info.action,
        info.action_input,
        info.what_i_did,
        info.plan,
        info.observation
      );
      actions.innerHTML = "";
      actions.appendChild(w);
    },
  });

  const prompt = $("#prompt").value;
  const session = $("#session").value;
  const files = await api.uploadFiles($("#files").files);

  await api.execute(prompt, session, files);
};

const setRandomSessionId = () => {
  const sessionId = Math.random().toString(36).substring(2, 15);
  $("#session").value = sessionId;
};

const createSpinner = () => `
<div class="text-center">
  <div class="spinner-border m-3"></div>
</div>
`;

const createActionCard = (
  index,
  action,
  input,
  whatIdid,
  plan,
  observation
) => `
<div class="accordion">
  <div class="accordion-item">
    <h2 class="accordion-header">
      <button class="accordion-button">
        Action #${index} - ${action}
      </button>
    </h2>
    <div class="accordion-collapse collapse show">
      <div class="accordion-body">
        <table class="table">
          <tbody>
            <tr>
              <th>Input</th>
              <td><div>${input}</div></td>
            </tr>
            <tr>
              <th>What I Did</th>
              <td><div>${whatIdid}</div></td>
            </tr>
          </tbody>
        </table>

        <table class="table">
          <thead>
            <tr>
              <th colspan="2">Plan</th>
            </tr>
          </thead>
          <tbody>
          ${plan
            .split("- ")
            .map((p) => p.trim())
            .filter((p) => p.length > 0)
            .map(
              (p) => `
              <tr>
              ${
                p.startsWith("[ ]")
                  ? `<td><input class="form-check-input" type="checkbox" /></td>
                  <td>${p.replace("[ ]", "")}</td>`
                  : ""
              }
              ${
                p.startsWith("[x]")
                  ? `<td><input class="form-check-input" type="checkbox" checked/></td>
                  <td>${p.replace("[x]", "")}</td>`
                  : ""
              }
              ${
                !p.startsWith("[ ]") && !p.startsWith("[x]")
                  ? `<td></td><td>${p}</td>`
                  : ""
              }
              </tr>`
            )
            .join("")}
          </tbody>
        </table>

        <table class="table">
          <thead>
            <tr>
              <th colspan="2">Observation</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>
                <div style="white-space: pre">${observation}</div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>
  </div>
</div>`;
