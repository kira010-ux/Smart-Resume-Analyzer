const browserHost = typeof window !== "undefined" ? window.location.hostname : "localhost";
const API_URL = import.meta.env.VITE_API_URL || `http://${browserHost}:8000`;

export async function analyzeMatch({ resumeText, jobText, resumeFile, jobFile }) {
  const formData = new FormData();

  if (resumeFile) formData.append("resume_file", resumeFile);
  else formData.append("resume_text", resumeText);

  if (jobFile) formData.append("job_description_file", jobFile);
  else formData.append("job_description_text", jobText);

  const response = await fetch(`${API_URL}/analyze`, {
    method: "POST",
    body: formData,
  });

  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.detail || "The analysis could not be completed.");
  }
  return payload;
}

export async function getHistory() {
  const response = await fetch(`${API_URL}/history`);
  if (!response.ok) {
    throw new Error("History could not be loaded.");
  }
  return response.json();
}
