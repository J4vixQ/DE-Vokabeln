<template>
  <div class="vocab-card">
    <!-- 只在非人物类时渲染标题 -->
    <h2 v-if="deck !== 'nomen_people'" class="vocab-card-title">
      <span
        class="article"
        :class="nomenObjUnderlineClass"
      >
        {{ article }} <span class="noun">{{ noun }}</span>
      </span>
    </h2><!--
   --><!-- 这样下方紧接着内容块，没有空白行 -->

    <!-- 人物名词内容 -->
    <template v-if="deck === 'nomen_people' && (hasMale || hasFemale)">
      <div class="gender-blocks">
        <!-- 男性 -->
        <div v-if="hasMale" class="person-block male">
          <div>
            <span class="article">{{ getArticle(data['单数男']) }}</span>
            <span class="noun">{{ getNoun(data['单数男']) }}</span>
          </div>
          <div class="plural">{{ data['复数男'] }}</div>
          <div class="meaning">{{ data['意思男'] }}</div>
        </div>
        <!-- 女性 -->
        <div v-if="hasFemale" class="person-block female">
          <div>
            <span class="article">{{ getArticle(data['单数女']) }}</span>
            <span class="noun">{{ getNoun(data['单数女']) }}</span>
          </div>
          <div class="plural">{{ data['复数女'] }}</div>
          <div class="meaning">{{ data['意思女'] }}</div>
        </div>
        <p class="vocab-card-sentence"> {{ data["例句"] }}</p>
      </div>
    </template>


    <!-- 名词类 -->
    <template v-else-if="deck === 'nomen_obj'">
      <p v-if="data.复数" class="vocab-card-plural">{{ data.复数 }}</p>
      <p class="vocab-card-meaning">= {{ data.意思 }}</p>
      <p class="vocab-card-sentence"> {{ data["例句"] }}</p>
    </template>

    <!-- 动词原型 -->
    <template v-else-if="deck === 'verben_base'">
      <p class="vocab-card-meaning">{{ data["现在"] }}</p>
      <p class="vocab-card-meaning">{{ data["过去"] }}</p>
      <p class="vocab-card-meaning">{{ data["完成"] }}</p>
      <p class="vocab-card-meaning">= {{ data["意思"] }}</p>
      <p class="vocab-card-sentence"> {{ data["例句"] }}</p>
    </template>

    <!-- 动词短语 -->
    <template v-else-if="deck === 'verben_phrasen'">
      <p class="vocab-card-meaning">= {{ data["意思"] }}</p>
      <p class="vocab-card-sentence"> {{ data["例句"] }}</p>
    </template>

    <!-- 形容词比较级 -->
    <template v-else-if="deck === 'adj_steigerung'">
      <p class="vocab-card-meaning">{{ data["比较级"] }}</p>
      <p class="vocab-card-meaning">{{ data["最高级"] }}</p>
      <p class="vocab-card-meaning">= {{ data["意思"] }}</p>
      <p class="vocab-card-sentence"> {{ data["例句"] }}</p>
    </template>

    <!-- 普通形容词等 -->
    <template v-else-if="deck === 'adj_base'">
      <p class="vocab-card-meaning">= {{ data["意思"] }}</p>
      <p class="vocab-card-sentence"> {{ data["例句"] }}</p>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: Object,
  deck: String
})

const hasMale = computed(() => !!(props.data["单数男"] || props.data["意思男"]));
const hasFemale = computed(() => !!(props.data["单数女"] || props.data["意思女"]));
function getArticle(word = "") {
  return word.split(" ")[0] || "";
}
function getNoun(word = "") {
  return word.split(" ").slice(1).join(" ") || "";
}

const deckNameMap = {
  nomen_obj: "Nomen - Objekte",
  nomen_people: "Nomen - Personen",
  verben_base: "Verben - Grundformen",
  verben_phrasen: "Verben - Redewendungen",
  adj_base: "Adjektive - allgemein",
  adj_steigerung: "Adjektive - Steigerung",
};

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
