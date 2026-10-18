// deckId → 对应的 json 文件；phrasen 由两个文件合并
const FILES = { phrasen: ['verben_phrasen', 'adv_phrasen'] }

const cache = {}

export function loadDeck(deck) {
  if (!cache[deck]) {
    const files = FILES[deck] || [deck]
    cache[deck] = Promise.all(
      files.map(f => fetch(`${import.meta.env.BASE_URL}data/${f}.json`).then(r => r.json()))
    ).then(parts => parts.flat())
  }
  return cache[deck]
}
