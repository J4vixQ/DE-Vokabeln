<template>
  <div class="categories-container">
    <h1 class="categories-title"></h1>
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
import { useRouter } from 'vue-router';

const router = useRouter();
const categories = [
  { id: "nomen_obj", label: "Nomen - Objekte" },
  { id: "nomen_people", label: "Nomen - Personen" },
  { id: "verben_base", label: "Verben - Grundformen" },
  { id: "verben_phrasen", label: "Verben - Redewendungen" },
  { id: "adj_adv", label: "Adjektive und Adverbien" },
  { id: "adv_phrasen", label: "Adverb Phrasen" },
];
// const deckNameMap = {
//   nomen_obj: "Nomen - Objekte",
//   nomen_people: "Nomen - Personen",
//   verben_base: "Verben Grundformen",
//   verben_phrasen: "Verben Phrasen",
//   adj_adv: "Adjektive und Adverbien",
//   adv_phrasen: "Adverb Phrasen",
// };

function goToDeck(deckId) {
  router.push(`/deck/${deckId}`);
}
</script>
