// npm xlsx fs-extra

// node tools/excel2json.js
const XLSX = require("xlsx");
const fs = require("fs-extra");
const path = require("path");

const maps = [
  { file: "_A1/Nomen.xlsx", sheet: "Obj", out: "nomen_obj" },
  { file: "_A1/Nomen.xlsx", sheet: "人",   out: "nomen_people" },
  { file: "_A1/Verben.xlsx", sheet: "Grund Verben",  out: "verben_base" },
  { file: "_A1/Verben.xlsx", sheet: "Verb Phrasen",  out: "verben_phrasen" },
  { file: "_A1/Adjektive.xlsx", sheet: "Adj",   out: "adj_base" },
  { file: "_A1/Adjektive.xlsx", sheet: "Gut",   out: "adj_steigerung" },
];

fs.ensureDirSync(path.join(__dirname, "..", "public", "data"));

maps.forEach(({ file, sheet, out }) => {
  const wb = XLSX.readFile(path.join(__dirname, "..", file));
  const ws = wb.Sheets[sheet];
  const json = XLSX.utils.sheet_to_json(ws, { defval: "" }); // 空单元格也保留
  fs.outputJsonSync(path.join(__dirname, "..", "public", "data", `${out}.json`), json, { spaces: 2 });
  console.log(`✓ ${out}.json created`);
});
