import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

function App() {
  return (
    <div className="shell">
      <header>
        <a className="wordmark" href="/" aria-label="Galene home">
          <span className="mark" aria-hidden="true">
            g.
          </span>{" "}
          Galene
        </a>
        <span className="preview">Early preview</span>
      </header>
      <main>
        <p className="eyebrow">A little order. A lighter move.</p>
        <h1>
          At home with
          <br />
          your belongings.
        </h1>
        <p className="intro">
          A place to remember what you own, find where it lives, and prepare for
          what comes next.
        </p>
        <section className="welcome" aria-labelledby="welcome-title">
          <div className="room" aria-hidden="true">
            <div className="window" />
            <div className="plant" />
            <div className="box" />
          </div>
          <div>
            <p className="eyebrow">Making room</p>
            <h2 id="welcome-title">Your inventory starts here.</h2>
            <p>
              Galene is taking shape. Sign-in, rooms, and your first belongings
              are coming next.
            </p>
          </div>
        </section>
      </main>
      <footer>
        Galene <span>For the things that make a home.</span>
      </footer>
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
