// npm init -y
// npm i xlsx fs-extra

// node tools/excel2json.js
const XLSX = require("xlsx");
const fs = require("fs-extra");
const path = require("path");

const maps = [
  { file: "Nomen.xlsx", sheet: "Obj", out: "nomen_obj" },
  { file: "Nomen.xlsx", sheet: "人",   out: "nomen_people" },
  { file: "Verben.xlsx", sheet: "Grund Verben",  out: "verben_base" },
  { file: "Verben.xlsx", sheet: "Verb Phrasen",  out: "verben_phrasen" },
  { file: "Adjektive.xlsx", sheet: "Adj",   out: "adj_base" },
  { file: "Adjektive.xlsx", sheet: "Gut",   out: "adj_steigerung" },
];

maps.forEach(({ file, sheet, out }) => {
  const wb = XLSX.readFile(path.join("..", file));
  const ws = wb.Sheets[sheet];
  const json = XLSX.utils.sheet_to_json(ws, { defval: "" }); // 空单元格也保留
  fs.outputJsonSync(path.join(__dirname, "..", "data", `${out}.json`), json, { spaces: 2 });
  console.log(`✓ ${out}.json created`);
});
