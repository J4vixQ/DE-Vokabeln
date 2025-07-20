// 工具：随机整数
const rand = max => Math.floor(Math.random() * max);

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

    const card = document.getElementById("card");
    const render = () => {
      const item = data[rand(data.length)];
      if (item === current) return render(); // 避免重复
      current = item;

      // 根据不同 deck 生成不同格式
      switch (deck) {
        case "nomen_obj":
        case "nomen_people":
          card.innerHTML = `
            <h2>${item["单数"] || "(—)"}</h2>
            <p>${item["复数"]}</p>
            <p>意：${item["意思"]}</p>`;
          break;

        case "verben_base":
          card.innerHTML = `
            <h2>${item["原型"]}</h2>
            <p>Präsens: ${item["现在(第三人称单数)"]}</p>
            <p>Präteritum: ${item["过去(第三人称单数)"]}</p>
            <p>Perfekt: ${item["完成"]}</p>
            <p>意：${item["意思"]}</p>`;
          break;

        case "verben_phrasen":
          card.innerHTML = `
            <h2>${item["词组"]}</h2>
            <p>意：${item["意思"]}</p>`;
          break;

        case "adj_base":
          card.innerHTML = `
            <h2>${item["单词"]}</h2>
            <p>意：${item["意思"]}</p>`;
          break;

        case "adj_steigerung":
          card.innerHTML = `
            <h2>${item["原型"]}</h2>
            <p>Comparative: ${item["比较级"]}</p>
            <p>Superlative: ${item["最高级"]}</p>
            <p>意：${item["意思"]}</p>`;
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
