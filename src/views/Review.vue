<template>
  <div class="deck-container">
    <div class="back-actions">
      <button class="back-btn" @click="goBack">◁ Back</button>
    </div>
    <h1 class="deck-title">Review{{ mode ? (mode === 'quiz' ? ' · Quiz' : ' · Ansehen') : '' }}</h1>

    <div v-if="loading" class="review-status">loading...</div>

    <div v-else-if="!queue.length" class="review-status">👍</div>

    <!-- 选择模式 -->
    <div v-else-if="!mode" class="categories-list">
      <p class="review-count">{{ queue.length }} Karten</p>
      <button class="card-link" @click="start('view')">Ansehen</button>
      <button class="card-link" @click="start('quiz')">Quiz</button>
    </div>

    <!-- 看模式：翻完一轮 -->
    <div v-else-if="mode === 'view' && currentIndex >= queue.length" class="categories-list">
      <p class="review-count">Fertig</p>
      <button class="card-link" @click="start('quiz')">Jetzt Quiz</button>
    </div>

    <template v-else>
      <p class="review-count">
        {{ mode === 'view' ? `${currentIndex + 1} / ${queue.length}` : `${queue.length} remaining` }}
      </p>
      <div class="deck-list">
        <VocabCard
          v-if="currentCard"
          :key="cardKey"
          :data="currentCard.data"
          :deck="currentCard.deck"
          :quizMode="mode === 'quiz'"
          :choices="mode === 'quiz' ? currentChoices : null"
          @answer="handleAnswer"
        />
      </div>
      <div class="deck-actions">
        <button class="hide-btn" @click="hideCurrent">Ausblenden</button>
        <button
          class="next-btn"
          :disabled="mode === 'quiz' && answeredCurrent === null"
          @click="nextCard"
        >▷ Next</button>
      </div>
    </template>

    <div v-if="undo" class="undo-toast">
      <span>{{ undoWord }} ausgeblendet</span>
      <button class="undo-btn" @click="undoHide">Rückgängig</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import VocabCard from '../components/VocabCard.vue'
import { loadWrongCards, removeWrongCard, addWrongCard, generateChoices, getCardKey } from '../utils/wrongCards'
import { hiddenKeySet, hideCard, unhideKey } from '../utils/hiddenCards'
import { loadDeck } from '../utils/decks'
import { recordAnswer, recordView } from '../utils/stats'
import { recordResult } from '../utils/cardScores'

const router = useRouter()

const mode            = ref(null)  // null = 未选, 'view' | 'quiz'
const queue           = ref([])
const currentIndex    = ref(0)
const answeredCurrent = ref(null)  // null = 未答, true = 对, false = 错
const currentChoices  = ref([])
const loading         = ref(true)
const cardKey         = ref(0)
const undo            = ref(null)  // { item, idx, wasWrong, timer }
const poolCache       = {}
let penalized         = new Set()  // 本轮已扣过分的卡：同一轮里重复答错只扣一次

const currentCard = computed(() => queue.value[currentIndex.value] || null)
const undoWord    = computed(() => undo.value && getCardKey(undo.value.item.deck, undo.value.item.data).split('|')[1])

function loadQueue() {
  const hidden = hiddenKeySet()
  queue.value = loadWrongCards().filter(c => !hidden.has(getCardKey(c.deck, c.data)))
}

// 换到 currentIndex 指向的卡：重置作答状态
function showCurrent({ countView = true } = {}) {
  answeredCurrent.value = null
  cardKey.value++
  if (!currentCard.value) return
  if (mode.value === 'quiz') {
    const { deck, data } = currentCard.value
    currentChoices.value = generateChoices(data, poolCache[deck] || [], deck)
  } else if (countView) {
    recordView()
  }
}

function start(m) {
  mode.value = m
  loadQueue()
  currentIndex.value = 0
  penalized = new Set()
  showCurrent()
}

// 看模式只翻，不改熟悉度、不动错题列表
function handleAnswer(isCorrect) {
  const { deck, data } = currentCard.value
  const key = getCardKey(deck, data)
  answeredCurrent.value = isCorrect
  recordAnswer(isCorrect)
  if (isCorrect || !penalized.has(key)) recordResult(deck, data, isCorrect)
  if (isCorrect) {
    removeWrongCard(deck, data)
  } else {
    penalized.add(key)
  }
}

function nextCard() {
  if (mode.value === 'view') {
    currentIndex.value++
  } else {
    if (answeredCurrent.value === null) return
    // 答对：从队列移除；答错：移到队列末尾
    const card = queue.value.splice(currentIndex.value, 1)[0]
    if (!answeredCurrent.value) queue.value.push(card)
    if (currentIndex.value >= queue.value.length) currentIndex.value = 0
  }
  showCurrent()
}

function hideCurrent() {
  const idx  = currentIndex.value
  const item = queue.value[idx]
  const key  = getCardKey(item.deck, item.data)
  const wasWrong = loadWrongCards().some(c => getCardKey(c.deck, c.data) === key)
  hideCard(item.deck, item.data)
  removeWrongCard(item.deck, item.data)
  queue.value.splice(idx, 1)
  if (mode.value === 'quiz' && idx >= queue.value.length) currentIndex.value = 0

  if (undo.value) clearTimeout(undo.value.timer)
  undo.value = { item, idx, wasWrong, timer: setTimeout(() => { undo.value = null }, 5000) }
  showCurrent()
}

function undoHide() {
  const { item, idx, wasWrong, timer } = undo.value
  clearTimeout(timer)
  undo.value = null
  unhideKey(getCardKey(item.deck, item.data))
  if (wasWrong) addWrongCard(item.deck, item.data)
  if (!mode.value) return
  queue.value.splice(idx, 0, item)
  currentIndex.value = idx
  showCurrent({ countView: false })
}

function goBack() {
  if (mode.value) {
    mode.value = null
    loadQueue()
  } else {
    router.push('/')
  }
}

onMounted(async () => {
  loadQueue()
  const decks = [...new Set(queue.value.map(c => c.deck))]
  await Promise.all(decks.map(async d => { poolCache[d] = await loadDeck(d) }))
  loading.value = false
})
</script>

<style scoped>
.deck-actions {
  gap: 0.75rem;
}
.hide-btn {
  pointer-events: auto;
  padding: 0.6em 1.2em;
  font-size: 0.9rem;
  border-radius: 0.5em;
  border: 1px solid var(--card-border);
  background: var(--card-bg);
  color: var(--gray);
  cursor: pointer;
}
.hide-btn:hover {
  color: var(--fg);
}
.undo-toast {
  position: fixed;
  bottom: 5rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.9rem;
  border-radius: 0.5rem;
  border: 1px solid var(--card-border);
  background: var(--card-bg);
  box-shadow: var(--card-shadow);
  color: var(--fg);
  font-size: 0.85rem;
  white-space: nowrap;
}
.undo-btn {
  border: none;
  background: none;
  color: var(--primary);
  font-weight: bold;
  cursor: pointer;
  padding: 0;
}
</style>
