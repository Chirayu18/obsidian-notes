#!/usr/bin/env python3
"""Deterministic local-link inventory. No network, deletion, or Archive traversal.

Checks rendered Markdown/wiki links and local HTML/CSS/TeX asset references.
Code fences and inline code are examples, not rendered links. Heading/block
anchors are retained during rewrites; this checker validates target files only.
"""
import argparse
import collections
import json
import os
import posixpath
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
TEXT = {'.md', '.html', '.css', '.tex'}


def files():
    out = subprocess.check_output(
        ['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=ROOT
    ).decode().split('\0')
    paths = {p for p in out if p and not p.startswith(('Archive/', '.'))
             and (ROOT / p).is_file()}
    # Deck figures may deliberately be gitignored but are still local assets.
    for top in ('Projects', 'References', 'Meta'):
        for directory, children, names in os.walk(ROOT / top):
            children[:] = [x for x in children if not x.startswith('.')
                           and x != '__pycache__'
                           and not (Path(directory) / x / '.git').exists()
                           and (Path(directory) / x).relative_to(ROOT).as_posix() != 'References/Private']
            for name in names:
                if not name.startswith('.'):
                    paths.add((Path(directory) / name).relative_to(ROOT).as_posix())
    return sorted(paths)


def rendered(text):
    def blank(m):
        return ''.join('\n' if c == '\n' else ' ' for c in m.group())
    text = re.sub(r'(?ms)^([ \t]*)(`{3,}|~{3,})[^\n]*\n.*?^\1\2[^\n]*(?:\n|$)', blank, text)
    text = re.sub(r'`+[^`\n]*`+', blank, text)
    return text


def references(source, text):
    """Yield (kind, start, end, raw target), with offsets into original text."""
    suffix = Path(source).suffix
    body = rendered(text) if suffix == '.md' else text
    if suffix == '.md':
        for m in re.finditer(r'\[\[([^\]\n]+)\]\]', body):
            raw = m[1].split('|', 1)[0].removesuffix('\\')
            yield 'wiki', m.start(1), m.start(1) + len(raw), raw
        for m in re.finditer(r'!?\[[^\]\n]*\]\((<[^>\n]*>|(?:[^()\n]|\([^()\n]*\))+)\)', body):
            raw = m[1]
            if raw.startswith('<'):
                yield 'markdown', m.start(1) + 1, m.start(1) + len(raw) - 1, raw[1:-1]
            else:
                raw = re.split(r'\s+[\"\']', raw, maxsplit=1)[0].rstrip()
                yield 'markdown', m.start(1), m.start(1) + len(raw), raw
    for m in re.finditer(r'(?:src|href|poster|data-background-image)\s*=\s*([\"\'])(.*?)\1', body):
        yield 'html', m.start(2), m.end(2), m[2]
    if suffix == '.css':
        for m in re.finditer(r'url\(\s*[\"\']?([^\)\"\']+)[\"\']?\s*\)', body):
            yield 'css', m.start(1), m.end(1), m[1].strip()
    if suffix == '.tex':
        for m in re.finditer(r'\\(?:includegraphics(?:\[[^\]]*\])?|input|include)\{([^}]+)\}', body):
            yield 'tex', m.start(1), m.end(1), m[1]


class Resolver:
    def __init__(self, paths):
        self.paths = set(paths)
        self.private = set()
        private = ROOT / 'References/Private'
        if private.is_dir():
            self.private = {p.relative_to(ROOT).as_posix() for p in private.rglob('*.md')}
        self.names = collections.defaultdict(list)
        for p in self.paths | self.private:
            self.names[Path(p).name.casefold()].append(p)
        self.folded = {p.casefold(): p for p in paths}

    def resolve(self, source, raw, kind='wiki'):
        value = unquote(raw.strip()).replace('\\ ', ' ')
        if not value or value.startswith('#'):
            return source, 'self'
        if re.match(r'^[a-zA-Z][\w+.-]*:', value) or value.startswith(('~/', '//')):
            return None, 'external'
        if any(x in value for x in ('<%', '{{', '<Project', '<name', '$', '*')):
            return None, 'template'
        value = value.split('#', 1)[0].split('?', 1)[0]
        prefix = str(ROOT) + '/'
        if value.startswith(prefix):
            value = value[len(prefix):]
        elif value.startswith('/'):
            return None, 'external-local'
        variants = [value]
        if kind == 'wiki' and not value.endswith('.md'):
            variants.append(value + '.md')
        if kind == 'tex' and not Path(value).suffix:
            variants += [value + x for x in ('.tex', '.pdf', '.png', '.jpg')]
        parent = posixpath.dirname(source)
        candidates = []
        # Wikilinks allow vault-qualified targets; Markdown is source-relative.
        for v in variants:
            candidates += ([v, posixpath.normpath(posixpath.join(parent, v))]
                           if kind == 'wiki' and '/' in v else [posixpath.normpath(posixpath.join(parent, v))])
            if kind == 'wiki' or (kind == 'markdown' and v.startswith(('Projects/', 'References/', 'Meta/', 'Daily/', 'Templates/'))):
                candidates.append(v)
        if kind == 'tex':
            text = (ROOT / source).read_text(errors='replace')
            for declaration in re.finditer(r'\\graphicspath\{((?:\{[^}]*\})+)\}', text):
                for directory in re.findall(r'\{([^}]*)\}', declaration[1]):
                    candidates += [posixpath.normpath(posixpath.join(parent, directory, v)) for v in variants]
        for c in candidates:
            if c in self.paths:
                return c, 'resolved'
            if c in self.private:
                return c, 'local-only'
        for c in candidates:
            if (kind != 'wiki' or '/' in value) and c.casefold() in self.folded:
                return self.folded[c.casefold()], 'case-mismatch'
            if kind != 'wiki' and any(p.startswith(c.rstrip('/') + '/') for p in self.paths):
                return c.rstrip('/') + '/', 'directory'
        if kind != 'wiki':
            return None, 'missing'
        matches = []
        for v in variants:
            matches += [p for p in self.names[Path(v).name.casefold()]
                        if '/' not in v or p.casefold().endswith('/' + v.casefold())]
        matches = sorted(set(matches))
        if not matches:
            return None, 'missing'
        def score(p):
            a, b = parent.split('/'), posixpath.dirname(p).split('/')
            common = 0
            for x, y in zip(a, b):
                if x != y:
                    break
                common += 1
            return common, -(len(a) + len(b) - 2 * common)
        ranked = sorted(matches, key=score, reverse=True)
        if len(ranked) > 1 and score(ranked[0]) == score(ranked[1]):
            return None, 'ambiguous'
        return ranked[0], 'local-only' if ranked[0] in self.private else 'resolved'


def audit(paths=None):
    paths = paths or files()
    resolver = Resolver(paths)
    issues, edges, blanks = [], [], []
    for p in paths:
        if Path(p).suffix not in TEXT:
            continue
        text = (ROOT / p).read_text(errors='replace')
        if p.endswith('.md') and not text.strip():
            blanks.append(p)
        for kind, start, end, raw in references(p, text):
            target, state = resolver.resolve(p, raw, kind)
            entry = dict(source=p, line=text.count('\n', 0, start) + 1,
                         kind=kind, raw=raw, target=target, state=state)
            if state in ('missing', 'ambiguous', 'case-mismatch'):
                issues.append(entry)
            if target:
                edges.append(entry)
    return dict(files=len(paths), edges=edges, issues=issues, blank_notes=blanks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', type=Path)
    args = parser.parse_args()
    result = audit()
    if args.json:
        args.json.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(files=result['files'], links=len(result['edges']),
                          issues=len(result['issues']), blank_notes=len(result['blank_notes']))))
    if not args.json:
        for item in result['issues']:
            print(f"{item['source']}:{item['line']}: {item['state']}: {item['raw']}")
    return int(bool(result['issues']))


if __name__ == '__main__':
    raise SystemExit(main())
