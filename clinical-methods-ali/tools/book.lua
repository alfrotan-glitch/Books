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
  if cls ~= "note" and cls ~= "figure-ph" then return nil end
  if FORMAT:match("typst") then
    return typst_wrap(cls == "note" and "note" or "figph", el.content)
  elseif FORMAT:match("docx") then
    el.attributes["custom-style"] = (cls == "note") and "Note" or "Figure Placeholder"
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
