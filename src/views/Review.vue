<template>
  <div class="deck-container">
    <div class="back-actions">
      <button class="back-btn" @click="goHome">◁ Back</button>
    </div>
    <h1 class="deck-title">Review</h1>

    <div v-if="loading" class="review-status">loading...</div>

    <template v-else-if="queue.length > 0">
      <p class="review-count">{{ queue.length }} remaining</p>
      <div class="deck-list">
        <VocabCard
          v-if="currentCard"
          :key="cardKey"
          :data="currentCard.data"
          :deck="currentCard.deck"
          :quizMode="true"
          :choices="currentChoices"
          @answer="handleAnswer"
        />
      </div>
      <div class="deck-actions">
        <button
          class="next-btn"
          :disabled="answeredCurrent === null"
          @click="nextCard"
        >▷ Next</button>
      </div>
    </template>

    <div v-else class="review-status">👍</div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import VocabCard from '../components/VocabCard.vue'
import {
  loadWrongCards, removeWrongCard, generateChoices
} from '../utils/wrongCards'
import { recordAnswer } from '../utils/stats'

const router = useRouter()

const queue          = ref([])
const currentIndex   = ref(0)
const answeredCurrent = ref(null)  // null = 未答, true = 对, false = 错
const currentChoices = ref([])
const loading        = ref(true)
const cardKey        = ref(0)
const poolCache      = {}

const currentCard = computed(() => queue.value[currentIndex.value] || null)

async function loadPool(deck) {
  if (poolCache[deck]) return
  if (deck === 'phrasen') {
    const [r1, r2] = await Promise.all([
      fetch(`${import.meta.env.BASE_URL}data/verben_phrasen.json`),
      fetch(`${import.meta.env.BASE_URL}data/adv_phrasen.json`),
    ])
    const [d1, d2] = await Promise.all([r1.json(), r2.json()])
    poolCache[deck] = [...d1, ...d2]
  } else {
    const res = await fetch(`${import.meta.env.BASE_URL}data/${deck}.json`)
    poolCache[deck] = await res.json()
  }
}

function updateChoices() {
  if (!currentCard.value) return
  const { deck, data } = currentCard.value
  currentChoices.value = generateChoices(data, poolCache[deck] || [], deck)
}

function handleAnswer(isCorrect) {
  answeredCurrent.value = isCorrect
  recordAnswer(isCorrect)
  if (isCorrect) {
    removeWrongCard(currentCard.value.deck, currentCard.value.data)
  }
}

function nextCard() {
  if (answeredCurrent.value === null) return
  if (answeredCurrent.value) {
    // 答对：从队列移除
    queue.value.splice(currentIndex.value, 1)
    if (currentIndex.value >= queue.value.length) currentIndex.value = 0
  } else {
    // 答错：移到队列末尾
    const card = queue.value.splice(currentIndex.value, 1)[0]
    queue.value.push(card)
    if (currentIndex.value >= queue.value.length) currentIndex.value = 0
  }
  answeredCurrent.value = null
  cardKey.value++
  updateChoices()
}

function goHome() {
  router.push('/')
}

onMounted(async () => {
  queue.value = loadWrongCards()
  const decks = [...new Set(queue.value.map(c => c.deck))]
  await Promise.all(decks.map(loadPool))
  updateChoices()
  loading.value = false
})
</script>
