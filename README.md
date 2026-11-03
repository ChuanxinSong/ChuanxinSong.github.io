# Chuanxin Song

Personal academic homepage at [chuanxinsong.github.io](https://chuanxinsong.github.io/).

## Edit the content

Most content is maintained in `data/site.json`.

| Field | Content |
| --- | --- |
| `profile.bio` | Biography paragraphs |
| `profile.bioLinks` | Advisor links |
| `publications` | Paper titles, authors, venues, summaries, media and links |
| `publicationGroups` | Research groups and their diagrams |
| `honors`, `competitionAwards` | Honors and competition records |
| `academicService` | Reviewing service |
| `misc` | Personal interests |

Keep JSON syntax valid, including double quotes and commas. Image, video and PDF paths are relative to the project root. Add replacement media to `assets/` and update its path in the data.

`styles.css` controls typography, spacing and responsive layout. `scripts/build.py` contains the HTML template and generates `index.html`. `app.js` implements video playback and enlarged media dialogs.

## Update through GitHub

1. Open the file you want to edit on GitHub, such as `data/site.json`.
2. Use the pencil button to edit it, then commit the change to `main`.
3. Open the Actions tab and wait for **Publish homepage** to finish successfully.
4. Refresh the public website.

Every push to `main` regenerates the page and deploys it through GitHub Pages. The generated `index.html` in the source repository is a local-preview snapshot. The deployment always builds it afresh from the current data and template.

## Local preview

Requires Python 3.9 or newer with its standard library.

```sh
python scripts/build.py
python -m http.server 4173 --bind 127.0.0.1
```

Visit [the local preview](http://127.0.0.1:4173/). Regenerate the page after editing the data or template. Refresh after editing CSS or JavaScript.

To produce the same website files as GitHub Actions, run

```sh
python scripts/build.py
python scripts/package_site.py
```

The output is `dist/`. The packaging script collects local files referenced by the generated HTML, including lazy-loaded videos, enlarged images and PDFs. When adding CSS imports or dynamically generated resource paths, update the packaging script to include those dependencies.

## Media

The repository contains the image, video and PDF files used by the homepage. Videos are stored as ordinary Git files. Preserve the `.gitattributes` settings when updating media.

Figures, photographs and videos retain their respective owners' rights. See the linked papers, code repositories and datasets for their terms.
