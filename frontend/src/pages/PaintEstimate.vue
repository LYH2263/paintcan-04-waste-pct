<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
const room_id = ref(1)
const waste_pct = ref(null)
const defaults = ref({})
const out = ref(null)
const err = ref('')
onMounted(async () => { defaults.value = await getJSON('/api/settings') })
const run = async () => {
  err.value = ''; out.value = null
  const body = { room_id: room_id.value, persist: true }
  if (waste_pct.value !== null && waste_pct.value !== '') body.waste_pct = Number(waste_pct.value)
  try {
    out.value = await postJSON('/api/estimate', body)
  } catch (e) { err.value = e.message }
}
</script>
<template><div class="page"><h1>估漆工作台</h1>
<label>房间ID <input v-model.number="room_id" /></label>
<label>损耗百分点 <input v-model="waste_pct" type="number" min="0" :max="defaults.waste_max_pct"
  :placeholder="`默认 ${defaults.waste_pct}（上限 ${defaults.waste_max_pct}）`" /></label>
<button @click="run">估算</button>
<p v-if="err" class="err">{{ err }}</p>
<div v-if="out">
  <p>净 {{ out.net_m2 }} m² · {{ out.coats }} 遍</p>
  <p>基础升数 {{ out.liters }} L · 损耗 {{ out.waste_pct }}% ·
     应付升数 <span class="hero-num">{{ out.chargeable_liters }} L</span></p>
</div></div></template>
