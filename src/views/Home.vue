<template>
  <div class="categories-container">
    <div class="categories-list">
      <h1 class="categories-list-title">Vokabeln</h1>
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
import { deckNameMap } from '../constants'

const categories = Object.entries(deckNameMap).map(([id, label]) => ({ id, label }))
</script>
