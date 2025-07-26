import { createRouter, createWebHistory, createWebHashHistory  } from 'vue-router'
import Home from '../views/Home.vue'
import Deck from '../views/Deck.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/deck/:deckId', component: Deck },
]

const router = createRouter({
  history: createWebHashHistory('/DE-Vokabeln/'),
  routes,
  scrollBehavior() {
    return { top: 0 };
  }
})

export default router
