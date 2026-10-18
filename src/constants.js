export const deckNameMap = {
  nomen_obj:    "Nomen - Objekte",
  nomen_people: "Nomen - Personen",
  verben_base:  "Verben",
  adj_adv:      "Adjektive",
  phrasen:      "Phrasen",
}

// 抽卡分组：先等概率选组，再在组内按熟悉度加权
export const deckGroups = [
  ['nomen_obj', 'nomen_people'],
  ['verben_base'],
  ['adj_adv'],
  ['phrasen'],
]
