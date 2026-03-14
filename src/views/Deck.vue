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
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import VocabCard from '../components/VocabCard.vue'
import { deckNameMap } from '../constants'

const route  = useRoute()
const router = useRouter()

const deckId   = route.params.deckId
const deckName = deckNameMap[deckId] || deckId

const allData      = ref([])
const currentCards = ref([])

function showRandomCard() {
  if (!allData.value.length) return
  const idx = Math.floor(Math.random() * allData.value.length)
  currentCards.value = [allData.value[idx]]
}

function goHome() {
  router.push('/')
}

onMounted(async () => {
  const res = await fetch(`${import.meta.env.BASE_URL}data/${deckId}.json`)
  allData.value = await res.json()
  showRandomCard()
})
</script>
