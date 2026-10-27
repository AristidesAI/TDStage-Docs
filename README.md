# TDStage documentation

Source for the TDStage documentation site, published with GitHub Pages at
<https://aristidesai.github.io/TDStage-Docs/>.

The system itself lives in a separate private repository. This repository
holds documentation only: how to run the console, set up the phones, operate
the TouchDesigner hub, and integrate with the tracking output.

## Editing

Pages are Markdown with YAML front matter. The theme is
[just-the-docs](https://just-the-docs.com), pulled in as a remote theme, so
there is no build step to run locally and nothing to install. Push to `main`
and GitHub Pages rebuilds the site.

Front matter controls where a page sits in the navigation:

```yaml
---
title: Running the console
parent: Console
nav_order: 2
---
```

A section index page uses `has_children: true` and no `parent`.

## What does not belong here

This repository is public. Commercial terms, client correspondence, pricing,
venue addresses and personal contact details stay in the private repository.
