// Diagram theme. The site is dark, and Mermaid's default is not, so an
// unconfigured diagram arrives as a bright panel with dark text in the middle
// of a dark page. `dark` matches the surrounding text rather than fighting it.
//
// securityLevel strict keeps click handlers and inline HTML out of diagrams:
// these are drawings, not an execution surface.
{
  theme: "dark",
  securityLevel: "strict",
  flowchart: { htmlLabels: true, curve: "basis", useMaxWidth: true }
}
