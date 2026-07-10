(function () {
  const STORAGE_KEY = "let-reviewer-dismissed";

  function initReviewerBar() {
    if (localStorage.getItem(STORAGE_KEY) === "1") return;

    const bar = document.createElement("aside");
    bar.className = "reviewer-bar";
    bar.innerHTML = `
      <div class="reviewer-inner">
        <span class="reviewer-label">New here? 3-minute path</span>
        <nav class="reviewer-steps" aria-label="Reviewer path">
          <a href="${path("vision.html")}">1. Problem</a>
          <span aria-hidden="true">→</span>
          <a href="${path("run/relay-death-t14.html#h14")}">2. Live runner · T+14</a>
          <span aria-hidden="true">→</span>
          <a href="${path("demo/blocked_receipt.html")}">3. BLOCK receipt</a>
        </nav>
        <button type="button" class="reviewer-dismiss" aria-label="Dismiss guide">×</button>
      </div>`;
    document.body.appendChild(bar);

    bar.querySelector(".reviewer-dismiss")?.addEventListener("click", () => {
      localStorage.setItem(STORAGE_KEY, "1");
      bar.remove();
    });
  }

  function path(rel) {
    const p = window.location.pathname;
    if (p.includes("/run/") || p.includes("/demo/")) return "../" + rel;
    return rel;
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initReviewerBar);
  } else {
    initReviewerBar();
  }
})();
