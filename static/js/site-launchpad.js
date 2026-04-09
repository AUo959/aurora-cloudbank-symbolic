import {
  createCommandPanel,
  createElement,
  createEmptyState,
  createExperienceItem,
  createFilterButton,
  createLayerRow,
  createLink,
  createMetricCard,
  createMiniRuntimeSurface,
  createModeButton,
  createResourceHeader,
  createResourceRow,
  createRuntimeSurface,
  createStatusFacts,
  createSummaryBlock,
  formatDate,
  getById,
  replaceChildren,
  runtimeGlobal
} from "./site-dom.js";

const dataPath = "site-data.json";
const page = document.body.dataset.page;

function renderHeroActions(siteData) {
  const target = getById("hero-actions");
  replaceChildren(target, siteData.heroActions.map((action) => createLink(action.label, action.href, `button-link ${action.style}`)));
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

  replaceChildren(target, [
    createElement("div", { className: "status-pill" }, [
      createElement("span", { className: "status-dot", attributes: { "aria-hidden": "true" } }),
      deployment.status
    ]),
    createStatusFacts(facts)
  ]);
}

function renderMiniRuntimeSurfaces(siteData) {
  const target = getById("hero-runtime-surfaces");
  replaceChildren(target, siteData.runtimeSurfaces.slice(0, 3).map((surface) => createMiniRuntimeSurface(surface)));
}

function renderEvidence(siteData) {
  const metricsTarget = getById("evidence-metrics");
  const notesTarget = getById("evidence-notes");

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

  replaceChildren(metricsTarget, metrics.map((metric) => createMetricCard(metric)));

  if (notesTarget) {
    replaceChildren(notesTarget, siteData.generated.notes.map((note) => createElement("div", {
      className: "note-chip",
      text: note
    })));
  }
}

function renderLayers(siteData) {
  const target = getById("layer-map");
  replaceChildren(target, siteData.layers.map((layer) => createLayerRow(layer)));
}

function renderExperiences(siteData, targetId = "experience-list") {
  const target = getById(targetId);
  replaceChildren(target, siteData.experiences.map((experience) => createExperienceItem(experience)));
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
  const initialHash = runtimeGlobal.location?.hash?.slice(1) || "";
  const defaultPersonaId = siteData.personas[0]?.id;
  const personaState = {
    activePersona: siteData.personas.find((entry) => entry.id === initialHash)?.id || defaultPersonaId,
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
    const normalizedQuery = personaState.query.trim().toLowerCase();
    const filteredResources = personaResources.filter((resource) => {
      const matchesKind = personaState.activeKind === "all" || resource.kind === personaState.activeKind;
      const haystack = [resource.title, resource.summary, resource.tags.join(" "), resource.sourcePath]
        .join(" ")
        .toLowerCase();

      return matchesKind && (!normalizedQuery || haystack.includes(normalizedQuery));
    });

    replaceChildren(personaTarget, siteData.personas.map((entry) => createModeButton(entry, entry.id === persona.id)));
    replaceChildren(summaryTarget, [createSummaryBlock(persona)]);

    const panels = siteData.commandPanels.filter((panel) => panel.personas.includes(persona.id));
    replaceChildren(commandTarget, panels.map((panel) => createCommandPanel(panel)));

    replaceChildren(filterTarget, kinds.map((kind) => createFilterButton(kind, kind === personaState.activeKind)));

    if (filteredResources.length === 0) {
      replaceChildren(resourceTarget, [createEmptyState("No resources match the current mode and search.")]);
      return;
    }

    replaceChildren(resourceTarget, filteredResources.map((resource) => createResourceRow(resource)));
  };

  personaTarget?.addEventListener("click", (event) => {
    const button = event.target.closest("[data-persona]");
    if (!button) {
      return;
    }

    personaState.activePersona = button.dataset.persona;
    personaState.activeKind = "all";
    runtimeGlobal.history?.replaceState({}, "", `#${personaState.activePersona}`);
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

  const metrics = [
    ["Version", `v${siteData.generated.version}`],
    ["Deployment", siteData.generated.deployment.status],
    ["Readiness", `${siteData.generated.deployment.readinessPercent}%`],
    ["Route entries", String(siteData.generated.metrics.apiRouteEntries)]
  ];

  replaceChildren(metricsTarget, metrics.map(([label, value]) => createElement("div", { className: "metric-card" }, [
    createElement("div", { className: "metric-label", text: label }),
    createElement("div", { className: "metric-value", text: value })
  ])));

  replaceChildren(runtimeTarget, siteData.runtimeSurfaces.map((surface) => createRuntimeSurface(surface)));

  replaceChildren(checklistTarget, siteData.opsChecklist.map((item) => createElement("li", { text: item })));

  const operateResources = siteData.resources
    .filter((resource) => resource.personas.includes("operate") || resource.personas.includes("build"))
    .slice(0, 6);

  replaceChildren(resourcesTarget, operateResources.map((resource) => createElement("article", { className: "resource-row" }, [
    createElement("div", {}, [
      createResourceHeader(resource.kind, resource.sourcePath),
      createElement("h3", { text: resource.title }),
      createElement("p", { text: resource.summary })
    ]),
    createLink("Open", resource.href, "resource-action")
  ])));

  renderExperiences(siteData, "dashboard-experiences");
}

function applyCommonSiteData(siteData) {
  const versionChip = getById("version-chip");
  const buildStamp = getById("footer-build-stamp");
  const dashboardBuildStamp = getById("dashboard-build-stamp");
  const revisionSuffix = siteData.generated.revision ? ` · ${siteData.generated.revision}` : "";
  const buildText = `Built ${formatDate(siteData.generated.buildTime)}${revisionSuffix} from tracked repo evidence`;

  if (versionChip) {
    versionChip.textContent = `v${siteData.generated.version}`;
  }

  if (buildStamp) {
    buildStamp.textContent = buildText;
  }

  if (dashboardBuildStamp) {
    dashboardBuildStamp.textContent = buildText;
  }
}

function enableReveals() {
  const nodes = [...document.querySelectorAll("[data-reveal]")];
  if (!("IntersectionObserver" in runtimeGlobal)) {
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
  if (!runtimeGlobal.navigator?.serviceWorker) {
    return;
  }

  runtimeGlobal.addEventListener("load", () => {
    runtimeGlobal.navigator.serviceWorker.register("sw.js").catch((error) => {
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
