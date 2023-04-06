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

  const query = document.getElementById("query").value;
  const key = document.getElementById("key").value;
  fetch("/command", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query,
      key,
      files,
    }),
  });
  return false;
};
