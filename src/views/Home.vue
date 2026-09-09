<template>
  <div class="categories-container">
    <nav class="home-icons">
      <router-link to="/data" class="icon-btn" aria-label="Daten" title="Daten">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="3" />
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
        </svg>
      </router-link>
      <router-link to="/stats" class="icon-btn" aria-label="Stats" title="Stats">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <path d="M4 20V10M12 20V4M20 20v-6" />
        </svg>
      </router-link>
    </nav>
    <div class="categories-list">
      <h1 class="categories-list-title">Vokabeln</h1>
      <div class="quiz-toggle">
        <label class="toggle-label">
          <input type="checkbox" v-model="quizMode" @change="saveQuizMode" />
          <span class="toggle-text">Quiz-Modus</span>
        </label>
      </div>
      <router-link
        v-for="c in categories"
        :key="c.id"
        :to="`/deck/${c.id}`"
        class="card-link"
      >
        {{ c.label }}
      </router-link>
      <router-link v-if="wrongCount > 0" to="/review" class="card-link card-link-wrong">
        Review ({{ wrongCount }})
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { deckNameMap } from '../constants'
import { loadWrongCards } from '../utils/wrongCards'

const categories = Object.entries(deckNameMap).map(([id, label]) => ({ id, label }))
const quizMode   = ref(localStorage.getItem('quizMode') === 'true')
const wrongCount = ref(0)

function saveQuizMode() {
  localStorage.setItem('quizMode', quizMode.value)
}

onMounted(() => {
  wrongCount.value = loadWrongCards().length
})
</script>
