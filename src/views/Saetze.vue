<template>
  <div class="deck-container">
    <div class="back-actions">
      <button class="back-btn" @click="goHome">◁ Back</button>
    </div>
    <h1 class="deck-title">Sätze</h1>
    <div class="deck-list">
      <div v-if="current" class="vocab-card">
        <p class="saetze-sentence">{{ current['例句'] }}</p>
        <p v-if="current['翻译']" class="vocab-card-translation">{{ current['翻译'] }}</p>
      </div>
    </div>
    <div class="deck-actions">
      <button class="next-btn" @click="showRandom">▷ Next</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { loadDeck } from '../utils/decks'

const router = useRouter()

const current = ref(null)   // { 例句, 翻译 }
let sentences = []

// 随机一句，不和上一句重复
function showRandom() {
  if (!sentences.length) return
  let next
  do {
    next = sentences[Math.floor(Math.random() * sentences.length)]
  } while (sentences.length > 1 && next === current.value)
  current.value = next
}

function goHome() {
  router.push('/')
}

onMounted(async () => {
  sentences = await loadDeck('sentences')
  showRandom()
})
</script>

<style scoped>
.saetze-sentence {
  font-size: 1.15rem;
  line-height: 1.5;
  color: var(--fg);
}
</style>
