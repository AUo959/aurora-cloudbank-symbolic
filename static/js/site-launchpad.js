const dataPath = "site-data.json";

const getById = (id) => document.getElementById(id);
const page = document.body.dataset.page;

function isExternal(href) {
  return /^https?:\/\//.test(href);
}

function linkAttributes(href) {
  return isExternal(href) ? ' target="_blank" rel="noreferrer"' : "";
}

function formatDate(value) {
  if (!value) {
    return "Unknown";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return `${new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "UTC"
  }).format(date)} UTC`;
}

function renderHeroActions(siteData) {
  const target = getById("hero-actions");
  if (!target) {
    return;
  }

  target.innerHTML = siteData.heroActions.map((action) => `
    <a class="button-link ${action.style}" href="${action.href}"${linkAttributes(action.href)}>${action.label}</a>
  `).join("");
}

function renderDeploymentStatus(siteData) {
  const target = getById("deployment-status");
  if (!target) {
    return;
  }

  const deployment = siteData.generated.deployment;
  const facts = [
    ["Readiness", `${deployment.readinessPercent}%`],
    ["Verified", formatDate(deployment.timestamp)],
    ["Pages URL", siteData.site.pagesUrl.replace(/^https?:\/\//, "")]
  ];

  target.innerHTML = `
    <div class="status-pill"><span class="status-dot"></span>${deployment.status}</div>
    <dl class="status-facts">
      ${facts.map(([label, value]) => `
        <div>
          <dt>${label}</dt>
          <dd>${value}</dd>
        </div>
      `).join("")}
    </dl>
  `;
}

function renderMiniRuntimeSurfaces(siteData) {
  const target = getById("hero-runtime-surfaces");
  if (!target) {
    return;
  }

  target.innerHTML = siteData.runtimeSurfaces.slice(0, 3).map((surface) => `
    <div class="surface-mini-item">
      <span class="surface-badge">${surface.availability}</span>
      <strong>${surface.title}</strong>
      <p>${surface.description}</p>
    </div>
  `).join("");
}

function renderEvidence(siteData) {
  const metricsTarget = getById("evidence-metrics");
  const notesTarget = getById("evidence-notes");

  if (metricsTarget) {
    const metrics = [
      {
        label: "Version",
        value: `v${siteData.generated.version}`,
        source: "VERSION"
      },
      {
        label: "Deployment",
        value: siteData.generated.deployment.status,
        source: `deployment/status/latest_check.json · ${siteData.generated.deployment.readinessPercent}%`
      },
      {
        label: "API Route Entries",
        value: String(siteData.generated.metrics.apiRouteEntries),
        source: "docs/api/API_CATALOG.json"
      },
      {
        label: "Modules",
        value: String(siteData.generated.metrics.moduleCount),
        source: "Top-level directories under modules/"
      },
      {
        label: "Docs",
        value: String(siteData.generated.metrics.docsCount),
        source: "Tracked files under docs/"
      },
      {
        label: "Tests",
        value: String(siteData.generated.metrics.testCount),
        source: "Tracked files under tests/"
      }
    ];

    metricsTarget.innerHTML = metrics.map((metric) => `
      <div class="metric-card">
        <div class="metric-label">${metric.label}</div>
        <div class="metric-value">${metric.value}</div>
        <div class="metric-source">${metric.source}</div>
      </div>
    `).join("");
  }

  if (notesTarget && siteData.generated.notes.length) {
    notesTarget.innerHTML = siteData.generated.notes.map((note) => `
      <div class="note-chip">${note}</div>
    `).join("");
  }
}

function renderLayers(siteData) {
  const target = getById("layer-map");
  if (!target) {
    return;
  }

  target.innerHTML = siteData.layers.map((layer) => `
    <article class="layer-row">
      <div class="layer-level">${layer.level}</div>
      <div>
        <h3>${layer.title}</h3>
        <p>${layer.summary}</p>
      </div>
      <a class="resource-action" href="${layer.href}"${linkAttributes(layer.href)}>Open source</a>
    </article>
  `).join("");
}

function renderExperiences(siteData, targetId = "experience-list") {
  const target = getById(targetId);
  if (!target) {
    return;
  }

  target.innerHTML = siteData.experiences.map((experience) => `
    <article class="experience-item">
      <div>
        <div class="experience-header">
          <span class="kind-chip">${experience.type}</span>
          <span class="path-chip">${experience.href}</span>
        </div>
        <h3>${experience.title}</h3>
        <p>${experience.summary}</p>
      </div>
      <a class="resource-action" href="${experience.href}">Open</a>
    </article>
  `).join("");
}

function installCopyHandlers(root = document) {
  root.addEventListener("click", async (event) => {
    const trigger = event.target.closest("[data-copy]");
    if (!trigger) {
      return;
    }

    try {
      await navigator.clipboard.writeText(trigger.dataset.copy);
      const original = trigger.textContent;
      trigger.textContent = "Copied";
      trigger.classList.add("copied");
      setTimeout(() => {
        trigger.textContent = original;
        trigger.classList.remove("copied");
      }, 1200);
    } catch (error) {
      console.error("Copy failed", error);
    }
  });
}

function renderLaunchpad(siteData) {
  const personaState = {
    activePersona: siteData.personas.find((entry) => entry.id === window.location.hash.slice(1))?.id || siteData.personas[0].id,
    activeKind: "all",
    query: ""
  };

  const personaTarget = getById("persona-switcher");
  const summaryTarget = getById("persona-summary");
  const commandTarget = getById("command-panels");
  const resourceTarget = getById("resource-list");
  const filterTarget = getById("resource-filters");
  const searchTarget = getById("resource-search");

  const renderPersona = () => {
    const persona = siteData.personas.find((entry) => entry.id === personaState.activePersona);
    const personaResources = siteData.resources.filter((resource) => resource.personas.includes(persona.id));
    const kinds = ["all", ...new Set(personaResources.map((resource) => resource.kind))];
    const filteredResources = personaResources.filter((resource) => {
      const matchesKind = personaState.activeKind === "all" || resource.kind === personaState.activeKind;
      const query = personaState.query.trim().toLowerCase();
      const haystack = [resource.title, resource.summary, resource.tags.join(" "), resource.sourcePath].join(" ").toLowerCase();
      return matchesKind && (!query || haystack.includes(query));
    });

    personaTarget.innerHTML = siteData.personas.map((entry) => `
      <button class="mode-button ${entry.id === persona.id ? "active" : ""}" data-persona="${entry.id}">
        ${entry.label}
      </button>
    `).join("");

    summaryTarget.innerHTML = `
      <div class="section-kicker">Current mode</div>
      <h3>${persona.label}</h3>
      <p>${persona.summary}</p>
      <ul>
        ${persona.outcomes.map((outcome) => `<li>${outcome}</li>`).join("")}
      </ul>
    `;

    const panels = siteData.commandPanels.filter((panel) => panel.personas.includes(persona.id));
    commandTarget.innerHTML = panels.map((panel) => `
      <article class="command-panel">
        <div class="command-header">
          <div>
            <h3>${panel.title}</h3>
            <p>${panel.intro}</p>
          </div>
          <button class="copy-button" data-copy="${panel.commands.join("\n").replace(/"/g, "&quot;")}">Copy block</button>
        </div>
        <div class="command-list">
          ${panel.commands.map((command) => `
            <div class="command-line">
              <code>${command}</code>
              <button class="copy-button" data-copy="${command.replace(/"/g, "&quot;")}">Copy</button>
            </div>
          `).join("")}
        </div>
      </article>
    `).join("");

    filterTarget.innerHTML = kinds.map((kind) => `
      <button class="filter-button ${kind === personaState.activeKind ? "active" : ""}" data-kind="${kind}">
        ${kind === "all" ? "All resources" : kind}
      </button>
    `).join("");

    if (filteredResources.length === 0) {
      resourceTarget.innerHTML = `<div class="empty-state">No resources match the current mode and search.</div>`;
      return;
    }

    resourceTarget.innerHTML = filteredResources.map((resource) => `
      <article class="resource-row">
        <div>
          <div class="resource-header">
            <span class="kind-chip">${resource.kind}</span>
            <span class="path-chip">${resource.sourcePath}</span>
          </div>
          <h3>${resource.title}</h3>
          <p>${resource.summary}</p>
          <div class="tag-line">
            ${resource.tags.map((tag) => `<span>${tag}</span>`).join("")}
          </div>
        </div>
        <a class="resource-action" href="${resource.href}"${linkAttributes(resource.href)}>Open</a>
      </article>
    `).join("");
  };

  personaTarget?.addEventListener("click", (event) => {
    const button = event.target.closest("[data-persona]");
    if (!button) {
      return;
    }

    personaState.activePersona = button.dataset.persona;
    personaState.activeKind = "all";
    window.history.replaceState({}, "", `#${personaState.activePersona}`);
    renderPersona();
  });

  filterTarget?.addEventListener("click", (event) => {
    const button = event.target.closest("[data-kind]");
    if (!button) {
      return;
    }

    personaState.activeKind = button.dataset.kind;
    renderPersona();
  });

  searchTarget?.addEventListener("input", (event) => {
    personaState.query = event.target.value;
    renderPersona();
  });

  renderPersona();
}

function renderDashboard(siteData) {
  const metricsTarget = getById("dashboard-metrics");
  const runtimeTarget = getById("dashboard-runtime");
  const checklistTarget = getById("dashboard-checklist");
  const resourcesTarget = getById("dashboard-resources");

  if (metricsTarget) {
    const metrics = [
      ["Version", `v${siteData.generated.version}`],
      ["Deployment", siteData.generated.deployment.status],
      ["Readiness", `${siteData.generated.deployment.readinessPercent}%`],
      ["Route entries", String(siteData.generated.metrics.apiRouteEntries)]
    ];

    metricsTarget.innerHTML = metrics.map(([label, value]) => `
      <div class="metric-card">
        <div class="metric-label">${label}</div>
        <div class="metric-value">${value}</div>
      </div>
    `).join("");
  }

  if (runtimeTarget) {
    runtimeTarget.innerHTML = siteData.runtimeSurfaces.map((surface) => `
      <div class="runtime-surface">
        <span class="surface-badge">${surface.availability}</span>
        <strong>${surface.title}</strong>
        <p>${surface.description}</p>
        <a class="surface-link" href="${surface.href}"${linkAttributes(surface.href)}>Open surface</a>
      </div>
    `).join("");
  }

  if (checklistTarget) {
    checklistTarget.innerHTML = siteData.opsChecklist.map((item) => `<li>${item}</li>`).join("");
  }

  if (resourcesTarget) {
    const operateResources = siteData.resources.filter((resource) => resource.personas.includes("operate") || resource.personas.includes("build")).slice(0, 6);
    resourcesTarget.innerHTML = operateResources.map((resource) => `
      <article class="resource-row">
        <div>
          <div class="resource-header">
            <span class="kind-chip">${resource.kind}</span>
            <span class="path-chip">${resource.sourcePath}</span>
          </div>
          <h3>${resource.title}</h3>
          <p>${resource.summary}</p>
        </div>
        <a class="resource-action" href="${resource.href}"${linkAttributes(resource.href)}>Open</a>
      </article>
    `).join("");
  }

  renderExperiences(siteData, "dashboard-experiences");
}

function applyCommonSiteData(siteData) {
  const versionChip = getById("version-chip");
  const buildStamp = getById("footer-build-stamp");
  const dashboardBuildStamp = getById("dashboard-build-stamp");
  const revisionSuffix = siteData.generated.revision ? ` · ${siteData.generated.revision}` : "";

  if (versionChip) {
    versionChip.textContent = `v${siteData.generated.version}`;
  }

  if (buildStamp) {
    buildStamp.textContent = `Built ${formatDate(siteData.generated.buildTime)}${revisionSuffix} from tracked repo evidence`;
  }

  if (dashboardBuildStamp) {
    dashboardBuildStamp.textContent = `Built ${formatDate(siteData.generated.buildTime)}${revisionSuffix} from tracked repo evidence`;
  }
}

function enableReveals() {
  const nodes = [...document.querySelectorAll("[data-reveal]")];
  if (!("IntersectionObserver" in window)) {
    nodes.forEach((node) => node.classList.add("is-visible"));
    return;
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.15
  });

  nodes.forEach((node) => observer.observe(node));
}

function registerServiceWorker() {
  if (!("serviceWorker" in navigator)) {
    return;
  }

  window.addEventListener("load", () => {
    navigator.serviceWorker.register("sw.js").catch((error) => {
      console.error("Service worker registration failed", error);
    });
  });
}

async function main() {
  try {
    const response = await fetch(dataPath);
    const siteData = await response.json();

    document.documentElement.classList.add("is-ready");
    applyCommonSiteData(siteData);
    renderHeroActions(siteData);
    renderDeploymentStatus(siteData);
    renderMiniRuntimeSurfaces(siteData);

    if (page === "launchpad") {
      renderEvidence(siteData);
      renderLayers(siteData);
      renderExperiences(siteData);
      renderLaunchpad(siteData);
    }

    if (page === "dashboard") {
      renderDashboard(siteData);
    }

    installCopyHandlers();
    enableReveals();
    registerServiceWorker();
  } catch (error) {
    console.error("Failed to render site data", error);
  }
}

document.addEventListener("DOMContentLoaded", main);
