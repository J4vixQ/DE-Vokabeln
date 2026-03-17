<template>
  <div class="categories-container">
    <div class="categories-list">
      <h1 class="categories-list-title">Vokabeln</h1>
      <div class="quiz-toggle">
        <label class="toggle-label">
          <input
            type="checkbox"
            v-model="quizMode"
            @change="saveQuizMode"
          />
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
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { deckNameMap } from '../constants'

const categories = Object.entries(deckNameMap).map(([id, label]) => ({ id, label }))

const quizMode = ref(localStorage.getItem('quizMode') === 'true')

function saveQuizMode() {
  localStorage.setItem('quizMode', quizMode.value)
}
</script>
