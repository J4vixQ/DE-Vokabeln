<template>
  <div class="deck-container">
    <div class="back-actions">
      <button class="back-btn" @click="goHome">◁ Back</button>
    </div>
    <h1 class="deck-title">{{ quizMode ? 'Quiz' : 'Ansehen' }}</h1>
    <div class="deck-list">
      <VocabCard
        v-if="current"
        :key="cardKey"
        :data="current.data"
        :deck="current.deck"
        :quizMode="quizMode"
        :choices="quizMode ? currentChoices : null"
        @answer="handleAnswer"
      />
    </div>
    <div class="deck-actions">
      <button
        class="next-btn"
        :disabled="quizMode && !currentAnswered"
        @click="showRandomCard"
      >▷ Next</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import VocabCard from '../components/VocabCard.vue'
import { deckGroups } from '../constants'
import { loadDeck } from '../utils/decks'
import { generateChoices, addWrongCard, removeWrongCard, getCardKey } from '../utils/wrongCards'
import { hiddenKeySet } from '../utils/hiddenCards'
import { recordAnswer, recordView } from '../utils/stats'
import { pickWeightedIndex, recordResult, recordCardView } from '../utils/cardScores'

const route  = useRoute()
const router = useRouter()

const quizMode = route.params.mode === 'quiz'

const current         = ref(null)   // { deck, data }
const currentChoices  = ref([])
const currentAnswered = ref(false)
const cardKey         = ref(0)

const pools = {}   // deck → 全部卡片（含隐藏的），用于生成干扰项
let groups  = []   // 每组可抽的 { deck, data }（已去掉隐藏的）

function showRandomCard() {
  if (!groups.length) return
  const group = groups[Math.floor(Math.random() * groups.length)]
  const card  = group[pickWeightedIndex(group)]
  current.value = card
  currentAnswered.value = false
  cardKey.value++
  if (quizMode) {
    currentChoices.value = generateChoices(card.data, pools[card.deck], card.deck)
  } else {
    recordView()
    recordCardView(card.deck, card.data)
  }
}

function handleAnswer(isCorrect) {
  const { deck, data } = current.value
  currentAnswered.value = true
  recordAnswer(isCorrect)
  recordResult(deck, data, isCorrect)
  if (!isCorrect) {
    addWrongCard(deck, data)
  } else {
    removeWrongCard(deck, data)
  }
}

function goHome() {
  router.push('/')
}

onMounted(async () => {
  const decks = deckGroups.flat()
  const lists = await Promise.all(decks.map(loadDeck))
  decks.forEach((d, i) => { pools[d] = lists[i] })

  const hidden = hiddenKeySet()
  groups = deckGroups
    .map(g => g
      .flatMap(deck => pools[deck].map(data => ({ deck, data })))
      .filter(c => !hidden.has(getCardKey(c.deck, c.data))))
    .filter(g => g.length)
  showRandomCard()
})
</script>
