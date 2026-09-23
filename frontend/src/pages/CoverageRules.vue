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
    s.value = await putJSON('/api/settings', {
      coverage: Number(s.value.coverage), coats: Number(s.value.coats),
      waste_pct: Number(s.value.waste_pct), waste_max_pct: Number(s.value.waste_max_pct),
    })
    msg.value = '已保存'
  } catch (e) { msg.value = e.message }
}
</script>
<template><div class="page"><h1>遮盖力参数</h1>
<label>每升可刷 <input v-model="s.coverage" type="number" min="0.1" step="0.1" /> m²</label><br/>
<label>默认 <input v-model="s.coats" type="number" min="1" /> 遍</label><br/>
<label>默认损耗 <input v-model="s.waste_pct" type="number" min="0" /> 百分点</label><br/>
<label>损耗上限 <input v-model="s.waste_max_pct" type="number" min="0" /> 百分点</label><br/>
<button @click="save">保存</button>
<p class="err" v-if="msg">{{ msg }}</p>
</div></template>
