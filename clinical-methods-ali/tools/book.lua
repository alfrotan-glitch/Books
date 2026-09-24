-- Pandoc Lua filter: format-specific rendering of reading aids.
--   ::: note        -> Typst #note[...] box / DOCX "Note" style / EPUB <div class="note">
--   ::: figure-ph   -> Typst #figph[...] / DOCX "Figure Placeholder" style / EPUB <div class="figure-ph">
-- Also splits chapter headings "فصل X: Title" into a label + title for the Typst chapter opener.

local function typst_wrap(fn, blocks)
  local out = { pandoc.RawBlock("typst", "#" .. fn .. "[") }
  for _, b in ipairs(blocks) do table.insert(out, b) end
  table.insert(out, pandoc.RawBlock("typst", "]"))
  return out
end

function Div(el)
  local cls = el.classes[1]
  local map = { note = {"note", "Note"}, ["figure-ph"] = {"figph", "Figure Placeholder"},
                objectives = {"objectives", "Objectives"}, keypoints = {"keypoints", "Key Points"},
                selftest = {"selftest", "Self Test"},
                redflags = {"redflags", "Red Flags"}, case = {"casebox", "Clinical Case"} }
  local m = map[cls]
  if not m then return nil end
  if FORMAT:match("typst") then
    return typst_wrap(m[1], el.content)
  elseif FORMAT:match("docx") then
    el.attributes["custom-style"] = m[2]
    return el
  end
  return el
end

local function esc(s)
  return (s:gsub("([%[%]#%*_\\@$<>`~])", "\\%1"))
end

function Header(el)
  if el.level ~= 1 or not FORMAT:match("typst") then return nil end
  local txt = pandoc.utils.stringify(el.content)
  local label, title = txt:match("^(فصل [^:]+):%s*(.+)$")
  if not label then label, title = txt:match("^(ضمیمه):%s*(.+)$") end
  if label then
    return pandoc.RawBlock("typst",
      "#heading(level: 1, supplement: [" .. esc(label) .. "])[" .. esc(title) .. "]")
  end
  return pandoc.RawBlock("typst", "#heading(level: 1, supplement: [بخش])[" .. esc(txt) .. "]")
end

-- Ordered-list items with no Arabic-script text (English references) are set LTR.
function OrderedList(el)
  local all_ltr = true
  for _, item in ipairs(el.content) do
    if pandoc.utils.stringify(item):match("[\216-\219][\128-\191]") then
      all_ltr = false
    end
  end
  if not all_ltr then return nil end
  if FORMAT:match("typst") then
    return { pandoc.RawBlock("typst", "#block(width: 100%)[#set text(dir: ltr, lang: \"en\", size: 9pt); #set par(justify: false); #set enum(numbering: n => [#n.])"),
             el, pandoc.RawBlock("typst", "]") }
  elseif FORMAT:match("html") or FORMAT:match("epub") then
    return pandoc.Div({el}, pandoc.Attr("", {"ltr"}, {{"dir", "ltr"}}))
  elseif FORMAT:match("docx") then
    return pandoc.Div({el}, pandoc.Attr("", {}, {{"dir", "ltr"}}))
  end
end

-- Table cells that contain no Arabic-script text (lab values, units, English terms)
-- are set left-to-right so "0.3-1.0 mg/100ml" is not bidi-reordered.
local function is_ltr(blocks)
  local s = pandoc.utils.stringify(blocks)
  return s:match("[%w]") and not s:match("[\216-\219][\128-\191]")
end

local function fix_cell(cell)
  if not is_ltr(cell.contents) then return cell end
  if FORMAT:match("typst") then
    local out = { pandoc.RawBlock("typst", "#text(dir: ltr)[") }
    for _, b in ipairs(cell.contents) do table.insert(out, b) end
    table.insert(out, pandoc.RawBlock("typst", "]"))
    cell.contents = out
  elseif FORMAT:match("html") or FORMAT:match("epub") then
    cell.contents = { pandoc.Div(cell.contents, pandoc.Attr("", {"ltr"}, {{"dir", "ltr"}})) }
  end
  return cell
end

function Table(tbl)
  for _, body in ipairs(tbl.bodies) do
    for _, row in ipairs(body.body) do
      for i, c in ipairs(row.cells) do row.cells[i] = fix_cell(c) end
    end
  end
  return tbl
end

-- Size book figures from their natural width (PNG rendered at 300 ppi) relative to the
-- A5 text block (~110 mm), so small diagrams are not blown up.
local function png_width(path)
  local f = io.open(path, "rb"); if not f then return nil end
  local d = f:read(24); f:close()
  if not d or #d < 24 then return nil end
  local b1, b2, b3, b4 = d:byte(17, 20)
  return ((b1 * 256 + b2) * 256 + b3) * 256 + b4
end

function Image(img)
  if not img.classes:includes("bookfig") then return nil end
  local px = png_width(img.src)
  if px then
    local mm = px / 400 * 25.4   -- figures are rendered at 400 ppi
    local pct = math.min(100, math.floor(mm * 1.25 / 110 * 100 + 0.5))
    img.attributes["width"] = tostring(pct) .. "%"
  end
  if FORMAT == "typst" then  -- vector figure in the PDF
    local svg = img.src:gsub("assets/figures/([%w%-]+)%.png$", "assets/figures/svg/%1.svg")
    local f = io.open(svg, "r")
    if f then f:close(); img.src = svg end
  end
  return img
end

-- PDF only: back-matter marker + subject index with real page numbers (Typst queries <idx> markers)
function Pandoc(doc)
  if FORMAT ~= "typst" then return nil end
  local out, in_index = {}, false
  for _, b in ipairs(doc.blocks) do
    local is_h1 = (b.t == "Header" and b.level == 1) or (b.t == "RawBlock" and b.text:find("#heading%(level: 1") ~= nil)
    if is_h1 then
      local txt = b.t == "Header" and pandoc.utils.stringify(b) or b.text
      if txt:find("فهرست اصطلاحات") then
        table.insert(out, pandoc.RawBlock("typst", '#metadata("backmatter") <backmatter>'))
      end
      in_index = txt:find("فهرست موضوعی") ~= nil
      table.insert(out, b)
    elseif in_index and b.t == "Para" and pandoc.utils.stringify(b):find("شماره فصل") then
      table.insert(out, pandoc.Para({pandoc.Str("اعداد"), pandoc.Space(), pandoc.Str("شماره"), pandoc.Space(), pandoc.Str("صفحه"), pandoc.Space(), pandoc.Str("را"), pandoc.Space(), pandoc.Str("نشان"), pandoc.Space(), pandoc.Str("می‌دهند.")}))
    elseif in_index and b.t == "BulletList" then
      local terms = {}
      for _, item in ipairs(b.content) do
        local first = item[1]
        local term = nil
        if first and first.content then
          for _, il in ipairs(first.content) do
            if il.t == "Strong" then term = pandoc.utils.stringify(il); break end
          end
        end
        if term then table.insert(terms, '"' .. term:gsub('\\', '\\\\'):gsub('"', '\\"') .. '"') end
      end
      table.insert(out, pandoc.RawBlock("typst", "#book-index((" .. table.concat(terms, ", ") .. ",))"))
    else
      table.insert(out, b)
    end
  end
  doc.blocks = out
  return doc
end
