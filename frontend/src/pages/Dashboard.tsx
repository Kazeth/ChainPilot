import { useEffect, useState } from "react";

export default function Dashboard() {
  const [data, setData] = useState<string | null>(null);

  useEffect(() => {
    fetch("https://fluffy-computing-machine-pxv46g79v9wf9r5v-8083.app.github.dev/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question:
          "What's the balance of address bc1q8sxznvhualuyyes0ded7kgt33876phpjhp29rs?",
      }),
    })
      .then((res) => res.json())
      .then((data) => setData(data.answer))
      .catch(console.error);
  }, []);

  return (
    <div>
      <h2>Dashboard</h2>
      <p>Welcome to your AI Crypto Agent dashboard!</p>
      <h3>Balance Result</h3>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}