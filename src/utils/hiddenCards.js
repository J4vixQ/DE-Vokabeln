import { getCardKey } from './wrongCards'

const KEY = 'hiddenCards'

// ["verben_base|gehen", ...] —— 不再抽到的卡
export function loadHidden() {
  try { return JSON.parse(localStorage.getItem(KEY) || '[]') }
  catch { return [] }
}

function save(list) {
  localStorage.setItem(KEY, JSON.stringify(list))
}

export function hiddenKeySet() {
  return new Set(loadHidden())
}

export function hideCard(deck, data) {
  const list = loadHidden()
  const key = getCardKey(deck, data)
  if (!list.includes(key)) {
    list.push(key)
    save(list)
  }
}

export function unhideKey(key) {
  save(loadHidden().filter(k => k !== key))
}

export function clearHidden() {
  localStorage.removeItem(KEY)
}
