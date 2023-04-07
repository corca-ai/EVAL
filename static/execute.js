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

const submit = async () => {
  setAnswer("Loading...", []);
  const files = [];
  const rawfiles = document.getElementById("files").files;

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

  const prompt = document.getElementById("prompt").value;
  const session = document.getElementById("session").value;

  try {
    const response = await fetch("/api/execute", {
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
    const { answer, files: responseFiles } = await response.json();
    setAnswer(answer, responseFiles);
  } catch (e) {
    setAnswer("Error: " + e.message, []);
  }
};

const setRandomSessionId = () => {
  const sessionId = Math.random().toString(36).substring(2, 15);
  document.getElementById("session").value = sessionId;
};
