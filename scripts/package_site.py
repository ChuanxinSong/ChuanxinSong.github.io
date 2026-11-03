"""Collect the generated homepage and its local dependencies for GitHub Pages."""
from html.parser import HTMLParser
from pathlib import Path
import shutil
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / 'dist'


class PageFiles(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = {'index.html', '.nojekyll'}

    def handle_starttag(self, tag, attributes):
        for name, value in attributes:
            if name not in {'src', 'href', 'poster', 'data-src', 'data-image'} or not value:
                continue
            url = urlsplit(value)
            if not url.scheme and not url.netloc and url.path:
                self.paths.add(unquote(url.path))


def main():
    page = PageFiles()
    page.feed((ROOT / 'index.html').read_text(encoding='utf-8'))
    for relative_path in page.paths:
        source = (ROOT / relative_path).resolve()
        if not source.is_relative_to(ROOT) or not source.is_file():
            raise ValueError(f'Missing or out-of-project page file: {relative_path}')

    if DESTINATION.is_symlink() or DESTINATION.resolve() != ROOT / 'dist':
        raise ValueError('The distribution directory must remain inside this project.')
    if DESTINATION.exists():
        shutil.rmtree(DESTINATION)
    DESTINATION.mkdir()

    for relative_path in sorted(page.paths):
        destination = DESTINATION / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative_path, destination)
    print(f'Packaged {len(page.paths)} files into dist/.')


if __name__ == '__main__':
    main()
