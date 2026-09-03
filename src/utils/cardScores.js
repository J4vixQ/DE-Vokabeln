import { getCardKey } from './wrongCards'

const KEY = 'cardScores'
const MAX = 5

// { "verben_base|gehen": 4.34, ... }  —— 每卡熟悉度 0..5
function load() {
  try { return JSON.parse(localStorage.getItem(KEY) || '{}') }
  catch { return {} }
}

function save(obj) {
  localStorage.setItem(KEY, JSON.stringify(obj))
}

export function getLevel(deck, data) {
  return load()[getCardKey(deck, data)] || 0
}

function setLevel(deck, data, level) {
  const obj = load()
  const clamped = Math.max(0, Math.min(MAX, level))
  obj[getCardKey(deck, data)] = Math.round(clamped * 100) / 100
  save(obj)
}

// quiz 答题：对 +1，错 -2
export function recordResult(deck, data, isCorrect) {
  const cur = getLevel(deck, data)
  setLevel(deck, data, isCorrect ? cur + 1 : cur - 2)
}

// non-quiz 看一次：弱证据，约三次顶一次答对
export function recordCardView(deck, data) {
  setLevel(deck, data, getLevel(deck, data) + 0.34)
}

// 按熟悉度加权随机：level 越低越容易被抽到（weight = 1/(level+1)）
export function pickWeightedIndex(cards, deck) {
  if (!cards.length) return -1
  const scores = load()
  const weights = cards.map(c => 1 / ((scores[getCardKey(deck, c)] || 0) + 1))
  const total = weights.reduce((a, b) => a + b, 0)
  let r = Math.random() * total
  for (let i = 0; i < weights.length; i++) {
    r -= weights[i]
    if (r < 0) return i
  }
  return weights.length - 1
}
