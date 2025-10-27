document.addEventListener("DOMContentLoaded", () => {
  const projectsAccordion = document.querySelector("#projectsAccordion");
  const projectsStatus = document.querySelector("#projectsStatus");

  if (!projectsAccordion) {
    console.warn("Projects accordion container not found.");
    return;
  }

  fetch("assets/publications.json")
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Failed to load publications (${response.status})`);
      }
      return response.json();
    })
    .then((publications) => {
      if (!Array.isArray(publications) || publications.length === 0) {
        projectsAccordion.innerHTML =
          '<div class="alert alert-info mb-0">No publications available yet. Check back soon!</div>';
        return;
      }

      const sorted = publications
        .slice()
        .sort((a, b) => {
          if (b.year !== a.year) return b.year - a.year;
          return a.title.localeCompare(b.title);
        });

      projectsAccordion.innerHTML = sorted
        .map((pub, index) => {
          const collapseId = pub.id || `publication-${index}`;
          const focusText = pub.focus ? `<b>Focus:</b> ${pub.focus}` : "";
          const venueText = pub.venue ? `<b>Venue:</b> ${pub.venue}` : "";
          const yearText = Number.isFinite(pub.year)
            ? `<b>Year:</b> ${pub.year}`
            : "";
          const metaLine = [focusText, venueText, yearText]
            .filter(Boolean)
            .join(" | ");
          const description = pub.description
            ? `<p>${pub.description}</p>`
            : "";
          const link =
            pub.link && pub.link.href
              ? `<a href="${pub.link.href}" target="_blank" rel="noopener noreferrer" class="btn btn-outline-info btn-sm">${pub.link.label || "View"}</a>`
              : "";

          return `
            <div class="accordion-item">
              <h2 class="accordion-header">
                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#${collapseId}">
                  ${pub.title || "Untitled Publication"}
                </button>
              </h2>
              <div id="${collapseId}" class="accordion-collapse collapse" data-bs-parent="#projectsAccordion">
                <div class="accordion-body">
                  ${metaLine ? `<p>${metaLine}</p>` : ""}
                  ${description}
                  ${link}
                </div>
              </div>
            </div>
          `;
        })
        .join("");
    })
    .catch((error) => {
      console.error(error);
      projectsAccordion.innerHTML =
        '<div class="alert alert-danger mb-0">We hit a snag loading publications. Please try refreshing.</div>';
    })
    .finally(() => {
      if (projectsStatus) {
        projectsStatus.classList.add("d-none");
      }
    });
});
