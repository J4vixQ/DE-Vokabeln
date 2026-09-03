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
          v-for="z in zoomKeys"
          :key="z"
          class="zoom-btn"
          :class="{ active: zoom === z }"
          @click="setZoom(z)"
        >{{ z }}</button>
      </div>

      <div
        ref="scroller"
        class="stats-chart-scroll"
        :class="{ draggable, grabbing: dragging }"
        @pointerdown="onPointerDown"
        @pointermove="onPointerMove"
        @pointerup="onPointerUp"
        @pointerleave="onPointerUp"
      >
        <svg :width="svgWidth" :height="svgHeight">
          <g v-for="(entry, i) in visibleSeries" :key="entry.date">
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
      <p v-if="draggable" class="stats-hint">← ziehen zum Verschieben</p>
    </template>

    <div v-else class="review-status">No data yet</div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { dailySeries } from '../utils/stats'

const router = useRouter()

const chartH = 160
const labelH = 44
const svgHeight = chartH + labelH

// 每个视图渲染多少天（Alle = 全部历史）
const WINDOWS = { '1W': 7, '1M': 30, 'Alle': Infinity }
const zoomKeys = Object.keys(WINDOWS)

const series = dailySeries()

const todayStr = new Date().toISOString().slice(0, 10)
const todayEntry = series.find(e => e.date === todayStr) || { correct: 0, wrong: 0, view: 0 }

const zoom = ref('1W')

// 容器宽度（响应式）→ 决定 bar 宽度
const scroller = ref(null)
const wrapW = ref(320)
let ro = null

const visibleSeries = computed(() => {
  const n = WINDOWS[zoom.value]
  return n === Infinity ? series : series.slice(-n)
})

// 1M 和 Alle 用同一个 bar 宽度（按 30 天铺满容器）；1W 按 7 天铺满
const barStep = computed(() => {
  const perView = zoom.value === '1W' ? 7 : 30
  return wrapW.value / perView
})
const gap = computed(() => Math.max(1, Math.round(barStep.value * 0.28)))
const barW = computed(() => Math.max(1, barStep.value - gap.value))
const labelEvery = computed(() => Math.max(1, Math.round(52 / barStep.value)))

// 只有 Alle 会超出容器 → 可拖动
const draggable = computed(() => zoom.value === 'Alle' && series.length > 30)
const svgWidth = computed(() =>
  draggable.value ? visibleSeries.value.length * barStep.value : wrapW.value,
)

const maxTotal = computed(() => Math.max(
  ...visibleSeries.value.map(e => e.correct + e.wrong + e.view),
  1,
))

function barX(i) { return i * barStep.value + gap.value / 2 }
function h(v) { return (v / maxTotal.value) * chartH }

function tooltip(e) {
  return `${e.date}  ✓${e.correct} ✗${e.wrong} 👁${e.view}`
}
function formatDate(d) {
  return d.slice(5).replace('-', '/')
}

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

onMounted(() => {
  const el = scroller.value
  if (el) {
    wrapW.value = el.clientWidth
    ro = new ResizeObserver(() => { wrapW.value = el.clientWidth })
    ro.observe(el)
  }
  scrollToToday()
})
onBeforeUnmount(() => ro && ro.disconnect())

// ── 拖动（仅 Alle，仅鼠标；触屏用原生横向滚动）──
const dragging = ref(false)
let startX = 0
let startScroll = 0

function onPointerDown(e) {
  if (!draggable.value || e.pointerType !== 'mouse') return
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
  overflow-x: hidden;
  padding-bottom: 0.5rem;
}
.stats-chart-scroll.draggable {
  overflow-x: auto;
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
