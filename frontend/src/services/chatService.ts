export const sendChatMessage = async (formData: FormData) => {
  const response = await fetch("http://localhost:8000/chat", {
    method: "POST",
    body: formData,
  });
  if (!response.ok) throw new Error("Network Error");
  return await response.json();
};
