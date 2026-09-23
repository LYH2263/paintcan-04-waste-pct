<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
const s = ref({})
const wastePct = ref('0')
const wasteMax = ref('20')
const msg = ref('')
onMounted(async () => {
  s.value = await getJSON('/api/settings')
  wastePct.value = s.value.waste_pct ?? '0'
  wasteMax.value = s.value.waste_max_pct ?? '20'
})
const save = async () => {
  msg.value = ''
  try {
    s.value = await putJSON('/api/settings', { waste_pct: String(wastePct.value), waste_max_pct: String(wasteMax.value) })
    msg.value = '已保存'
  } catch (e) { msg.value = String(e) }
}
</script>
<template><div class="page"><h1>设置</h1>
<label>默认损耗% <input v-model="wastePct" /></label>
<label>损耗上限% <input v-model="wasteMax" /></label>
<button @click="save">保存</button>
<p v-if="msg">{{ msg }}</p>
<pre>{{ s }}</pre></div></template>
