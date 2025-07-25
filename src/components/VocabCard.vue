<template>
  <div class="vocab-card">
    <!-- 自动高亮名词词性（der/die/das） -->
    <h2 class="vocab-card-title">
      <span
        class="article"
        :class="nomenObjUnderlineClass"
      >
        {{ article }} <span class="noun">{{ noun }}</span>
      </span>
    </h2>

    <!-- 名词类 -->
    <template v-if="deck === 'nomen_obj' || deck === 'nomen_people'">
      <p v-if="data.复数" class="vocab-card-plural">{{ data.复数 }}</p>
      <p class="vocab-card-meaning">= {{ data.意思 }}</p>
    </template>

    <!-- 动词原型 -->
    <template v-else-if="deck === 'verben_base'">
      <p class="vocab-card-meaning">Präsens: {{ data["现在(第三人称单数)"] }}</p>
      <p class="vocab-card-meaning">Präteritum: {{ data["过去(第三人称单数)"] }}</p>
      <p class="vocab-card-meaning">Perfekt: {{ data["完成"] }}</p>
      <p class="vocab-card-meaning">= {{ data["意思"] }}</p>
    </template>

    <!-- 动词短语 -->
    <template v-else-if="deck === 'verben_phrasen'">
      <p class="vocab-card-meaning">= {{ data["意思"] }}</p>
    </template>

    <!-- 形容词比较级 -->
    <template v-else-if="deck === 'adj_steigerung'">
      <p class="vocab-card-meaning">Comparative: {{ data["比较级"] }}</p>
      <p class="vocab-card-meaning">Superlative: {{ data["最高级"] }}</p>
      <p class="vocab-card-meaning">= {{ data["意思"] }}</p>
    </template>

    <!-- 普通形容词等 -->
    <template v-else>
      <p class="vocab-card-meaning">= {{ data["意思"] }}</p>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: Object,
  deck: String
})

const deckNameMap = {
  nomen_obj: "Nomen - Objekte",
  nomen_people: "Nomen - Personen",
  verben_base: "Verben - Grundformen",
  verben_phrasen: "Verben - Redewendungen",
  adj_base: "Adjektive - allgemein",
  adj_steigerung: "Adjektive - Steigerung",
};

// 这里用 props.deck 替换 deckId
const deckName = computed(() => deckNameMap[props.deck] || props.deck);

const rawWord = computed(() =>
  props.data["单数"] || props.data["原型"] || props.data["词组"] || props.data["单词"] || ""
)

const article = computed(() => rawWord.value.split(" ")[0] || "")
const noun = computed(() => rawWord.value.split(" ").slice(1).join(" ") || "")

const nomenObjUnderlineClass = computed(() => {
  if (props.deck === 'nomen_obj') {
    switch (article.value) {
      case "der": return "border-blue";
      case "die": return "border-pink";
      case "das": return "border-gray";
      default: return "";
    }
  }
  return "no-underline";
});
</script>
