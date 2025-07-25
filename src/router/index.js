import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Deck from '../views/Deck.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/deck/:deckId', component: Deck },
]

const router = createRouter({
  history: createWebHistory('/DE-Vokabeln/'),
  routes,
})

export default router
