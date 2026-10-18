<template>
  <div class="deck-container">
    <div class="back-actions">
      <button class="back-btn" @click="goHome">◁ Back</button>
    </div>
    <h1 class="deck-title">Daten</h1>

    <p class="data-note">Alle Daten liegen nur in diesem Browser (pro Gerät, nichts synchronisiert).</p>

    <div class="data-row" v-for="row in rows" :key="row.key">
      <div class="data-info">
        <span class="data-label">{{ row.label }}</span>
        <span class="data-count">{{ counts[row.key] }}</span>
      </div>
      <button class="data-btn" @click="clearOne(row)">{{ row.action }}</button>
    </div>

    <button class="data-btn data-btn-all" @click="clearAll">Alles löschen</button>

    <template v-if="hidden.length">
      <h2 class="data-subtitle">Ausgeblendet</h2>
      <div class="data-row" v-for="h in hidden" :key="h.key">
        <div class="data-info">
          <span class="data-label">{{ h.word }}</span>
          <span class="data-count">{{ h.deckName }}</span>
        </div>
        <button class="data-btn" @click="restore(h.key)">Einblenden</button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { loadStats, clearStats } from '../utils/stats'
import { loadWrongCards, clearWrongCards } from '../utils/wrongCards'
import { scoredCount, resetScores } from '../utils/cardScores'
import { loadHidden, unhideKey, clearHidden } from '../utils/hiddenCards'
import { deckNameMap } from '../constants'

const router = useRouter()

const rows = [
  {
    key: 'cardScores',
    label: 'Familiarität (Gewichtung)',
    action: 'Zurücksetzen',
    confirm: 'Familiaritäts-Gewichtung zurücksetzen?',
    read: () => `${scoredCount()} Karten`,
    clear: resetScores,
  },
  {
    key: 'wrongCards',
    label: 'Falsch-Liste (Review)',
    action: 'Leeren',
    confirm: 'Falsch-Liste leeren?',
    read: () => `${loadWrongCards().length} Karten`,
    clear: clearWrongCards,
  },
  {
    key: 'dailyStats',
    label: 'Tagesstatistik',
    action: 'Leeren',
    confirm: 'Tagesstatistik löschen?',
    read: () => `${loadStats().length} Tage`,
    clear: clearStats,
  },
  {
    key: 'hiddenCards',
    label: 'Ausgeblendete Karten',
    action: 'Alle einblenden',
    confirm: 'Alle ausgeblendeten Karten wieder einblenden?',
    read: () => `${loadHidden().length} Karten`,
    clear: clearHidden,
  },
]

const counts = reactive({})
const hidden = ref([])
function refresh() {
  rows.forEach(r => { counts[r.key] = r.read() })
  hidden.value = loadHidden().map(key => {
    const i = key.indexOf('|')
    const deck = key.slice(0, i)
    return { key, word: key.slice(i + 1), deckName: deckNameMap[deck] || deck }
  })
}
refresh()

function clearOne(row) {
  if (!window.confirm(row.confirm)) return
  row.clear()
  refresh()
}

function restore(key) {
  unhideKey(key)
  refresh()
}

function clearAll() {
  if (!window.confirm('Familiarität, Falsch-Liste, Tagesstatistik und ausgeblendete Karten löschen?')) return
  rows.forEach(r => r.clear())
  localStorage.removeItem('quizMode')
  refresh()
}

function goHome() { router.push('/') }
</script>

<style scoped>
.data-note {
  font-size: 0.8rem;
  color: var(--gray);
  text-align: center;
  margin-bottom: 1.5rem;
}
.data-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--card-border);
}
.data-info {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}
.data-label {
  font-size: 0.95rem;
  color: var(--fg);
}
.data-count {
  font-size: 0.8rem;
  color: var(--gray);
}
.data-subtitle {
  font-size: 1.1rem;
  font-weight: bold;
  color: var(--fg);
  margin: 2rem 0 0.5rem;
}
.data-btn {
  flex-shrink: 0;
  padding: 0.4rem 0.9rem;
  font-size: 0.8rem;
  border: 1px solid var(--card-border);
  border-radius: 6px;
  background: var(--button-bg);
  color: var(--button-fg);
  cursor: pointer;
}
.data-btn:hover {
  background: var(--button-hover);
  color: #fff;
}
.data-btn-all {
  display: block;
  width: 100%;
  margin-top: 1.5rem;
  padding: 0.6rem;
  border-color: #ef444455;
  color: #ef4444;
  background: transparent;
}
.data-btn-all:hover {
  background: #ef444422;
  color: #ef4444;
}
</style>
