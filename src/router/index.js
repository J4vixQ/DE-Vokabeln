import { createRouter, createWebHistory, createWebHashHistory  } from 'vue-router'
import Home from '../views/Home.vue'
import Deck from '../views/Deck.vue'
import Review from '../views/Review.vue'
import Stats from '../views/Stats.vue'
import Data from '../views/Data.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/deck/:deckId', component: Deck },
  { path: '/review', component: Review },
  { path: '/stats', component: Stats },
  { path: '/data', component: Data },
]

const router = createRouter({
  history: createWebHashHistory('/DE-Vokabeln/'),
  routes,
  scrollBehavior() {
    return { top: 0 };
  }
})

export default router
