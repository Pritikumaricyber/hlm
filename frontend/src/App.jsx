
import { useEffect, useState } from "react";
import "./App.css";
const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello! I’m your Human-Like Memory AI. I can remember information, learn your preferences, and adapt my responses over time.",
    },
  ]);

  const [loading, setLoading] = useState(false);

  const [memories, setMemories] = useState([]);
  const [memoryLoading, setMemoryLoading] = useState(true);

  const [behavioralProfiles, setBehavioralProfiles] = useState([]);
  const [behavioralLoading, setBehavioralLoading] = useState(true);
  const [systemActivity, setSystemActivity] = useState([
    "System ready",
  ]);

  // null = checking, true = online, false = offline
  const [backendOnline, setBackendOnline] = useState(null);

  const checkBackend = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      setBackendOnline(response.ok);
    } catch {
      setBackendOnline(false);
    }
  };

  const loadMemories = async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/memory-state/frontend_user`
      );

      if (!response.ok) {
        throw new Error(`Memory server returned ${response.status}`);
      }

      const data = await response.json();
      setMemories(data.memories);
    } catch (error) {
      console.error("Failed to load memories:", error);
    } finally {
      setMemoryLoading(false);
    }
  };

  const loadBehavioralProfile = async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/behavioral-profile/frontend_user`
      );

      if (!response.ok) {
        throw new Error(
          `Behavioral profile server returned ${response.status}`
        );
      }

      const data = await response.json();
      setBehavioralProfiles(data.profiles);
    } catch (error) {
      console.error("Failed to load behavioral profile:", error);
    } finally {
      setBehavioralLoading(false);
    }
  };

  useEffect(() => {
    const initializeDashboard = async () => {
      await Promise.all([
        checkBackend(),
        loadMemories(),
        loadBehavioralProfile(),
      ]);
    };

    initializeDashboard();
  }, []);

  const sendMessage = async () => {
    const trimmedMessage = message.trim();

    if (!trimmedMessage || loading) {
      return;
    }

    const userMessage = {
      role: "user",
      content: trimmedMessage,
    };

    setMessages((previous) => [...previous, userMessage]);
    setMessage("");
    setLoading(true);
    setSystemActivity([
      "Processing message",
      "Retrieving relevant memories",
      "Checking behavioral profile",
    ]);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: "frontend_user",
          message: trimmedMessage,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const data = await response.json();
      setBackendOnline(true);
      setSystemActivity([
        "Memory retrieved",
        "Behavioral profile checked",
        "Response generated",
      ]);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: data.response,
        },
      ]);

      await loadMemories();
      await loadBehavioralProfile();
    } catch (error) {
      console.error(error);
      setBackendOnline(false);
      setSystemActivity([
        "Backend connection failed",
      ]);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            "I couldn't connect to the memory backend. Please make sure the FastAPI server is running.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Human-Like Memory AI</h1>
          <p>Memory-Augmented Intelligent System</p>
        </div>

        <div className="status">
          <span
            className={`status-dot ${
              backendOnline === false ? "offline" : ""
            }`}
          ></span>
          {backendOnline === null
            ? "Checking backend..."
            : backendOnline
            ? "Backend Ready"
            : "Backend Offline"}
        </div>
      </header>

      <main className="dashboard">
        <section className="chat-container">
          <div className="chat-header">
            <div>
              <h2>Conversation</h2>
              <p>
                The system can recall memories and adapt its responses based
                on learned information.
              </p>
            </div>
          </div>

          <div className="messages">
            {messages.map((item, index) => (
              <div
                key={index}
                className={`message-row ${
                  item.role === "user" ? "user-row" : "assistant-row"
                }`}
              >
                <div
                  className={`message ${
                    item.role === "user"
                      ? "user-message"
                      : "assistant-message"
                  }`}
                >
                  {item.content}
                </div>
              </div>
            ))}

            {loading && (
              <div className="message-row assistant-row">
                <div className="message assistant-message typing">
                  Thinking...
                </div>
              </div>
            )}
          </div>

          <div className="input-area">
            <textarea
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Talk to your AI..."
              rows={1}
              disabled={loading}
            />

            <button
              onClick={sendMessage}
              disabled={loading || !message.trim()}
            >
              {loading ? "..." : "Send"}
            </button>
          </div>

          <p className="hint">
            Press Enter to send • Shift + Enter for a new line
          </p>
          
        </section>
        <aside className={`memory-panel ${systemActivity.length > 1 ? "activity-expanded" : ""}`}>
          <div className="memory-panel-header">
            <div>
              <h2>Memory State</h2>
              <p>Persistent memories for this user</p>
            </div>

            <span className="memory-count">{memories.length}</span>
          </div>

          {memoryLoading ? (
            <div className="memory-empty">Loading memories...</div>
          ) : memories.length === 0 ? (
            <div className="memory-empty">No memories stored yet.</div>
          ) : (
            <div className="memory-list">
              {memories.map((memory) => (
                <div className="memory-card" key={memory.id}>
                  <div className="memory-card-top">
                    <span className="memory-type">
                      {memory.memory_type}
                    </span>

                    <span className={`memory-status ${memory.status}`}>
                      {memory.status}
                    </span>
                  </div>

                  <p className="memory-content">{memory.content}</p>

                  <div className="memory-details">
                    <span>
                      Importance: {memory.importance.toFixed(2)}
                    </span>
                    <span>
                      Confidence: {memory.confidence.toFixed(2)}
                    </span>
                    <span>
                      Strength: {memory.strength.toFixed(2)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="behavioral-panel">
            <div className="memory-panel-header">
              <div>
                <h2>Behavioral Profile</h2>
                <p>Learned patterns for this user</p>
              </div>

              <span className="memory-count">
                {behavioralProfiles.length}
              </span>
            </div>

                        {behavioralLoading ? (
              <div className="memory-empty">
                Loading behavioral profile...
              </div>
            ) : behavioralProfiles.length === 0 ? (
              <div className="memory-empty">
                No behavioral patterns learned yet.
              </div>
            ) : (
              <div className="memory-list">
                {behavioralProfiles.map((profile) => (
                  <div
                    className="memory-card"
                    key={`${profile.concept}-${profile.behavior}`}
                  >
                    <div className="memory-card-top">
                      <span className="memory-type">
                        {profile.behavior}
                      </span>

                      <span
                        className={`memory-status ${profile.direction}`}
                      >
                        {profile.direction}
                      </span>
                    </div>

                    <p className="memory-content">
                      {profile.concept}
                    </p>

                    <div className="memory-details">
                      <span>
                        Evidence: {profile.evidence_count}
                      </span>
                      <span>
                        Consistency: {profile.consistency.toFixed(2)}
                      </span>
                      <span>
                        Confidence: {profile.confidence.toFixed(2)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          <section className="activity-panel">
            <div className="memory-panel-header">
              <div>
                <h2>System Activity</h2>
                <p>Recent memory-system events</p>
              </div>
            </div>
            <div className="activity-list">
              {systemActivity.map((activity, index) => (
              <div
                className="activity-item"
                key={`${activity}-${index}`}
              >
                <span className="activity-dot" />
                <span>{activity}</span>
              </div>
          ))}
        </div>
        </section>
        </aside>
      </main>
    </div>
  );
}

export default App;