(function () {
  async function loadScenario(id) {
    const prefix = document.body.dataset.dataPrefix || "";
    const res = await fetch(`${prefix}data/${id}.json`, { cache: "no-cache" });
    if (!res.ok) throw new Error(`missing data/${id}.json`);
    return res.json();
  }

  async function loadLatest() {
    const prefix = document.body.dataset.dataPrefix || "";
    const res = await fetch(`${prefix}data/latest.json`);
    if (!res.ok) return null;
    return res.json();
  }

  window.LatticeSiteData = { loadScenario, loadLatest };
})();
