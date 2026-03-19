<template>
  <div class="deck-container">
    <div class="back-actions">
      <button class="back-btn" @click="goHome">◁ Back</button>
    </div>
    <h1 class="deck-title">Stats</h1>

    <!-- Today summary -->
    <div class="stats-today">
      <span class="stats-today-num stats-correct">{{ todayEntry.correct }}</span>
      <span class="stats-today-num stats-wrong">{{ todayEntry.wrong }}</span>
    </div>
    <div class="stats-legend">
      <span><span class="legend-dot" style="background:#22c55e"></span> Richtig</span>
      <span><span class="legend-dot" style="background:#ef4444"></span> Falsch</span>
    </div>

    <!-- Chart -->
    <div class="stats-chart-scroll" v-if="history.length > 0">
      <svg :width="svgWidth" :height="svgHeight">
        <g v-for="(entry, i) in history" :key="entry.date">
          <!-- wrong (red) on top -->
          <rect
            v-if="entry.wrong > 0"
            :x="i * barStep"
            :y="chartH - barH(entry, 'both')"
            :width="barW"
            :height="barH(entry, 'wrong')"
            fill="#ef4444"
          />
          <!-- correct (green) at bottom -->
          <rect
            v-if="entry.correct > 0"
            :x="i * barStep"
            :y="chartH - barH(entry, 'correct')"
            :width="barW"
            :height="barH(entry, 'correct')"
            fill="#22c55e"
          />
          <!-- date label -->
          <text
            :x="i * barStep + barW / 2"
            :y="chartH + 14"
            text-anchor="end"
            font-size="10"
            fill="#9ca3af"
            :transform="`rotate(-45, ${i * barStep + barW / 2}, ${chartH + 14})`"
          >{{ formatDate(entry.date) }}</text>
        </g>
      </svg>
    </div>

    <div v-else class="review-status">No data yet</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { loadStats } from '../utils/stats'

const router = useRouter()

const barW = 24
const barStep = 32
const chartH = 160
const labelH = 44
const svgHeight = chartH + labelH

const allStats = loadStats()
const history = allStats.slice(-30)

const todayStr = new Date().toISOString().slice(0, 10)
const todayEntry = history.find(e => e.date === todayStr) || { correct: 0, wrong: 0 }

const maxTotal = Math.max(...history.map(e => (e.correct || 0) + (e.wrong || 0)), 1)
const svgWidth = barStep * history.length || 100

function barH(entry, type) {
  if (type === 'correct') return ((entry.correct || 0) / maxTotal) * chartH
  if (type === 'wrong')   return ((entry.wrong   || 0) / maxTotal) * chartH
  if (type === 'both')    return ((entry.correct + entry.wrong) / maxTotal) * chartH
  return 0
}

function formatDate(d) {
  return d.slice(5).replace('-', '/')
}

function goHome() { router.push('/') }
</script>

<style scoped>
.stats-today {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 0.5rem;
}
.stats-today-num {
  font-size: 2rem;
  font-weight: bold;
}
.stats-correct { color: #22c55e; }
.stats-wrong   { color: #ef4444; }

.stats-legend {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  font-size: 0.85rem;
  color: var(--gray);
  margin-bottom: 1.5rem;
}
.legend-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 2px;
  margin-right: 4px;
  vertical-align: middle;
}
.stats-chart-scroll {
  overflow-x: auto;
  padding-bottom: 0.5rem;
}
</style>
