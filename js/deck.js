// 工具：随机整数
const rand = max => Math.floor(Math.random() * max);

// 工具：为德语名词加性别样式
const formatGenderNoun = word => {
  if (!word) return "(—)";
  if (word.startsWith("der ")) {
    return `<span class="gender-masc">${word}</span>`;
  } else if (word.startsWith("die ")) {
    return `<span class="gender-fem">${word}</span>`;
  } else if (word.startsWith("das ")) {
    return `<span class="gender-neut">${word}</span>`;
  }
  return word;
};

// 1) 解析 query string
const params = new URLSearchParams(location.search);
const deck = params.get("deck");
if (!deck) location.href = "index.html"; // 无参就跳回

// 2) 载入对应 JSON
fetch(`data/${deck}.json`)
  .then(r => r.json())
  .then(data => {
    document.title += ` · ${deck}`;
    let current = null;

    const container = document.getElementById("card-container");

    const render = () => {
      const item = data[rand(data.length)];
      if (item === current) return render(); // 避免重复
      current = item;

      // 根据不同 deck 生成不同格式
      switch (deck) {
        case "nomen_obj":
          container.innerHTML = `
            <div class="card">
              <h2>${formatGenderNoun(item["单数"])}</h2>
              <p>${item["复数"] || ""}</p>
              <p>意：${item["意思"] || ""}</p>
            </div>`;
          break;

        case "nomen_people": {
          container.innerHTML = "";

          const createCard = (title, plural, meaning) => {
            const div = document.createElement("div");
            div.className = "card";
            div.innerHTML = `
              <h2>${formatGenderNoun(title)}</h2>
              ${plural ? `<p>${plural}</p>` : ""}
              ${meaning ? `<p>意：${meaning}</p>` : ""}
            `;
            return div;
          };

          const hasMale = item["单数男"] || item["复数男"] || item["意思男"];
          const hasFemale = item["单数女"] || item["复数女"] || item["意思女"];

          if (hasMale) {
            container.appendChild(createCard(
              item["单数男"] || "(—)",
              item["复数男"] || "",
              item["意思男"] || ""
            ));
          }

          if (hasFemale) {
            container.appendChild(createCard(
              item["单数女"] || "(—)",
              item["复数女"] || "",
              item["意思女"] || ""
            ));
          }
          break;
        }

        case "verben_base":
          container.innerHTML = `
            <div class="card">
              <h2>${item["原型"]}</h2>
              <p>Präsens: ${item["现在(第三人称单数)"]}</p>
              <p>Präteritum: ${item["过去(第三人称单数)"]}</p>
              <p>Perfekt: ${item["完成"]}</p>
              <p>意：${item["意思"]}</p>
            </div>`;
          break;

        case "verben_phrasen":
          container.innerHTML = `
            <div class="card">
              <h2>${item["词组"]}</h2>
              <p>意：${item["意思"]}</p>
            </div>`;
          break;

        case "adj_base":
          container.innerHTML = `
            <div class="card">
              <h2>${item["单词"]}</h2>
              <p>意：${item["意思"]}</p>
            </div>`;
          break;

        case "adj_steigerung":
          container.innerHTML = `
            <div class="card">
              <h2>${item["原型"]}</h2>
              <p>Comparative: ${item["比较级"]}</p>
              <p>Superlative: ${item["最高级"]}</p>
              <p>意：${item["意思"]}</p>
            </div>`;
          break;
      }

    };

    document.getElementById("next-btn").onclick = render;
    render(); // 首次渲染
  })
  .catch(err => {
    document.getElementById("card").textContent = "数据加载失败！";
    console.error(err);
  });
