<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
const s = ref({})
const msg = ref('')
const load = async () => { s.value = await getJSON('/api/settings') }
onMounted(load)
const save = async () => {
  msg.value = ''
  try {
    const body = {}
    for (const k of ['coverage', 'coats', 'waste_pct', 'waste_max_pct'])
      if (s.value[k] !== undefined && s.value[k] !== '') body[k] = Number(s.value[k])
    s.value = await putJSON('/api/settings', body)
    msg.value = '已保存'
  } catch (e) { msg.value = e.message }
}
</script>
<template><div class="page"><h1>设置</h1>
<table>
  <tr><td>遮盖力 (m²/L)</td><td><input v-model="s.coverage" type="number" min="0.1" step="0.1" /></td></tr>
  <tr><td>默认遍数</td><td><input v-model="s.coats" type="number" min="1" /></td></tr>
  <tr><td>默认损耗（百分点）</td><td><input v-model="s.waste_pct" type="number" min="0" /></td></tr>
  <tr><td>损耗上限（百分点）</td><td><input v-model="s.waste_max_pct" type="number" min="0" /></td></tr>
</table>
<button @click="save">保存</button>
<p class="err" v-if="msg">{{ msg }}</p>
</div></template>
