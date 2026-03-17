export function getMeaning(item, deck) {
  if (deck === 'nomen_people') {
    return [item['意思男'], item['意思女']].filter(Boolean).join(' / ')
  }
  return item['意思'] || ''
}

export function getCardKey(deck, data) {
  const word = data['单数'] || data['原型'] || data['词组'] || data['单数男'] || data['复数男'] || ''
  return `${deck}|${word}`
}

export function generateChoices(currentItem, pool, deck) {
  const correct = getMeaning(currentItem, deck)
  const wrongs = [...new Set(
    pool
      .map(item => getMeaning(item, deck))
      .filter(m => m && m !== correct)
  )].sort(() => Math.random() - 0.5).slice(0, 3)

  return [...wrongs, correct]
    .sort(() => Math.random() - 0.5)
    .map(text => ({ text, correct: text === correct }))
}

export function loadWrongCards() {
  try { return JSON.parse(localStorage.getItem('wrongCards') || '[]') }
  catch { return [] }
}

function saveWrongCards(list) {
  localStorage.setItem('wrongCards', JSON.stringify(list))
}

export function addWrongCard(deck, data) {
  const list = loadWrongCards()
  const key = getCardKey(deck, data)
  if (!list.find(c => getCardKey(c.deck, c.data) === key)) {
    list.push({ deck, data })
    saveWrongCards(list)
  }
}

export function removeWrongCard(deck, data) {
  const list = loadWrongCards()
  const key = getCardKey(deck, data)
  saveWrongCards(list.filter(c => getCardKey(c.deck, c.data) !== key))
}

