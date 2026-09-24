-- Pandoc Lua filter: format-specific rendering of reading aids.
--   ::: note        -> Typst #note[...] box / DOCX "Note" style / EPUB <div class="note">
--   ::: figure-ph   -> Typst #figph[...] / DOCX "Figure Placeholder" style / EPUB <div class="figure-ph">
-- Also splits chapter headings "فصل X: Title" into a label + title for the Typst chapter opener.

local function typst_wrap(fn, blocks)
  local out = { pandoc.RawBlock("typst", "#" .. fn .. "[") }
  for i, b in ipairs(blocks) do
    -- keep a bold box title on the same page as the text that follows it
    if i == 1 and #blocks > 1 and b.t == "Para" and b.content[1] and b.content[1].t == "Strong" then
      table.insert(out, pandoc.RawBlock("typst", "#block(sticky: true, above: 0pt, below: 0.65em)["))
      table.insert(out, b)
      table.insert(out, pandoc.RawBlock("typst", "]"))
    else
      table.insert(out, b)
    end
  end
  table.insert(out, pandoc.RawBlock("typst", "]"))
  return out
end

function Div(el)
  local cls = el.classes[1]
  local map = { note = {"note", "Note"}, ["figure-ph"] = {"figph", "Figure Placeholder"},
                objectives = {"objectives", "Objectives"}, keypoints = {"keypoints", "Key Points"},
                selftest = {"selftest", "Self Test"},
                redflags = {"redflags", "Red Flags"}, case = {"casebox", "Clinical Case"},
                story = {"story", "Story"}, bigidea = {"bigidea", "Big Idea"}, rule = {"rule", "Bedside Rule"},
                evidence = {"evidence", "Evidence"}, pitfall = {"pitfall", "Pitfall"}, expert = {"expert", "Expert"},
                summary = {"summary", "Summary"}, practice = {"practice", "Practice"}, osce = {"selftest", "OSCE"} }
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
  if not label then label, title = txt:match("^(بخش [^:]+):%s*(.+)$") end
  if label then
    return pandoc.RawBlock("typst",
      "#heading(level: 1, supplement: [" .. esc(label) .. "])[" .. esc(title) .. "]")
  end
  return pandoc.RawBlock("typst", "#heading(level: 1, supplement: none)[" .. esc(txt) .. "]")
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
local function is_ar_lead(b) return b and b >= 0xD8 and b <= 0xDB end
-- does `text` contain `term` as a whole word (no Arabic/Latin letter glued before; no letter glued after)?
local function has_term(text, term)
  local init = 1
  while true do
    local i, j = text:find(term, init, true)
    if not i then return false end
    local ok = true
    if i > 2 and is_ar_lead(text:byte(i - 2)) then ok = false end
    if i > 1 and text:sub(i - 1, i - 1):match("[%w]") then ok = false end
    local nb = text:byte(j + 1)
    if is_ar_lead(nb) or (nb and string.char(nb):match("[%w]")) then ok = false end
    if ok then return true end
    init = j + 1
  end
end

local function h1text(b)
  if b.t == "Header" and b.level == 1 then return pandoc.utils.stringify(b) end
  if b.t == "RawBlock" and b.text:find("#heading%(level: 1") then return b.text end
  return nil
end

-- collect index terms from the index appendix
local function index_terms(blocks)
  local in_index, terms = false, {}
  for _, b in ipairs(blocks) do
    local h = h1text(b)
    if h then
      in_index = h:find("فهرست موضوعی") ~= nil
    elseif in_index and b.t == "BulletList" then
      for _, item in ipairs(b.content) do terms[#terms + 1] = pandoc.utils.stringify(item[1]) end
    end
  end
  return terms
end

-- mark the first occurrence of each term in every level-1/2 section with #metadata(term) <idx>
local function mark_terms(blocks, terms)
  local seen, stop, pending = {}, false, {}
  local function tstr(t) return '"' .. t:gsub('\\', '\\\\'):gsub('"', '\\"') .. '"' end
  local visit
  local function mark_inlines(el)
    local txt = pandoc.utils.stringify(el)
    for _, t in ipairs(terms) do
      if not seen[t] and has_term(txt, t) then
        seen[t] = true
        el.content:insert(pandoc.RawInline("typst", "#metadata(" .. tstr(t) .. ") <idx>"))
      end
    end
  end
  visit = function(bl)
    for _, b in ipairs(bl) do
      if stop then return end
      local h = h1text(b)
      if h then
        if h:find("ضمیمه") then stop = true; return end
        seen = {}
      elseif b.t == "Header" and b.level >= 2 then
        -- a term in a section heading marks the main discussion (metadata goes into a following block)
        local txt = pandoc.utils.stringify(b)
        local hits = {}
        for _, t in ipairs(terms) do
          if has_term(txt, t) then hits[#hits + 1] = "#metadata(" .. tstr(t) .. ") <idx>"; seen[t] = true end
        end
        if #hits > 0 then pending[#pending + 1] = {b, table.concat(hits, " ")} end
      elseif b.t == "Para" or b.t == "Plain" then mark_inlines(b)
      elseif b.t == "Div" or b.t == "BlockQuote" then visit(b.content)
      elseif b.t == "BulletList" or b.t == "OrderedList" then
        for _, item in ipairs(b.content) do visit(item) end
      elseif b.t == "Table" then
        for _, body in ipairs(b.bodies) do
          for _, row in ipairs(body.body) do
            for _, cell in ipairs(row.cells) do visit(cell.contents) end
          end
        end
      end
    end
  end
  visit(blocks)
  for _, pr in ipairs(pending) do
    for i, b in ipairs(blocks) do
      if b == pr[1] then table.insert(blocks, i + 1, pandoc.RawBlock("typst", pr[2])); break end
    end
  end
end

function Pandoc(doc)
  if FORMAT ~= "typst" then
    -- no page numbers outside the PDF: drop the subject index
    local out, skip = {}, false
    for _, b in ipairs(doc.blocks) do
      if b.t == "Header" and b.level == 1 then skip = pandoc.utils.stringify(b):find("فهرست موضوعی") ~= nil end
      if not skip then out[#out + 1] = b end
    end
    doc.blocks = out
    return doc
  end
  local terms = index_terms(doc.blocks)
  if #terms > 0 then mark_terms(doc.blocks, terms) end
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
