const runtimeGlobal = globalThis;

function getById(id) {
  return document.getElementById(id);
}

function isExternal(href) {
  return typeof href === "string" && (href.startsWith("http://") || href.startsWith("https://"));
}

function toSafeHref(href) {
  if (typeof href !== "string") {
    return "#";
  }

  if (href.startsWith("#") || isExternal(href)) {
    return href;
  }

  return /^[./A-Za-z0-9][A-Za-z0-9./_#?=&:-]*$/.test(href) ? href : "#";
}

function appendChildren(parent, children = []) {
  for (const child of children) {
    if (child === null || child === undefined || child === false) {
      continue;
    }

    if (Array.isArray(child)) {
      appendChildren(parent, child);
      continue;
    }

    if (child instanceof Node) {
      parent.appendChild(child);
      continue;
    }

    parent.appendChild(document.createTextNode(String(child)));
  }
}

function applyElementProperties(element, options) {
  const { className, text, htmlFor, value, type, placeholder } = options;

  if (className) {
    element.className = className;
  }

  if (text !== undefined) {
    element.textContent = text;
  }

  if (htmlFor) {
    element.htmlFor = htmlFor;
  }

  if (value !== undefined) {
    element.value = value;
  }

  if (type) {
    element.type = type;
  }

  if (placeholder) {
    element.placeholder = placeholder;
  }
}

function applyElementCollections(element, options) {
  const { dataset, attributes } = options;

  if (dataset) {
    Object.entries(dataset).forEach(([key, datasetValue]) => {
      element.dataset[key] = datasetValue;
    });
  }

  if (attributes) {
    Object.entries(attributes).forEach(([key, attributeValue]) => {
      if (attributeValue !== undefined && attributeValue !== null) {
        element.setAttribute(key, attributeValue);
      }
    });
  }
}

function createElement(tagName, options = {}, children = []) {
  const element = document.createElement(tagName);
  applyElementProperties(element, options);
  applyElementCollections(element, options);
  appendChildren(element, children);
  return element;
}

function replaceChildren(target, children = []) {
  if (!target) {
    return;
  }

  target.replaceChildren();
  appendChildren(target, children);
}

function createLink(label, href, className, attributes = {}) {
  const safeHref = toSafeHref(href);
  const linkAttributes = {
    ...attributes,
    href: safeHref
  };

  if (isExternal(safeHref)) {
    linkAttributes.target = "_blank";
    linkAttributes.rel = "noreferrer";
  }

  return createElement("a", {
    className,
    text: label,
    attributes: linkAttributes
  });
}

function createChip(className, text) {
  return createElement("span", { className, text });
}

function createPathChip(text) {
  return createChip("path-chip", text);
}

function createKindChip(text) {
  return createChip("kind-chip", text);
}

function createCopyButton(label, value) {
  return createElement("button", {
    className: "copy-button",
    text: label,
    type: "button",
    dataset: {
      copy: value
    }
  });
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

function createStatusFacts(facts) {
  const list = createElement("dl", { className: "status-facts" });

  replaceChildren(list, facts.map(([label, value]) => createElement("div", {}, [
    createElement("dt", { text: label }),
    createElement("dd", { text: value })
  ])));

  return list;
}

function createMetricCard(metric) {
  return createElement("div", { className: "metric-card" }, [
    createElement("div", { className: "metric-label", text: metric.label }),
    createElement("div", { className: "metric-value", text: metric.value }),
    createElement("div", { className: "metric-source", text: metric.source })
  ]);
}

function createTagLine(tags) {
  return createElement("div", { className: "tag-line" }, tags.map((tag) => createElement("span", { text: tag })));
}

function createResourceHeader(kind, sourcePath) {
  return createElement("div", { className: "resource-header" }, [
    createKindChip(kind),
    createPathChip(sourcePath)
  ]);
}

function createResourceRow(resource) {
  return createElement("article", { className: "resource-row" }, [
    createElement("div", {}, [
      createResourceHeader(resource.kind, resource.sourcePath),
      createElement("h3", { text: resource.title }),
      createElement("p", { text: resource.summary }),
      createTagLine(resource.tags)
    ]),
    createLink("Open", resource.href, "resource-action")
  ]);
}

function createExperienceItem(experience) {
  return createElement("article", { className: "experience-item" }, [
    createElement("div", {}, [
      createElement("div", { className: "experience-header" }, [
        createKindChip(experience.type),
        createPathChip(experience.href)
      ]),
      createElement("h3", { text: experience.title }),
      createElement("p", { text: experience.summary })
    ]),
    createLink("Open", experience.href, "resource-action")
  ]);
}

function createLayerRow(layer) {
  return createElement("article", { className: "layer-row" }, [
    createElement("div", { className: "layer-level", text: layer.level }),
    createElement("div", {}, [
      createElement("h3", { text: layer.title }),
      createElement("p", { text: layer.summary })
    ]),
    createLink("Open source", layer.href, "resource-action")
  ]);
}

function createRuntimeSurface(surface) {
  return createElement("div", { className: "runtime-surface" }, [
    createChip("surface-badge", surface.availability),
    createElement("strong", { text: surface.title }),
    createElement("p", { text: surface.description }),
    createLink("Open surface", surface.href, "surface-link")
  ]);
}

function createModeButton(entry, isActive) {
  return createElement("button", {
    className: `mode-button${isActive ? " active" : ""}`,
    text: entry.label,
    type: "button",
    dataset: {
      persona: entry.id
    }
  });
}

function createFilterButton(kind, isActive) {
  return createElement("button", {
    className: `filter-button${isActive ? " active" : ""}`,
    text: kind === "all" ? "All resources" : kind,
    type: "button",
    dataset: {
      kind
    }
  });
}

function createEmptyState(message) {
  return createElement("div", {
    className: "empty-state",
    text: message
  });
}

function createSummaryBlock(persona) {
  const outcomesList = createElement("ul");
  replaceChildren(outcomesList, persona.outcomes.map((outcome) => createElement("li", { text: outcome })));

  return createElement("div", {}, [
    createElement("div", { className: "section-kicker", text: "Current mode" }),
    createElement("h3", { text: persona.label }),
    createElement("p", { text: persona.summary }),
    outcomesList
  ]);
}

function createCommandLine(command) {
  return createElement("div", { className: "command-line" }, [
    createElement("code", { text: command }),
    createCopyButton("Copy", command)
  ]);
}

function createCommandPanel(panel) {
  return createElement("article", { className: "command-panel" }, [
    createElement("div", { className: "command-header" }, [
      createElement("div", {}, [
        createElement("h3", { text: panel.title }),
        createElement("p", { text: panel.intro })
      ]),
      createCopyButton("Copy block", panel.commands.join("\n"))
    ]),
    createElement("div", { className: "command-list" }, panel.commands.map((command) => createCommandLine(command)))
  ]);
}

function createMiniRuntimeSurface(surface) {
  return createElement("div", { className: "surface-mini-item" }, [
    createChip("surface-badge", surface.availability),
    createElement("strong", { text: surface.title }),
    createElement("p", { text: surface.description })
  ]);
}

export {
  createCommandPanel,
  createEmptyState,
  createElement,
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
};
