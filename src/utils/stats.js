const STATS_KEY = 'dailyStats'

function today() {
  return new Date().toISOString().slice(0, 10)
}

export function loadStats() {
  try { return JSON.parse(localStorage.getItem(STATS_KEY) || '[]') }
  catch { return [] }
}

function saveStats(list) {
  localStorage.setItem(STATS_KEY, JSON.stringify(list))
}

export function recordAnswer(isCorrect) {
  const list = loadStats()
  const date = today()
  let entry = list.find(e => e.date === date)
  if (!entry) {
    entry = { date, correct: 0, wrong: 0 }
    list.push(entry)
  }
  if (isCorrect) entry.correct++
  else entry.wrong++
  saveStats(list)
}
