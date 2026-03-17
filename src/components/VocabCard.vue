<template>
  <div class="vocab-card" :class="{ 'quiz-mode': quizMode }" @click="reveal">

    <!-- 非人物类标题 -->
    <h2 v-if="deck !== 'nomen_people'" class="vocab-card-title">
      <template v-if="deck === 'nomen_obj'">
        <span class="article" :class="nomenObjUnderlineClass">
          {{ article }} <span class="noun">{{ noun }}</span>
        </span>
      </template>
      <template v-else>
        {{ rawWord }}
      </template>
    </h2>

    <!-- 人物名词 -->
    <template v-if="deck === 'nomen_people' && (hasMale || hasFemale)">
      <div class="gender-blocks">
        <div v-if="hasMale" class="person-block male">
          <div>
            <span class="article">{{ getArticle(data['单数男']) }}</span>
            <span class="noun">{{ getNoun(data['单数男']) }}</span>
          </div>
          <div class="plural">{{ data['复数男'] }}</div>
          <div v-show="!quizMode || revealed" class="meaning">{{ data['意思男'] }}</div>
        </div>
        <div v-if="hasFemale" class="person-block female">
          <div>
            <span class="article">{{ getArticle(data['单数女']) }}</span>
            <span class="noun">{{ getNoun(data['单数女']) }}</span>
          </div>
          <div class="plural">{{ data['复数女'] }}</div>
          <div v-show="!quizMode || revealed" class="meaning">{{ data['意思女'] }}</div>
        </div>
        <p v-if="data['例句']" class="vocab-card-sentence">{{ data['例句'] }}</p>
        <p v-show="(!quizMode || revealed) && data['翻译']" class="vocab-card-translation">{{ data['翻译'] }}</p>
      </div>
    </template>

    <!-- 名词 -->
    <template v-else-if="deck === 'nomen_obj'">
      <p v-if="data.复数" class="vocab-card-plural">{{ data.复数 }}</p>
      <p v-show="!quizMode || revealed" class="vocab-card-meaning">= {{ data.意思 }}</p>
      <p v-if="data['例句']" class="vocab-card-sentence">{{ data['例句'] }}</p>
      <p v-show="(!quizMode || revealed) && data['翻译']" class="vocab-card-translation">{{ data['翻译'] }}</p>
    </template>

    <!-- 动词原型 -->
    <template v-else-if="deck === 'verben_base'">
      <p class="vocab-card-meaning">{{ data['现在'] }}</p>
      <p class="vocab-card-meaning">{{ data['过去'] }}</p>
      <p class="vocab-card-meaning">{{ data['完成'] }}</p>
      <p v-show="!quizMode || revealed" class="vocab-card-meaning">= {{ data['意思'] }}</p>
      <p v-if="data['例句']" class="vocab-card-sentence">{{ data['例句'] }}</p>
      <p v-show="(!quizMode || revealed) && data['翻译']" class="vocab-card-translation">{{ data['翻译'] }}</p>
    </template>

    <!-- 短语（动词短语 + 副词短语合并） -->
    <template v-else-if="deck === 'phrasen'">
      <p v-show="!quizMode || revealed" class="vocab-card-meaning">= {{ data['意思'] }}</p>
      <p v-if="data['例句']" class="vocab-card-sentence">{{ data['例句'] }}</p>
      <p v-show="(!quizMode || revealed) && data['翻译']" class="vocab-card-translation">{{ data['翻译'] }}</p>
    </template>

    <!-- 形容词比较级 -->
    <template v-else-if="deck === 'adj_adv'">
      <p class="vocab-card-meaning">{{ data['比较级'] }}</p>
      <p class="vocab-card-meaning">{{ data['最高级'] }}</p>
      <p v-show="!quizMode || revealed" class="vocab-card-meaning">= {{ data['意思'] }}</p>
      <p v-if="data['例句']" class="vocab-card-sentence">{{ data['例句'] }}</p>
      <p v-show="(!quizMode || revealed) && data['翻译']" class="vocab-card-translation">{{ data['翻译'] }}</p>
    </template>

    <!-- quiz mode 提示 -->
    <p v-if="quizMode && !revealed" class="quiz-hint">点击查看释义</p>

  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  data:      Object,
  deck:      String,
  quizMode:  Boolean,
})

const revealed = ref(false)

watch(() => props.data, () => { revealed.value = false })

function reveal() {
  if (props.quizMode) revealed.value = true
}

const hasMale   = computed(() => !!(props.data['单数男'] || props.data['意思男']))
const hasFemale = computed(() => !!(props.data['单数女'] || props.data['意思女']))

function getArticle(word = '') {
  return word.split(' ')[0] || ''
}
function getNoun(word = '') {
  return word.split(' ').slice(1).join(' ') || ''
}

const rawWord = computed(() =>
  props.data['单数'] || props.data['原型'] || props.data['词组'] || ''
)

const article = computed(() => rawWord.value.split(' ')[0] || '')
const noun    = computed(() => rawWord.value.split(' ').slice(1).join(' ') || '')

const nomenObjUnderlineClass = computed(() => {
  switch (article.value) {
    case 'der': return 'border-blue'
    case 'die': return 'border-pink'
    case 'das': return 'border-gray'
    default:    return ''
  }
})
</script>
