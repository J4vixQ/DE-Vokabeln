<template>
  <div class="deck-container">
    <div class="back-actions">
      <button class="back-btn" @click="goHome">◁ Back</button>
    </div>
    <h1 class="deck-title">{{ deckName }}</h1>
    <div class="deck-list">
      <VocabCard
        v-for="(item, idx) in currentCards"
        :key="idx"
        :data="item"
        :deck="deckId"
      />
    </div>
    <div class="deck-actions">
      <button class="next-btn" @click="showRandomCard">▷ Next</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import VocabCard from '../components/VocabCard.vue';

// 1. 获取路由参数
const route = useRoute();
const router = useRouter();
function goHome() {
  router.push('/');
}
const deckId = route.params.deckId;

// 2. 卡片标题映射
const deckNameMap = {
  nomen_obj: "Nomen - Objekte",
  nomen_people: "Nomen - Personen",
  verben_base: "Verben - Grundformen",
  verben_phrasen: "Verben - Redewendungen",
  adj_base: "Adjektive - allgemein",
  adj_steigerung: "Adjektive - Steigerung",
};
const deckName = deckNameMap[deckId] || deckId;

// 3. 卡片数据
const allData = ref([]);
const currentCards = ref([]);

// 4. 随机索引
const rand = max => Math.floor(Math.random() * max);

// 5. 随机抽取一条/多条卡片
const showRandomCard = () => {
  if (!allData.value.length) return;
  const item = allData.value[rand(allData.value.length)];
  currentCards.value = [];

  if (deckId === 'nomen_people') {
    const hasMale = item["单数男"] || item["复数男"] || item["意思男"];
    const hasFemale = item["单数女"] || item["复数女"] || item["意思女"];
    if (hasMale) {
      currentCards.value.push({
        单数: item["单数男"],
        复数: item["复数男"],
        意思: item["意思男"]
      });
    }
    if (hasFemale) {
      currentCards.value.push({
        单数: item["单数女"],
        复数: item["复数女"],
        意思: item["意思女"]
      });
    }
  } else {
    currentCards.value.push(item);
  }
};

// 6. 挂载时加载数据
onMounted(async () => {
  const res = await fetch(`/data/${deckId}.json`);
  allData.value = await res.json();
  showRandomCard();
});
</script>