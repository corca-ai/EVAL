const submit = async () => {
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

  const { answer } = await response.json();
  document.getElementById("answer").textContent = answer;
};
