(() => {
  const shell = document.querySelector(".app-shell");
  const toggle = document.querySelector("[data-sidebar-toggle]");
  if (!shell || !toggle) return;

  const storageKey = "junance.sidebar.collapsed";
  const setCollapsed = (collapsed) => {
    document.documentElement.classList.remove("sidebar-precollapsed");
    shell.classList.toggle("sidebar-collapsed", collapsed);
    toggle.setAttribute("aria-expanded", String(!collapsed));
    toggle.setAttribute("aria-label", collapsed ? "Expandir menu" : "Recolher menu");
    toggle.setAttribute("title", collapsed ? "Expandir menu" : "Recolher menu");
    toggle.textContent = collapsed ? "›" : "‹";
  };

  setCollapsed(window.localStorage.getItem(storageKey) === "true");
  toggle.addEventListener("click", () => {
    const collapsed = !shell.classList.contains("sidebar-collapsed");
    setCollapsed(collapsed);
    window.localStorage.setItem(storageKey, String(collapsed));
  });
})();
