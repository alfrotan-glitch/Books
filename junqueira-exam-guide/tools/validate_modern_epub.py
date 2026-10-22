#!/usr/bin/env python3
"""Reader-experience regression checks for the modern EPUB 3 edition.

These checks complement EPUBCheck and do not certify accessibility in every
device/reader. No browser or internet connection is required.
"""
from pathlib import Path
from zipfile import ZipFile
from urllib.parse import unquote
from xml.etree import ElementTree as ET
import re
import posixpath

EPUB = Path(__file__).resolve().parents[1] / "Basic_Histology_Learning_Text.epub"
N = {
    "x": "http://www.w3.org/1999/xhtml",
    "e": "http://www.idpf.org/2007/ops",
    "o": "http://www.idpf.org/2007/opf",
    "d": "http://purl.org/dc/elements/1.1/",
}


def main():
    with ZipFile(EPUB) as z:
        files = set(z.namelist())
        css = z.read("EPUB/styles/stylesheet1.css").decode("utf-8")
        for required in (".table-scroll", "prefers-color-scheme: dark",
                         "font-family:", "max-width: 100%", "focus"):
            assert required in css, f"Missing reader-friendly CSS feature: {required}"

        spine = ET.fromstring(z.read("EPUB/content.opf"))
        metadata = spine.find("o:metadata", N)
        for name in ("description", "subject"):
            assert metadata.find(f"d:{name}", N) is not None, f"Missing {name} metadata"

        docs = sorted(x for x in files if re.fullmatch(r"EPUB/text/ch\d+\.xhtml", x))
        assert 38 <= len(docs) <= 65, (
            f"Expected chapter-level split into manageable XHTML files, got {len(docs)}"
        )
        assert max(len(z.read(x)) for x in docs) < 130000, (
            "A chapter XHTML file is too large for low-memory e-readers"
        )

        numbers = set()
        figures = []
        all_tables = 0
        note_count = 0
        for name in docs:
            root = ET.fromstring(z.read(name))
            body = root.find("x:body", N)
            assert body is not None and len("".join(body.itertext()).strip()) >= 8, (
                f"Blank chapter file: {name}"
            )
            for heading in root.findall(".//x:h2", N):
                m = re.match(r"^(\d{1,2})\s*·", "".join(heading.itertext()).strip())
                if m:
                    numbers.add(int(m.group(1)))
            for table in root.findall(".//x:table", N):
                all_tables += 1
            for wrapper in root.findall(".//x:div[@class='table-scroll']", N):
                assert wrapper.find("x:table", N) is not None, (
                    f"Empty table-scroller in {name}"
                )
            for img in root.findall(".//x:img", N):
                assert (img.get("alt") or "").strip(), f"Missing accessible image alt in {name}"
            for fig in root.findall(".//x:figure", N):
                if fig.find("x:img", N) is not None:
                    figures.append((name.removeprefix("EPUB/"), fig.get("id")))
            note_count += len(root.findall(".//x:blockquote[@class]", N))
            assert len(root.findall(".//x:table", N)) == len(
                root.findall(".//x:div[@class='table-scroll']", N)
            ), f"At least one table lacks a scrollable wrapper in {name}"

        assert numbers == set(range(1, 25)), (
            f"Missing or duplicated major chapter number: {sorted(numbers)}"
        )
        assert len(figures) == 9, f"Nine schematic figures expected, got {len(figures)}"
        assert all(id for _, id in figures), "Illustration needs an internal anchor"
        assert all_tables >= 75, f"Only {all_tables} accessible comparison tables found"
        assert note_count >= 20, "Semantic teaching callouts appear missing"

        nav = ET.fromstring(z.read("EPUB/nav.xhtml"))
        toc = nav.find(".//x:nav[@id='toc']", N)
        assert toc is not None, "Navigable table of contents is missing"
        links = toc.findall(".//x:a", N)
        assert len(links) >= 30, f"Too few ToC anchors: {len(links)}"
        illustration_nav = None
        for n in nav.findall(".//x:nav", N):
            if n.get("{" + N["e"] + "}type") == "loi":
                illustration_nav = n
                break
        assert illustration_nav is not None, "Illustration navigation is missing"
        figlinks = illustration_nav.findall(".//x:a", N)
        assert len(figlinks) == 9, f"Expected nine illustration navigation links: {len(figlinks)}"
        image_targets = {p + "#" + ident for p, ident in figures}
        assert {unquote(a.get("href", "")) for a in figlinks} == image_targets, (
            "Illustration list links are not matched to illustration anchors"
        )

        # No remote image, stylesheets, fonts or scripts. Educational hyperlinks
        # to university microscope resources are allowed.
        assert not any("http" in x and x.endswith(".css") for x in files)
        print(f"Modern EPUB PASS: {len(docs)} reflow sections, 24 numbered chapters, "
              f"{all_tables} scrollable tables, {note_count} styled learning notes, "
              "nine illustrated jump links, ebook-safe metadata and styling.")


if __name__ == "__main__":
    main()
