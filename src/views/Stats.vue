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
      <span class="stats-today-num stats-view">{{ todayEntry.view }}</span>
    </div>
    <div class="stats-legend">
      <span><span class="legend-dot" style="background:#22c55e"></span> Richtig</span>
      <span><span class="legend-dot" style="background:#ef4444"></span> Falsch</span>
      <span><span class="legend-dot" style="background:#9ca3af"></span> Angesehen</span>
    </div>

    <template v-if="series.length > 0">
      <div class="stats-zoom">
        <button
          v-for="z in zoomLevels"
          :key="z.key"
          class="zoom-btn"
          :class="{ active: zoom === z.key }"
          @click="setZoom(z.key)"
        >{{ z.key }}</button>
      </div>

      <div
        ref="scroller"
        class="stats-chart-scroll"
        :class="{ grabbing: dragging }"
        @pointerdown="onPointerDown"
        @pointermove="onPointerMove"
        @pointerup="onPointerUp"
        @pointerleave="onPointerUp"
      >
        <svg :width="svgWidth" :height="svgHeight">
          <g v-for="(entry, i) in series" :key="entry.date">
            <title>{{ tooltip(entry) }}</title>
            <rect
              v-if="entry.correct > 0"
              :x="barX(i)" :width="barW"
              :y="chartH - h(entry.correct)" :height="h(entry.correct)"
              fill="#22c55e"
            />
            <rect
              v-if="entry.wrong > 0"
              :x="barX(i)" :width="barW"
              :y="chartH - h(entry.correct) - h(entry.wrong)" :height="h(entry.wrong)"
              fill="#ef4444"
            />
            <rect
              v-if="entry.view > 0"
              :x="barX(i)" :width="barW"
              :y="chartH - h(entry.correct) - h(entry.wrong) - h(entry.view)" :height="h(entry.view)"
              fill="#9ca3af"
            />
            <text
              v-if="i % labelEvery === 0"
              :x="barX(i) + barW / 2"
              :y="chartH + 14"
              text-anchor="end"
              font-size="10"
              fill="#9ca3af"
              :transform="`rotate(-45, ${barX(i) + barW / 2}, ${chartH + 14})`"
            >{{ formatDate(entry.date) }}</text>
          </g>
        </svg>
      </div>
      <p class="stats-hint">← ziehen zum Verschieben</p>
    </template>

    <div v-else class="review-status">No data yet</div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { dailySeries } from '../utils/stats'

const router = useRouter()

const chartH = 160
const labelH = 44
const svgHeight = chartH + labelH

const zoomLevels = [
  { key: '2W', step: 32 },
  { key: '1M', step: 18 },
  { key: '3M', step: 9 },
  { key: 'Alle', step: 4 },
]

const series = dailySeries()

const todayStr = new Date().toISOString().slice(0, 10)
const todayEntry = series.find(e => e.date === todayStr) || { correct: 0, wrong: 0, view: 0 }

const maxTotal = Math.max(
  ...series.map(e => e.correct + e.wrong + e.view),
  1,
)

function pickDefaultZoom(len) {
  if (len <= 18) return '2W'
  if (len <= 40) return '1M'
  if (len <= 110) return '3M'
  return 'Alle'
}
const zoom = ref(pickDefaultZoom(series.length))

const barStep = computed(() => zoomLevels.find(z => z.key === zoom.value).step)
const gap = computed(() => Math.max(2, Math.round(barStep.value * 0.28)))
const barW = computed(() => Math.max(1, barStep.value - gap.value))
const labelEvery = computed(() => Math.max(1, Math.round(56 / barStep.value)))
const svgWidth = computed(() => Math.max(series.length * barStep.value + gap.value, 100))

function barX(i) { return i * barStep.value + gap.value / 2 }
function h(v) { return (v / maxTotal) * chartH }

function tooltip(e) {
  return `${e.date}  ✓${e.correct} ✗${e.wrong} 👁${e.view}`
}
function formatDate(d) {
  return d.slice(5).replace('-', '/')
}

// ── 缩放 / 拖动 ──────────────────────────────
const scroller = ref(null)

function scrollToToday() {
  nextTick(() => {
    const el = scroller.value
    if (el) el.scrollLeft = el.scrollWidth
  })
}

function setZoom(key) {
  zoom.value = key
}
watch(zoom, scrollToToday)
onMounted(scrollToToday)

const dragging = ref(false)
let startX = 0
let startScroll = 0

function onPointerDown(e) {
  if (e.pointerType !== 'mouse') return  // 触屏用原生横向滚动
  dragging.value = true
  startX = e.clientX
  startScroll = scroller.value.scrollLeft
}
function onPointerMove(e) {
  if (!dragging.value) return
  scroller.value.scrollLeft = startScroll - (e.clientX - startX)
}
function onPointerUp() {
  dragging.value = false
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
.stats-view    { color: #9ca3af; }

.stats-legend {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  font-size: 0.85rem;
  color: var(--gray);
  margin-bottom: 1rem;
}
.legend-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 2px;
  margin-right: 4px;
  vertical-align: middle;
}

.stats-zoom {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}
.zoom-btn {
  padding: 0.25rem 0.7rem;
  font-size: 0.8rem;
  border: 1px solid var(--card-border);
  border-radius: 6px;
  background: var(--button-bg);
  color: var(--button-fg);
  cursor: pointer;
}
.zoom-btn.active {
  background: var(--primary);
  color: #fff;
  border-color: var(--primary);
}

.stats-chart-scroll {
  overflow-x: auto;
  padding-bottom: 0.5rem;
  cursor: grab;
  touch-action: pan-x;
}
.stats-chart-scroll.grabbing {
  cursor: grabbing;
}
.stats-chart-scroll svg text {
  user-select: none;
}
.stats-hint {
  text-align: center;
  font-size: 0.75rem;
  color: var(--gray);
  margin-top: 0.25rem;
}
</style>
