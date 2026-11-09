// deckId → public/data/<deckId>.json，按 deck 缓存
const cache = {}

export function loadDeck(deck) {
  if (!cache[deck]) {
    cache[deck] = fetch(`${import.meta.env.BASE_URL}data/${deck}.json`).then(r => r.json())
  }
  return cache[deck]
}
