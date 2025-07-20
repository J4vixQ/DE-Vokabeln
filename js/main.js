// 写死类别数组即可；id 对应 data/ 下的 json 文件名
const categories = [
  { id: "nomen_obj", label: "Nomen - Objekte" },
  { id: "nomen_people", label: "Nomen - Personen" },
  { id: "verben_base", label: "Verben - Grundformen" },
  { id: "verben_phrasen", label: "Verben - Redewendungen" },
  { id: "adj_base", label: "Adjektive - allgemein" },
  { id: "adj_steigerung", label: "Adjektive - Steigerung" },
];

const grid = document.getElementById("category-grid");
categories.forEach(c => {
  const btn = document.createElement("button");
  btn.textContent = c.label;
  btn.onclick = () => location.href = `deck.html?deck=${c.id}`;
  grid.appendChild(btn);
});
