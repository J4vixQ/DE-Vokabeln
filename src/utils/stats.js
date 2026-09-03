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

function bump(field) {
  const list = loadStats()
  const date = today()
  let entry = list.find(e => e.date === date)
  if (!entry) {
    entry = { date, correct: 0, wrong: 0, view: 0 }
    list.push(entry)
  }
  entry[field] = (entry[field] || 0) + 1
  saveStats(list)
}

export function recordAnswer(isCorrect) {
  bump(isCorrect ? 'correct' : 'wrong')
}

// 非答题模式下每看一张卡记一次
export function recordView() {
  bump('view')
}

// 从最早有记录的那天到今天，逐日连续的序列；没有记录的日子补零。
// 只有有活动的日子才写进 localStorage，空白日在这里按需生成。
export function dailySeries() {
  const list = loadStats()
  if (!list.length) return []

  const byDate = {}
  let start = today()
  for (const e of list) {
    byDate[e.date] = e
    if (e.date < start) start = e.date
  }

  const out = []
  const cur = new Date(start + 'T00:00:00Z')
  const last = new Date(today() + 'T00:00:00Z')
  while (cur <= last) {
    const date = cur.toISOString().slice(0, 10)
    const e = byDate[date]
    out.push({
      date,
      correct: e?.correct || 0,
      wrong: e?.wrong || 0,
      view: e?.view || 0,
    })
    cur.setUTCDate(cur.getUTCDate() + 1)
  }
  return out
}
