# youn720lee.github.io

Personal academic homepage of **Younkwan Lee** — served by GitHub Pages at
<https://youn720lee.github.io>.

The site is a single static page generated from a few YAML files, so updating
it never requires touching HTML.

```
data/profile.yml        bio, education, experience, news, awards, activities, patents
data/publications.yml   publication list (one entry per paper)
data/projects.yml       industry projects
templates/index.html.j2 page template (Jinja2)
assets/css/style.css    styles (light/dark)
assets/js/main.js       filters, search, BibTeX dialog, theme toggle
assets/img/             avatar.svg (placeholder), favicon.svg — drop avatar.jpg here
assets/pubs/            paper thumbnails; tiles/ holds auto-generated venue tiles
build.py                regenerates index.html and assets/publications.bib
```

## Updating the site

1. Edit the YAML file(s) under `data/`.
2. Rebuild:

   ```bash
   pip install jinja2 pyyaml      # once
   python build.py
   ```

3. Commit and push `index.html`, `assets/`, and `data/` together.  GitHub Pages
   serves the committed `index.html` directly (`.nojekyll` disables Jekyll).

### Adding a paper

Append an entry to `data/publications.yml`:

```yaml
- key: lee2027example            # BibTeX key, must be unique
  title: Paper Title
  authors: [Younkwan Lee, Coauthor Name]
  venue: IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)
  venue_short: CVPR               # label on the auto-generated tile
  year: 2027
  type: conference                # journal | conference | workshop | preprint | domestic
  collapsed: true                 # optional: list it in the folded 'Other international conference papers' block
  award: Best Paper Award         # optional
  tags: [Oral]                    # optional badges
  pages: 1–10                     # optional; volume / number also supported
  links:                          # all optional
    paper: https://...            # or doi: — used as the title link, no button
    arxiv: https://arxiv.org/abs/...   # arxiv/code/project/dataset/video/slides/poster
    code: https://github.com/...       # are shown as buttons
    project: https://...
  image: assets/pubs/lee2027example.png   # optional; omit to use a venue tile
```

Thumbnails are picked up automatically: save a figure as
`assets/pubs/<key>.jpg` (or `.png`) and rebuild — no `image:` line needed.
A 3:2 image around 720×480 px looks best; anything else is letter-boxed or
cropped to 3:2.

### Replacing the avatar

Save a square photo as `assets/img/avatar.jpg` and set
`avatar: assets/img/avatar.jpg` in `data/profile.yml`.

### CV

Put the PDF at `assets/cv/Younkwan_Lee_CV.pdf` and set `cv:` in
`data/profile.yml`; the CV icon appears automatically.
