import React, { useState, useEffect, useCallback } from "react";

function App() {
  const [token, setToken] = useState(null);
  const [notes, setNotes] = useState([]);
  const [note, setNote] = useState("");
  const [error, setError] = useState("");

  const API_URL = "https://saas-backend.vercel.app"; // change to deployed backend later

  const login = async (email, password) => {
    try {
      const res = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) throw new Error("Login failed");
      const data = await res.json();
      setToken(data.access_token);
      setError("");
    } catch (err) {
      setError(err.message);
    }
  };

  // ✅ useCallback ensures fetchNotes reference is stable
  const fetchNotes = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API_URL}/notes`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error("Failed to fetch notes");
      const data = await res.json();
      setNotes(data);
    } catch (err) {
      setError(err.message);
    }
  }, [token]);

  const addNote = async () => {
    if (!token || !note) return;
    try {
      const res = await fetch(`${API_URL}/notes`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ content: note }),
      });
      if (res.ok) {
        setNote("");
        fetchNotes();
      } else {
        const err = await res.json();
        setError(err.detail || "Failed to add note");
      }
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    fetchNotes();
  }, [fetchNotes]); // ✅ no warning now

  return (
    <div style={{ padding: "2rem" }}>
      <h2>SaaS Notes App</h2>
      {!token ? (
        <div>
          <h3>Login</h3>
          <button onClick={() => login("admin@acme.test", "password")}>
            Login as Acme Admin
          </button>
          <button onClick={() => login("user@acme.test", "password")}>
            Login as Acme User
          </button>
          <button onClick={() => login("admin@globex.test", "password")}>
            Login as Globex Admin
          </button>
          <button onClick={() => login("user@globex.test", "password")}>
            Login as Globex User
          </button>
          {error && <p style={{ color: "red" }}>{error}</p>}
        </div>
      ) : (
        <div>
          <h3>Your Notes</h3>
          <input
            type="text"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="Write a note"
          />
          <button onClick={addNote}>Add Note</button>
          <ul>
            {notes.map((n) => (
              <li key={n.id}>{n.content}</li>
            ))}
          </ul>
          {error && <p style={{ color: "red" }}>{error}</p>}
        </div>
      )}
    </div>
  );
}

export default App;
