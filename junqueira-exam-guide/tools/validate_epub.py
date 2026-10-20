#!/usr/bin/env python3
"""Structural validation of the EPUB, used because EPUBCheck (Java) is unavailable.

    python3 tools/validate_epub.py Basic_Histology_Learning_Text.epub

Checks: OCF container and mimetype, OPF metadata and manifest, the navigation
document, XML well-formedness of every XHTML file, internal link and fragment
resolution, image resources, and external dependencies.
"""

import os
import posixpath
import sys
import zipfile
import xml.etree.ElementTree as ET
from urllib.parse import unquote

NS = {
    "c": "urn:oasis:names:tc:opendocument:xmlns:container",
    "opf": "http://www.idpf.org/2007/opf",
    "dc": "http://purl.org/dc/elements/1.1/",
    "x": "http://www.w3.org/1999/xhtml",
    "epub": "http://www.idpf.org/2007/ops",
}


def main(path):
    errors, warnings = [], []
    z = zipfile.ZipFile(path)
    names = z.namelist()

    if names[0] != "mimetype":
        errors.append("mimetype is not the first entry")
    if z.getinfo("mimetype").compress_type != zipfile.ZIP_STORED:
        errors.append("mimetype is compressed")
    if z.read("mimetype") != b"application/epub+zip":
        errors.append("wrong mimetype content")

    container = ET.fromstring(z.read("META-INF/container.xml"))
    rootfile = container.find(".//c:rootfile", NS)
    if rootfile is None:
        errors.append("container.xml has no rootfile")
        return report(errors, warnings)
    opf_path = rootfile.get("full-path")

    opf = ET.fromstring(z.read(opf_path))
    base = posixpath.dirname(opf_path)
    md = opf.find("opf:metadata", NS)
    for tag in ("dc:title", "dc:language", "dc:identifier"):
        if md is None or md.find(tag, NS) is None:
            errors.append("missing metadata: " + tag)
    version = opf.get("version")
    if version != "3.0":
        warnings.append("package version is " + str(version))

    manifest = {}
    nav_path = None
    for item in opf.findall("opf:manifest/opf:item", NS):
        href = posixpath.normpath(posixpath.join(base, item.get("href")))
        manifest[item.get("id")] = href
        if "nav" in (item.get("properties") or ""):
            nav_path = href
    if nav_path is None:
        errors.append("no navigation document (properties=nav)")
    if not opf.findall("opf:spine/opf:itemref", NS):
        errors.append("empty spine")

    docs = {}
    for name in names:
        if name.endswith((".xhtml", ".html")):
            try:
                docs[name] = ET.fromstring(z.read(name))
            except ET.ParseError as exc:
                errors.append("not well-formed: %s (%s)" % (name, exc))

    targets = {(n, None) for n in names}
    link_count = 0
    for name, root in docs.items():
        for a in root.iter("{%s}a" % NS["x"]):
            href = a.get("href")
            if not href:
                continue
            link_count += 1
            if href.startswith(("http://", "https://", "mailto:", "tel:")):
                warnings.append("external link in %s: %s" % (name, href))
                continue
            target, _, frag = href.partition("#")
            target = unquote(target)
            path_ = posixpath.normpath(posixpath.join(posixpath.dirname(name), target)) if target else name
            if path_ not in names:
                errors.append("broken link in %s: %s" % (name, href))
                continue
            if frag:
                try:
                    tdoc = docs[path_]
                except KeyError:
                    continue
                ids = {el.get("id") for el in tdoc.iter() if el.get("id")}
                if frag not in ids:
                    errors.append("missing fragment in %s: %s" % (name, href))

    for name, root in docs.items():
        for img in root.iter("{%s}img" % NS["x"]):
            src = unquote(img.get("src") or "")
            if not src or src.startswith(("http://", "https://", "data:")):
                continue
            target = posixpath.normpath(posixpath.join(posixpath.dirname(name), src))
            if target not in names:
                errors.append("missing image in %s: %s" % (name, src))
            if not (img.get("alt") or "").strip():
                warnings.append("image without alt text: %s" % src)

    print("files: %d   documents: %d   links checked: %d" % (len(names), len(docs), link_count))
    print("nav: %s" % nav_path)
    return report(errors, warnings)


def report(errors, warnings):
    for w in warnings:
        print("WARN  " + w)
    for e in errors:
        print("ERROR " + e)
    print("RESULT:", "PASS" if not errors else "FAIL",
          "(%d errors, %d warnings)" % (len(errors), len(warnings)))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "Basic_Histology_Learning_Text.epub"))
