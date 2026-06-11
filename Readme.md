# Bit Library

Inspired by Standford: https://web.archive.org/web/20220204203827/https://web.stanford.edu/class/cs106a/handouts_w2021/reference-bit.html

## Browser Playground

The static browser version is in `web/`. To run it locally:

```bash
python3 -m http.server 8000 --directory web
```

- Bit playground: http://127.0.0.1:8000/
- Generic Python console: http://127.0.0.1:8000/console.html

## GitHub Pages

The workflow at `.github/workflows/deploy-pages.yml` deploys `web/` whenever
changes to the site are pushed to `main`. It can also be run manually from the
Actions tab.

PyPI publishing is a separate, manually triggered workflow. Deploying the web
application does not publish the Python package.

Before the first deployment, open the repository's **Settings > Pages** and set
**Source** to **GitHub Actions**. After the workflow completes, the site is
available at:

https://garrett-webster.github.io/bit-web/
